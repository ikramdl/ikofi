print("Welcome to iKofi!")
#listing our products and their prices.
drinks = ["Espresso", "Americano", "Latte", "Capuccino", "Mocha","Affogato", "Iced Americano", "Iced Latte", "Pretty in Pink"]
prices = [10, 12, 15, 18, 20, 22, 14, 16, 12]
#working on the interacion with the customer
More = True
Total = 0
quantities=[]
orders=[]
line_totals=[]
#using a function for displaying the drinks with their prices on numbered list as a menu
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
    #printing the order to the customer with the price.
    return order, quantity
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
    for i in range (len(orders)):
        print(f"{drinks[orders[i]-1]} X {quantities[i]} = ${line_totals[i]}")
    print("                             ")
    print("-----------------------------")
    print(f"TOTAL: ${Total}")
    print("=============================")
    print("Thank you, please come again!")

#Displaying the menu to the customer
display_menu()
while More:
#taking the customer's order
    order, quantity = take_order()
    orders.append(order)
    quantities.append(int(quantity))
    line_total = prices[order-1] * int(quantity)
    line_totals.append(line_total)
    Total = sum(line_totals)
    More = another_order()
display_receipt()




