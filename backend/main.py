from fastapi import FastAPI, HTTPException
from fastapi import Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models import MenuItem, Order, OrderItem
from pydantic import BaseModel

#opening the home page
app = FastAPI()
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
class OrderItemRequest(BaseModel):
    quantity: int
    item_id: int
class MenuItemRequest(BaseModel):
    name: str
    price: int
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

@app.post("/checkout")
def checkout(db:Session = Depends(get_db)):
    cart_total = 0
    for cart_item in cart:
        cart += cart_item["total"]
    new_order = Order(grand_total=grand_total)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    for cart_item in cart:
        new_order_item = OrderItem(
            order_id = new_order.id,
            item_id = cart["item_id"],
            quantity = cart["item_quantity"]
        )
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