from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import get_db, engine, Base
from .models import MenuItem, Order, OrderItem, User
from pydantic import BaseModel
import bcrypt
import os
from pathlib import Path
from dotenv import load_dotenv
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = "HS256"
def create_access_token(user_id: int):
    expiration = datetime.utcnow() + timedelta(minutes=30)
    payload = {
        "user_id" : user_id,
        "exp": expiration
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm = ALGORITHM)
    return token

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    
    except JWTError:
        return None


print(create_access_token(17))
Base.metadata.create_all(bind=engine)

#opening the home page
app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

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
    token = create_access_token(user.id)
    return {
        "message": "Login successful!",
        "access_token": token
    }


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_access_token(token)
    if payload is None :
        raise HTTPException ( status_code=401, detail = "Invalid or expired token")
    user_id = payload["user_id"]
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
    )
    return user

@app.get("/profile", response_model = UserResponse)

def get_profile(current_user = Depends(get_current_user)):
    return current_user


