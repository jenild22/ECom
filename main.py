from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select
from models import User, Product, Order
from db import create_user, update_user_db, create_product, engine

app = FastAPI()

class LoginRequest(BaseModel):
    username: str
    password: str

class OrderCreateRequest(BaseModel):
    buyer_id: int
    product_id: int
    quantity: int

@app.get("/")
async def root():
    return {"message": "Hello World"}



@app.post("/register")
async def register(user: User):
    create_user(user)
    return {"message": f"User {user.username} registered successfully!"}

@app.post("/login")
async def login(credentials: LoginRequest):
    with Session(engine) as db:
        statement = select(User).where(User.username == credentials.username)
        filtered_user = db.exec(statement).first()

        if filtered_user and filtered_user.password == credentials.password:
            return {
                "message": f"Welcome {filtered_user.username}!",
                "role": filtered_user.role,
                "user_id": filtered_user.id
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

@app.get("/users/{user_id}")
async def get_user_details(user_id: int):
    with Session(engine) as db:
        user = db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

@app.put("/users/{user_id}")
async def update_user(user_id: int, updated_data: User):
    updated_user = update_user_db(user_id, updated_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User details updated successfully", "user": updated_user}

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    with Session(engine) as db:
        user = db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db.delete(user)
        db.commit()
        return {"message": f"User {user_id} deleted successfully"}



@app.post("/products")
async def add_product(product: Product):
    with Session(engine) as db:
        seller = db.get(User, product.seller_id)
        if not seller or seller.role.upper() != "SELLER":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only registered sellers can add products"
            )
        
        saved_product = create_product(product)
        return {"message": "Product created successfully", "product": saved_product}

@app.get("/seller/{seller_id}/products")
async def get_seller_products(seller_id: int):
    with Session(engine) as db:
        statement = select(Product).where(Product.seller_id == seller_id)
        products = db.exec(statement).all()
        return products

@app.put("/products/{product_id}")
async def update_product(product_id: int, updated_data: Product):
    with Session(engine) as db:
        product = db.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product.name = updated_data.name
        product.description = updated_data.description
        product.price = updated_data.price
        product.quantity = updated_data.quantity
        
        db.add(product)
        db.commit()
        db.refresh(product)
        return {"message": "Product updated successfully", "product": product}

@app.delete("/products/{product_id}")
async def delete_product(product_id: int):
    with Session(engine) as db:
        product = db.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        db.delete(product)
        db.commit()
        return {"message": f"Product {product_id} deleted successfully"}



@app.get("/products")
async def get_all_products():
    with Session(engine) as db:
        statement = select(Product).where(Product.quantity > 0)
        return db.exec(statement).all()

@app.get("/products/{product_id}")
async def get_product_details(product_id: int):
    with Session(engine) as db:
        product = db.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

@app.post("/orders")
async def purchase_product(order_req: OrderCreateRequest):
    if order_req.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order quantity must be greater than 0"
        )

    with Session(engine) as db:
        buyer = db.get(User, order_req.buyer_id)
        if not buyer or buyer.role.upper() != "BUYER":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only registered buyers can place orders"
            )

        product = db.get(Product, order_req.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product.quantity < order_req.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock. Only {product.quantity} items available."
            )

        total_amount = product.price * order_req.quantity

        new_order = Order(
            buyer_id=order_req.buyer_id,
            seller_id=product.seller_id,
            product_id=product.id,
            quantity=order_req.quantity,
            price=product.price,
            total_amount=total_amount,
            order_status="SUCCESS"
        )

        product.quantity -= order_req.quantity

        db.add(new_order)
        db.add(product)
        db.commit()
        db.refresh(new_order)

        return {"message": "Order placed successfully", "order": new_order}

@app.get("/orders/buyer/{buyer_id}")
async def get_buyer_orders(buyer_id: int):
    with Session(engine) as db:
        statement = select(Order).where(Order.buyer_id == buyer_id)
        return db.exec(statement).all()

@app.get("/orders/{order_id}")
async def get_order_details(order_id: int):
    with Session(engine) as db:
        order = db.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order