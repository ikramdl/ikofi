print("Welcome to iKofi!")
drinks = ["Espresso", "Americano", "Latte", "Capuccino", "Mocha","Affogato", "Iced Americano", "Iced Latte", "Pretty in Pink"]
prices = [10, 12, 15, 18, 20, 22, 14, 16, 12]
More = True
orders=[]




def display_menu():
    print("Take a look at our menu:")
    for i in range(len(drinks)):
        print(f"{i+1}.{drinks[i]} - ${prices[i]}")



def take_order():
    #Taking the customer's order. 
    order = (input("What would you like to order? (please enter the index of the drink you'd like to order)"))
    #checking if the customer entered a number.
    while not order.isdigit():
        print(f"Invalid order, please make sure you're selecting a number")
        order = (input("What would you like to order? (please enter the index of the drink you'd like to order)"))
    #once confirmed we check that the customer is entering a number that is in the range of our menu
    order = int(order)
    while order < 1 or order > len(drinks):
        print(f"Invalid order, please select a number from the menu")
        order = (input("What would you like to order? (please enter the index of the drink you'd like to order)"))
    quantity = input("How many would you like to order?")
    while not quantity.isdigit():
           print(f"Invalid quantity, please make sure you're selecting a number")
           quantity = input("How many would you like to order?")
    order_line = {
        "drink": drinks[int(order)-1],
        "price": prices[int(order)-1],
        "quantity": int(quantity),
    }
    order_line["total"] = order_line["price"]*order_line["quantity"]
    #printing the order to the customer with the price.
    return order_line 



def another_order():
    Another = input(f"Would you like to add another product? (yes/no)").lower()
    while Another != "yes" and Another != "no":
        print(f"Invalid input, please enter 'yes' or 'no'")
        Another = input(f"Would you like to add another product? (yes/no)").lower()
    if Another == "yes":
        return True            
    else:
        print(f"Thank you for your order, please proceed for the payment!")
        return False              



def display_receipt():
    print("=============================")
    print("           iKOFI")
    print("=============================")
    print("                             ")
    for order in orders:
        print(f"{order['drink']} X {order['quantity']} = ${order['total']}")
    print("                             ")
    print("-----------------------------")
    print(f"TOTAL: ${sum(order['total'] for order in orders)}")
    print("=============================")
    print("Thank you, please come again!")

#Displaying the menu to the customer
display_menu()
while More:
#taking the customer's order
    found = False
    order_line = take_order()
    for order in orders:
        if order['drink'] == order_line['drink']:
            order['quantity'] += order_line['quantity']
            order['total'] += order_line['total']
            found = True
            break
    if not found:
            orders.append(order_line)
    More = another_order()
display_receipt()




