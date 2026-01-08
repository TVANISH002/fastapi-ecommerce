from dotenv import load_dotenv
import os
from fastapi import FastAPI, HTTPException, Query, Path, Depends
from fastapi.responses import JSONResponse
from uuid import uuid4, UUID
from datetime import datetime
from typing import Dict

from app.service.products import (
    get_all_products,
    add_product,
    remove_product,
    change_product,
    load_products,
)
from app.schema.product import Product, ProductUpdate

load_dotenv()
app = FastAPI(title="FastAPI Ecommerce")


def common_logic():
    return "Hello There"


@app.get("/", response_model=dict)
def root(dep=Depends(common_logic)):
    db_path = os.getenv("BASE_URL", "Not set")
    return JSONResponse(
        status_code=200,
        content={
            "message": "Welcome to FastAPI.",
            "dependency": dep,
            "data_path": db_path,
        },
    )


@app.get("/products", response_model=Dict)
def list_products(
    dep=Depends(load_products),
    name: str = Query(default=None, min_length=1, max_length=50),
    sort_by_price: bool = Query(default=False),
    order: str = Query(default="asc"),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    products = dep

    if name:
        needle = name.strip().lower()
        products = [p for p in products if needle in p.get("name", "").lower()]

    if not products:
        raise HTTPException(status_code=404, detail=f"No product found matching name={name}")

    if sort_by_price:
        reverse = order == "desc"
        products = sorted(products, key=lambda p: p.get("price", 0), reverse=reverse)

    total = len(products)
    products = products[offset : offset + limit]
    return {"total": total, "limit": limit, "items": products}


@app.get("/products/{product_id}", response_model=Dict)
def get_product_by_id(product_id: str = Path(..., min_length=36, max_length=36)):
    products = get_all_products()
    for product in products:
        if product.get("id") == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found!")


@app.post("/products", status_code=201)
def create_product(product: Product):
    product_dict = product.model_dump(mode="json")
    product_dict["id"] = str(uuid4())
    product_dict["created_at"] = datetime.utcnow().isoformat() + "Z"

    try:
        add_product(product_dict)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return product_dict


@app.delete("/products/{product_id}")
def delete_product(product_id: UUID = Path(...)):
    try:
        return remove_product(str(product_id))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/products/{product_id}")
def update_product(product_id: UUID, payload: ProductUpdate):
    try:
        updated = change_product(
            str(product_id),
            payload.model_dump(mode="json", exclude_unset=True),
        )
        return updated
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
