import json
from pathlib import Path
from typing import List, Dict, Any
from uuid import UUID

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "products.json"


def load_products() -> List[Dict[str, Any]]:
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_products(products: List[Dict[str, Any]]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2)


def get_all_products() -> List[Dict[str, Any]]:
    return load_products()


def add_product(product: Dict[str, Any]) -> Dict[str, Any]:
    products = load_products()

    # simple duplicate check by name (optional)
    if any(p.get("name", "").strip().lower() == product.get("name", "").strip().lower() for p in products):
        raise ValueError("Product with this name already exists.")

    products.append(product)
    save_products(products)
    return product


def remove_product(product_id: str) -> Dict[str, Any]:
    products = load_products()
    new_products = [p for p in products if p.get("id") != product_id]

    if len(new_products) == len(products):
        raise ValueError("Product not found.")

    save_products(new_products)
    return {"message": "Deleted successfully", "id": product_id}


def change_product(product_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    products = load_products()
    for p in products:
        if p.get("id") == product_id:
            p.update(updates)
            save_products(products)
            return p
    raise ValueError("Product not found.")
