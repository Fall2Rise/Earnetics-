"""Stripe Product Management Router"""
from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import stripe
import os
from dotenv import load_dotenv

load_dotenv(override=True)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

router = APIRouter(prefix="/api/stripe", tags=["stripe"])


class ProductCreateRequest(BaseModel):
    name: str
    price: int  # in cents
    description: str | None = None
    interval: str = "month"  # month, year, week, day


class ProductResponse(BaseModel):
    id: str
    name: str
    price: int
    interval: str
    description: str | None = None


@router.get("/products")
def list_products() -> Dict[str, Any]:
    """List all Stripe products."""
    try:
        products = stripe.Product.list(limit=100)
        result = []
        
        for product in products.data:
            # Get price for each product
            prices = stripe.Price.list(product=product.id, limit=1)
            price_data = None
            if prices.data:
                pr = prices.data[0]
                price_data = {
                    "price_id": pr.id,
                    "amount": pr.unit_amount,
                    "interval": pr.recurring.get("interval") if pr.recurring else "one-time"
                }
            
            result.append({
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": price_data
            })
        
        return {
            "products": result,
            "total": len(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/products", response_model=ProductResponse)
def create_product(request: ProductCreateRequest) -> Dict[str, Any]:
    """Create a new Stripe product with pricing."""
    try:
        # Create product
        product = stripe.Product.create(
            name=request.name,
            description=request.description or ""
        )
        
        # Create price
        price = stripe.Price.create(
            product=product.id,
            unit_amount=request.price,
            currency="usd",
            recurring={"interval": request.interval}
        )
        
        return {
            "id": product.id,
            "name": product.name,
            "price": request.price,
            "interval": request.interval,
            "description": request.description
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/products/{product_id}")
def delete_product(product_id: str) -> Dict[str, Any]:
    """Archive a Stripe product."""
    try:
        product = stripe.Product.modify(product_id, active=False)
        return {
            "id": product.id,
            "status": "archived"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/customers")
def list_customers() -> Dict[str, Any]:
    """List Stripe customers."""
    try:
        customers = stripe.Customer.list(limit=100)
        return {
            "customers": [
                {
                    "id": c.id,
                    "email": c.email,
                    "name": c.name,
                    "created": c.created
                }
                for c in customers.data
            ],
            "total": len(customers.data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
