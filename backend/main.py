from fastapi import FastAPI, HTTPException
from fastapi import Depends
from sqlalchemy.orm import Session
from .database import get_db, engine, Base
from .models import MenuItem, Order, OrderItem, User
from pydantic import BaseModel
import bcrypt

Base.metadata.create_all(bind=engine)

#opening the home page
app = FastAPI()

class OrderItemRequest(BaseModel):
    quantity: int
    item_id: int

class MenuItemRequest(BaseModel):
    name: str
    price: int

class UserRequest(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

class LoginRequest(BaseModel):
    email: str
    password: str
    

@app.get("/")
def home():
    return {"message": "Welcome to iKofi!"}

#Opening the menu
@app.get("/menu")
def get_menu(db: Session = Depends(get_db)):
    return db.query(MenuItem).all()

#searching an item from the menu by id
@app.get("/menu/{item_id}")
def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code = 404, detail = "Item not found!")
    return item

@app.post("/menu")
def add_menu_item(menu_item: MenuItemRequest, db : Session = Depends(get_db)):
    new_item = MenuItem(
        name = menu_item.name,
        price = menu_item.price
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

cart = []
@app.post("/cart")
def add_to_cart(order: OrderItemRequest, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == order.item_id ).first()
    if not item:
        raise HTTPException(status_code = 404, detail ="Item Not Found!")
    for cart_item in cart:
        if cart_item["item_id"] == order.item_id:

            cart_item["quantity"] += order.quantity

            cart_item["total"] = cart_item["quantity"] * cart_item["price"]

            return {
                "message": "Your cart has been updated",
                "cart": cart
            }
    total = item.price * order.quantity

    new_entry = {
        "item_id": item.id,
        "name": item.name,
        "price": item.price,
        "quantity": order.quantity,
        "total": total
    }
    cart.append(new_entry)

    return {
        "message": "Your cart has been updated",
        "cart": cart
    }


@app.delete("/menu/{item_id}")
def delete_item(item_id:int, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(item_id == MenuItem.id).first()
    if not item:
        raise HTTPException(status_code=404, detail = "No Item Found!")
    db.delete(item)
    db.commit()
    return {"message":"Item Deleted Successfully!"}
@app.put("/menu/{item_id}")
def update_item(item_id:int, menu_item: MenuItemRequest, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(item_id == MenuItem.id).first()
    if not item:
        raise HTTPException(status_code=404, detail = "No Item Found!")
    item.name = menu_item.name
    item.price = menu_item.price
    db.commit()
    db.refresh(item)
    return item
@app.post("/user", response_model = UserResponse)
def register_user(user: UserRequest, db:Session = Depends(get_db)):
    hashed_password = bcrypt.hashpw(
    user.password.encode("utf-8"),
    bcrypt.gensalt()
    ).decode("utf-8")
    new_user = User(
    username=user.username,
    email=user.email,
    password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@app.post("/login")
def login_user(login: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not bcrypt.checkpw( login.password.encode("utf-8"), user.password.encode("utf-8")):
        raise HTTPException(status_code = 401, detail = "Invalid Email or Password" )
    return {"message": "Login successful!"}
