from fastapi import FastAPI, HTTPException, Depends, Form
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


Base.metadata.create_all(bind=engine)

#opening the home page
app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

#----------------------------------------------------------- CLASSES -------------------------------------------------------------------#


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
    

#------------------------------------------------------------------------------------------------------------------------------------#

@app.get("/")

def home():
    return {"message": "Welcome to iKofi!"}

#-----------------------------------------------------------GET MENU-----------------------------------------------------------------#

#Opening the menu
@app.get("/menu")

def get_menu(db: Session = Depends(get_db)):
    return db.query(MenuItem).all()

#-----------------------------------------------------------POST LOGIN-----------------------------------------------------------------#

@app.post("/login")
def login_user(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == username).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not bcrypt.checkpw(
        password.encode("utf-8"),
        user.password.encode("utf-8")
    ):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer"
    }
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_access_token(token)
    if payload is None :
        raise HTTPException ( status_code=401, detail = "Invalid or expired token")
    user_id = payload["user_id"]
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException( status_code=401, detail="User not found")
    return user
def require_admin(current_user = Depends(get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

#-----------------------------------------------------------GET PROFILE-------------------------------------------------------------------#

@app.get("/profile", response_model = UserResponse)

def get_profile(current_user = Depends(get_current_user)):
    return current_user

#-----------------------------------------------------------GET MENU ITEM-----------------------------------------------------------------#

#searching an item from the menu by id
@app.get("/menu/{item_id}")

def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code = 404, detail = "Item not found!")
    return item

#-----------------------------------------------------------POST MENU----------------------------------------------------------------------#

@app.post("/menu")

def add_menu_item(menu_item: MenuItemRequest, db : Session = Depends(get_db), current_user = Depends(require_admin)):
    new_item = MenuItem(
        name = menu_item.name,
        price = menu_item.price
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

#-----------------------------------------------------------POST CART---------------------------------------------------------------------#

@app.post("/cart")

def add_to_cart(order: OrderItemRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    current_order = db.query(Order).filter(Order.user_id == current_user.id, Order.status == "Pending").first()
    if current_order is None:
        current_order = Order(
            user_id=current_user.id,
            grand_total=0,
            status="Pending"
        )
        db.add(current_order)
        db.commit()
        db.refresh(current_order)
    item = db.query(MenuItem).filter(MenuItem.id == order.item_id ).first()
    if not item:
        raise HTTPException(status_code = 404, detail ="Item Not Found!")
    existing_item = db.query(OrderItem).filter(OrderItem.order_id == current_order.id, OrderItem.item_id == item.id).first()
    if existing_item:
        existing_item.quantity += order.quantity
    else:
        new_order_item = OrderItem(
            item_id=item.id,
            quantity=order.quantity,
            order_id=current_order.id,
        )
        db.add(new_order_item)

    current_order.grand_total = 0
    for order_item in current_order.items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == order_item.item_id).first()
        current_order.grand_total += menu_item.price * order_item.quantity
        db.commit()
    return {
        "message": "Your cart has been updated"
    }

#-----------------------------------------------------------GET CART-----------------------------------------------------------------#

@app.get("/cart")
def get_cart(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    current_order = db.query(Order).filter( Order.user_id == current_user.id, Order.status == "Pending").first()
    if current_order is None:
        return {
            "message": "Your cart is empty"
        }
    order_items = db.query(OrderItem).filter( OrderItem.order_id == current_order.id ).all()

    cart = []
    for order_item in order_items:
        item = db.query(MenuItem).filter(MenuItem.id == order_item.item_id).first()
        cart_item = {
        "item_id": item.id,
        "name": item.name,
        "price": item.price,
        "quantity": order_item.quantity,
        "total": item.price * order_item.quantity
        }
        cart.append(cart_item)
    return {
    "order_id": current_order.id,
    "status": current_order.status,
    "grand_total": current_order.grand_total,
    "cart": cart
    }

#-----------------------------------------------------------DELETE CART------------------------------------------------------------------#


@app.delete("/cart/{item_id}")
def remove_from_cart(item_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    current_order = db.query(Order).filter(Order.user_id == current_user.id,Order.status == "Pending").first()

    if current_order is None:
        raise HTTPException(status_code=404,detail="Cart is empty")

    order_item = db.query(OrderItem).filter(OrderItem.order_id == current_order.id, OrderItem.item_id == item_id).first()

    if order_item is None:
        raise HTTPException( status_code=404, detail="Item not found in cart")
    
    db.delete(order_item)
    db.flush()

    current_order.grand_total = 0

    for item in current_order.items:
        menu_item = db.query(MenuItem).filter(
            MenuItem.id == item.item_id
        ).first()

        current_order.grand_total += menu_item.price * item.quantity

    db.commit()

    return {
        "message": "Item removed from cart"
    }
#-----------------------------------------------------------DELETE MENU ITEM---------------------------------------------------------------#

@app.delete("/menu/{item_id}")

def delete_item(item_id:int, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    item = db.query(MenuItem).filter(item_id == MenuItem.id).first()
    if not item:
        raise HTTPException(status_code=404, detail = "No Item Found!")
    db.delete(item)
    db.commit()
    return {"message":"Item Deleted Successfully!"}
@app.put("/menu/{item_id}")

def update_item(item_id:int, menu_item: MenuItemRequest, current_user = Depends(require_admin), db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(item_id == MenuItem.id).first()
    if not item:
        raise HTTPException(status_code=404, detail = "No Item Found!")
    item.name = menu_item.name
    item.price = menu_item.price
    db.commit()
    db.refresh(item)
    return item

#-----------------------------------------------------------POST USER-----------------------------------------------------------------#

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

