import streamlit as st
import requests

# =========================
# CONFIG
# =========================
API_BASE = "http://127.0.0.1:8000"  # FastAPI base URL

st.set_page_config(page_title="E-commerce Dashboard", page_icon="🛒", layout="wide")
st.title("🛒 E-commerce Products Dashboard (Streamlit + FastAPI)")

# =========================
# HELPERS
# =========================
def api_get_products(name=None, sort_by_price=False, order="asc", limit=50, offset=0):
    params = {"limit": limit, "offset": offset, "sort_by_price": sort_by_price, "order": order}
    if name:
        params["name"] = name
    r = requests.get(f"{API_BASE}/products", params=params, timeout=10)
    return r

def api_create_product(payload: dict):
    r = requests.post(f"{API_BASE}/products", json=payload, timeout=10)
    return r

def api_delete_product(product_id: str):
    r = requests.delete(f"{API_BASE}/products/{product_id}", timeout=10)
    return r

def api_update_product(product_id: str, payload: dict):
    r = requests.put(f"{API_BASE}/products/{product_id}", json=payload, timeout=10)
    return r

# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.header("🔎 Search & Filters")

search_name = st.sidebar.text_input("Search by name", placeholder="e.g., Energy")
sort_by_price = st.sidebar.checkbox("Sort by price", value=False)
order = st.sidebar.selectbox("Order", ["asc", "desc"], index=0)
limit = st.sidebar.slider("Limit", 1, 100, 20)
offset = st.sidebar.number_input("Offset", min_value=0, value=0, step=1)

refresh = st.sidebar.button("🔄 Refresh Products")

# =========================
# LOAD PRODUCTS
# =========================
if refresh:
    st.rerun()

st.subheader("📦 Products List")

try:
    res = api_get_products(
        name=search_name if search_name.strip() else None,
        sort_by_price=sort_by_price,
        order=order,
        limit=limit,
        offset=offset,
    )

    if res.status_code == 200:
        data = res.json()
        st.caption(f"Total: {data.get('total', 0)} | Showing: {len(data.get('items', []))}")
        items = data.get("items", [])

        if items:
            st.dataframe(items, use_container_width=True)
        else:
            st.info("No products found.")
    else:
        st.error(f"Error fetching products ({res.status_code}): {res.text}")

except Exception as e:
    st.error(f"FastAPI not reachable. Is it running? Error: {e}")

st.divider()

# =========================
# ADD PRODUCT
# =========================
st.subheader("➕ Add New Product")

with st.form("add_product_form", clear_on_submit=True):
    name = st.text_input("Product Name")
    description = st.text_area("Description")
    price = st.number_input("Price", min_value=0.0, value=0.0, step=0.5)
    quantity = st.number_input("Quantity", min_value=0, value=1, step=1)

    submitted = st.form_submit_button("Create Product")

    if submitted:
        payload = {
            "name": name,
            "description": description,
            "price": price,
            "quantity": quantity,
        }

        try:
            r = api_create_product(payload)
            if r.status_code in (200, 201):
                st.success("✅ Product created successfully!")
                st.rerun()
            else:
                st.error(f"❌ Create failed ({r.status_code}): {r.text}")
        except Exception as e:
            st.error(f"Create request failed: {e}")

st.divider()

# =========================
# UPDATE / DELETE
# =========================
st.subheader("✏️ Update / 🗑️ Delete Product")

product_id = st.text_input("Enter Product ID (UUID) to Update/Delete", placeholder="paste product id here")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### ✏️ Update")
    upd_name = st.text_input("New Name (optional)")
    upd_description = st.text_area("New Description (optional)")
    upd_price = st.text_input("New Price (optional) e.g. 19.99")
    upd_quantity = st.text_input("New Quantity (optional) e.g. 10")

    if st.button("Update Product"):
        if not product_id.strip():
            st.warning("Please enter product_id.")
        else:
            payload = {}
            if upd_name.strip():
                payload["name"] = upd_name.strip()
            if upd_description.strip():
                payload["description"] = upd_description.strip()
            if upd_price.strip():
                try:
                    payload["price"] = float(upd_price.strip())
                except:
                    st.error("Price must be a number.")
            if upd_quantity.strip():
                try:
                    payload["quantity"] = int(upd_quantity.strip())
                except:
                    st.error("Quantity must be an integer.")

            if not payload:
                st.warning("Enter at least one field to update.")
            else:
                try:
                    r = api_update_product(product_id.strip(), payload)
                    if r.status_code == 200:
                        st.success("✅ Updated successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Update failed ({r.status_code}): {r.text}")
                except Exception as e:
                    st.error(f"Update request failed: {e}")

with col2:
    st.markdown("### 🗑️ Delete")
    if st.button("Delete Product"):
        if not product_id.strip():
            st.warning("Please enter product_id.")
        else:
            try:
                r = api_delete_product(product_id.strip())
                if r.status_code == 200:
                    st.success("✅ Deleted successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ Delete failed ({r.status_code}): {r.text}")
            except Exception as e:
                st.error(f"Delete request failed: {e}")
