from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Menu data:
menu = [
    {"id": 1, "name":"Espresso", "price":10},
    {"id": 2,"name":"Americano", "price":12},
    {"id": 3, "name":"Latte", "price":15},
    {"id": 4, "name":"Cappucino", "price":18},
    {"id": 5,"name":"Mocha", "price":20},
    {"id": 6, "name":"Affogato", "price":22},
    {"id": 7, "name":"Iced Americano", "price":14},
    {"id": 8, "name":"Iced Latte", "price":16},
    {"id": 9, "name":"Pretty in Pink", "price":12}
    ]


cart = []   #  <--- Stores all the carts items (order)
orders = [] #  <--- Stores all past checkout receipts

#model for the new incoming order requests
class OrderItem(BaseModel):
    item_id: int
    quantity: int

#home page
@app.get("/") # when somebody visitis the / url:
def home(): # run this function
    return {"message":"Welcome to ikofi!"} # return this message to the user

#to view the menu
@app.get("/menu")
def get_menu():
    return menu

# to view the items
@app.get("/menu/{item_id}")
def get_menu_item(item_id:int):
    for item in menu:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

# to edit the cart
@app.post("/cart")
def add_to_cart(order: OrderItem):
    #to add to cart we need to check if the item exists in the menu...
    selected_item = None
    for item in menu:
        if item["id"] == order.item_id:
            selected_item = item
            break

    # if the item doesn't exist in the menu:
    if not selected_item:
        raise HTTPException(status_code = 404, detail = "Item not found in menu")

    #check if item already exists in menu
    for cart_item in cart:
        if cart_item["id"] == order.item_id:
            cart_item["quantity"] += order.quantity
            cart_item["total"] = cart_item["price"] * cart_item["quantity"]
            return {"messaege": "Cart has been updated successfully!", "cart": cart}
        
    # Adding new item to the cart
    item_total = selected_item["price"] * order.quantity
    new_entry={
        "id": selected_item["id"],
        "name": selected_item["name"],
        "price": selected_item["price"],
        "quantity": order.quantity,
        "total": item_total
    }
    cart.append(new_entry)
    return {"message": "Item added successfully to cart", "cart": cart}

# to view the cart
@app.get("/cart")
def view_cart():
    grand_total = sum(item["total"] for item in cart)
    return{
        "cart": cart,
        "grand_total": grand_total
    }

# Removing an item from the cart
@app.delete("/cart/{item_id}")
def remove_from_cart(item_id : int):
    for cart_item in cart:
        if cart_item["id"] == item_id:
            cart.remove(cart_item)
            return {"message": "Item removed from the cart successfully", "cart": cart}
    raise HTTPException(status_code = 404, detail = "Item not found in cart")

# Deleting the entire cart
@app.delete("/cart")
def clear_cart():
    cart.clear()
    return {"message": "Cart cleared!", "cart": cart}
    
# checkout/ showing the bill
@app.post("/checkout")
def checkout():
    if not cart:
        raise HTTPException(status_code=400, detail = "Cart is Empty")

    grand_total = sum(item["total"] for item in cart)
    order_id = len(orders) +1 # <--- this helps us make a unique id for each order, like so: the first order's id is 1, the second is 2 etc...
    receipt = {
        "order_id": order_id,
        "message": "Order placed successfully! Thank you for ordering from ikofi.",
        "order_details": list(cart),  # snapshot of the items ordered (currently in the cart)
        "grand_total": grand_total,
        "status": "confirmed"
    }
    cart.clear()
    return receipt

# to check the history of the orders
@app.get("orders")
def get_order_history():
    return {
        "total": len(orders),
        "orders":orders
    }

# to look up one specific order
@app.get("orders{order_id}")
def get_order(order_id: int):
        for order in orders:
            if order["order_id"] == order_id:
                return order
        raise HTTPException(status_code=404, details = "Order not found")
