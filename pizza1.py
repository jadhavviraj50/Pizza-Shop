import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import time
from collections import defaultdict



# Initialize the main application window
app = tk.Tk()
app.title("Pizza Shop Application")

# Initialize ingredients and quantities
ingredients = {
    "Dough": 5,
    "Sauce": 5,
    "Toppings": 5
}

ingredient_options = ["Dough", "Sauce", "Toppings"]  # Options for the dropdown

# Initialize order variables
orders = []
order_id_counter = 1
collection_queue = []

order_id_counter = 1  # Initialize order ID counter

current_order_start_time = None

pizza_orders = defaultdict(list)

order_log = []

# Create functions for different actions
def add_to_basket():
    global order_id_counter  # Declare the variable as global
    size = size_var.get()
    quantity = int(quantity_var.get())
    total_ingredients_needed = calculate_ingredients(size, quantity)

    for ingredient, required_quantity in total_ingredients_needed.items():
        if ingredients[ingredient] < required_quantity:
            messagebox.showerror("Error", f"Not enough {ingredient} available.")
            return

    order = {"order_id": order_id_counter, "size": size, "quantity": quantity}
    orders.append(order)
    update_ingredients(total_ingredients_needed)
    update_basket()

    
def update_basket():
    basket_text.delete("1.0", tk.END)
    for order in orders:
        basket_text.insert(tk.END, f"Order ID: {order['order_id']}, Size: {order['size']}, Quantity: {order['quantity']}\n")

def calculate_ingredients(size, quantity):
    if size == "Small":
        return {"Dough": 1 * quantity, "Sauce": 1 * quantity, "Toppings": 2 * quantity}
    elif size == "Medium":
        return {"Dough": 2 * quantity, "Sauce": 1 * quantity, "Toppings": 3 * quantity}
    elif size == "Large":
        return {"Dough": 3 * quantity, "Sauce": 2 * quantity, "Toppings": 4 * quantity}

def update_ingredients_display():
    ingredients_text.delete("1.0", tk.END)
    for ingredient, quantity in ingredients.items():
        ingredients_text.insert(tk.END, f"{ingredient}: {quantity}\n")

def update_ingredients(needed_ingredients):
    for ingredient, quantity in needed_ingredients.items():
        ingredients[ingredient] -= quantity
        if ingredients[ingredient] <= 0:
            ingredients[ingredient] = 0  # Ensure ingredient quantity doesn't go negative

    update_ingredients_display()

def save_to_pdf(shopping_list):
    c = canvas.Canvas("shopping_list.pdf", pagesize=letter)
    y_position = 750
    for ingredient, quantity in shopping_list.items():
        c.drawString(100, y_position, f"{ingredient}: {quantity}")
        y_position -= 20
    c.save()
    
def checkout():
    # Calculate the total cost and show a checkout message
    total_cost = calculate_total_cost()
    messagebox.showinfo("Checkout", f"Total Cost: ${total_cost}\nThank you for your order!")

def calculate_total_cost():
    total_cost = 0
    for order in orders:
        if order['size'] == "Small":
            total_cost += 5 * order['quantity']
        elif order['size'] == "Medium":
            total_cost += 7 * order['quantity']
        elif order['size'] == "Large":
            total_cost += 10 * order['quantity']
    return total_cost

def add_ingredients():
    ingredient_name = ingredient_option_var.get()  # Use the selected ingredient from the dropdown
    ingredient_quantity = int(ingredient_quantity_var.get())
    
    if ingredient_name in ingredients:
        ingredients[ingredient_name] += ingredient_quantity
    else:
        ingredients[ingredient_name] = ingredient_quantity
    
    update_ingredients_display()
    
def place_order():
    global orders, collection_queue, order_id_counter, current_order_start_time
    current_order_start_time = time.time()

    order_id = order_id_counter
    order_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    for order in orders:
        order["order_id"] = order_id
        order["order_time"] = order_time
        pizza_id = f"{order['size']}-{order['quantity']}"
        pizza_orders[pizza_id].append(order_id)
        pizza_orders[pizza_id].sort(key=lambda x: pizza_orders[pizza_id].count(x), reverse=True)

    collection_queue.extend(orders)
    orders = []
    update_basket()
    update_collection_queue_display()
    messagebox.showinfo("Order Placed", "Order has been placed and added to the collection queue.")
    order_id_counter += 1  # Increment the order ID counter for the next session
    
def update_collection_queue_display():
    collection_queue_text.delete("1.0", tk.END)
    for order in collection_queue:
        collection_queue_text.insert(tk.END, f"Order ID: {order['order_id']}, Size: {order['size']}, Quantity: {order['quantity']}\n")

def order_delivered():
    global collection_queue
    if collection_queue:
        delivered_order = collection_queue.pop(0)  # Remove the first order in the queue
        update_collection_queue_display()

        order_id = delivered_order.get("order_id")
        order_time = delivered_order.get("order_time")
        delivered_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        quantity = delivered_order.get("quantity")
        size = delivered_order.get("size")
        
        order_log.append({
            "order_id": order_id,
            "order_time": order_time,
            "delivered_time": delivered_time,
            "quantity": quantity,
            "size": size
        })

        elapsed_time = time.time() - current_order_start_time
        elapsed_hours = int(elapsed_time // 3600)
        elapsed_minutes = int((elapsed_time % 3600) // 60)
        elapsed_seconds = int(elapsed_time % 60)
        messagebox.showinfo(
            "Order Delivered",
            f"Order ID {delivered_order['order_id']} has been delivered.\nTime taken: {elapsed_hours} hours, {elapsed_minutes} minutes, {elapsed_seconds} seconds."
        )
    else:
        messagebox.showinfo("No Orders", "No orders in the collection queue.")

def generate_shopping_list():
    zero_quantity_ingredients = [ingredient for ingredient, quantity in ingredients.items() if quantity == 0]
    
    if zero_quantity_ingredients:
        pdf_filename = "shopping_list.pdf"
        c = canvas.Canvas(pdf_filename, pagesize=letter)
        c.drawString(100, 750, "Shopping List - Ingredients with Zero Quantities")

        y = 700
        for ingredient in zero_quantity_ingredients:
            c.drawString(100, y, ingredient)
            y -= 20

        c.save()
        messagebox.showinfo("Shopping List Generated", f"Shopping list saved as '{pdf_filename}'")
    else:
        messagebox.showinfo("No Items", "No ingredients with zero quantities.")

def update_timer():
    if current_order_start_time is not None:
        elapsed_time = time.time() - current_order_start_time
        elapsed_hours = int(elapsed_time // 3600)
        elapsed_minutes = int((elapsed_time % 3600) // 60)
        elapsed_seconds = int(elapsed_time % 60)
        timer_var.set(f"{elapsed_hours:02}:{elapsed_minutes:02}:{elapsed_seconds:02}")
    else:
        timer_var.set("00:00:00")
    app.after(1000, update_timer)
    
def generate_pizza_report():
    if not pizza_orders:
        messagebox.showinfo("No Pizza Orders", "No pizza orders available for reporting.")
        return
    
    pdf_filename = "pizza_report.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    c.drawString(100, 750, "Pizza Order Report - Most Favorite Pizzas")
    
    y = 700
    for pizza_id, order_ids in pizza_orders.items():
        size, quantity = pizza_id.split("-")
        c.drawString(100, y, f"Pizza: Size {size}, Quantity {quantity}")
        y -= 20
        c.drawString(120, y, "Order ID\t\tDelivery Count\t\tLast 3 Deliveries")
        y -= 20
        
        for order_id in order_ids:
            delivery_count = order_ids.count(order_id)
            last_three_deliveries = order_ids[-3:] if len(order_ids) >= 3 else order_ids
            last_deliveries_text = ", ".join(str(order) for order in last_three_deliveries)
            
            c.drawString(120, y, f"{order_id}\t\t{delivery_count}\t\t{last_deliveries_text}")
            y -= 20
        
        y -= 20
    
    c.save()
    messagebox.showinfo("Pizza Report Generated", f"Pizza report saved as '{pdf_filename}'")
    
def generate_order_log():
    if not order_log:
        messagebox.showinfo("No Orders in Log", "No orders in the order log.")
        return

    pdf_filename = "order_log.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    c.drawString(100, 750, "Order Log")

    y = 700
    for entry in order_log:
        order_id = entry["order_id"]
        order_time = entry["order_time"]
        delivered_time = entry["delivered_time"]
        quantity = entry["quantity"]
        size = entry["size"]
        
        c.drawString(100, y, f"Order ID: {order_id}")
        y -= 20
        c.drawString(120, y, f"Order Time: {order_time}")
        y -= 20
        c.drawString(120, y, f"Delivered Time: {delivered_time}")
        y -= 20
        c.drawString(120, y, f"Quantity: {quantity}")
        y -= 20
        c.drawString(120, y, f"Size: {size}")
        y -= 40

    c.save()
    messagebox.showinfo("Order Log Generated", f"Order log saved as '{pdf_filename}'")

# Create GUI components
size_var = tk.StringVar(value="Small")
quantity_var = tk.StringVar(value="1")

size_label = tk.Label(app, text="Select Size:")
size_dropdown = tk.OptionMenu(app, size_var, "Small", "Medium", "Large")
quantity_label = tk.Label(app, text="Quantity:")
quantity_entry = tk.Entry(app, textvariable=quantity_var)
add_button = tk.Button(app, text="Add to Order", command=add_to_basket)
basket_label = tk.Label(app, text="Basket:")
basket_text = tk.Text(app, height=10, width=40)
checkout_button = tk.Button(app, text="Go to Checkout", command=checkout)
ingredients_label = tk.Label(app, text="Ingredients:")
ingredients_text = tk.Text(app, height=5, width=30)
update_ingredients_display()
ingredient_name_var = tk.StringVar()
ingredient_quantity_var = tk.StringVar(value="5")

ingredient_name_label = tk.Label(app, text="Ingredient Name:")
ingredient_name_entry = tk.Entry(app, textvariable=ingredient_name_var)
ingredient_quantity_label = tk.Label(app, text="Quantity:")
ingredient_quantity_entry = tk.Entry(app, textvariable=ingredient_quantity_var)
add_ingredient_button = tk.Button(app, text="Add Ingredient", command=add_ingredients)

# Ingredients display
ingredients_label = tk.Label(app, text="Ingredients:")
ingredients_text = tk.Text(app, height=5, width=30)
update_ingredients_display()  # Initialize the ingredient display

# Place Order button
place_order_button = tk.Button(app, text="Place Order", command=place_order)

# Collection Queue display
collection_queue_label = tk.Label(app, text="Collection Queue:")
collection_queue_text = tk.Text(app, height=10, width=40)
update_collection_queue_display()  # Initialize the collection queue display

# Timer display
timer_label = tk.Label(app, text="Timer:")
timer_var = tk.StringVar()
timer_var.set("00:00:00")
timer_display = tk.Label(app, textvariable=timer_var)


place_order_button = tk.Button(app, text="Place Order", command=place_order)

# Order Delivered button
order_delivered_button = tk.Button(app, text="Order Delivered", command=order_delivered)

# Dropdown for ingredient selection
ingredient_option_var = tk.StringVar(value=ingredient_options[0])
ingredient_option_dropdown = tk.OptionMenu(app, ingredient_option_var, *ingredient_options)

ingredient_quantity_label = tk.Label(app, text="Quantity:")
ingredient_quantity_entry = tk.Entry(app, textvariable=ingredient_quantity_var)
add_ingredient_button = tk.Button(app, text="Add Ingredient", command=add_ingredients)

generate_list_button = tk.Button(app, text="Generate Shopping List", command=generate_shopping_list)

generate_report_button = tk.Button(app, text="Generate Pizza Report", command=generate_pizza_report)

generate_log_button = tk.Button(app, text="Generate Order Log", command=generate_order_log)


# Arrange GUI components using grid layout
size_label.grid(row=0, column=0, sticky="w")
size_dropdown.grid(row=0, column=1, sticky="w")
quantity_label.grid(row=0, column=2, sticky="w")
quantity_entry.grid(row=0, column=3, sticky="w")
add_button.grid(row=0, column=4, sticky="w")
basket_label.grid(row=1, column=0, sticky="w")
basket_text.grid(row=2, column=0, columnspan=5, sticky="w")
checkout_button.grid(row=3, column=3, sticky="e")
ingredients_label.grid(row=4, column=0, sticky="w")
ingredients_text.grid(row=5, column=0, columnspan=5, sticky="w")
ingredient_name_label.grid(row=6, column=0, sticky="w")

ingredient_quantity_label.grid(row=6, column=2, sticky="w")
ingredient_quantity_entry.grid(row=6, column=3, sticky="w")
add_ingredient_button.grid(row=6, column=4, sticky="w")
ingredients_label.grid(row=7, column=0, sticky="w")
ingredients_text.grid(row=8, column=0, columnspan=5, sticky="w")
place_order_button.grid(row=3, column=4, sticky="e")
collection_queue_label.grid(row=9, column=0, sticky="w")
collection_queue_text.grid(row=10, column=0, columnspan=5, sticky="w")
place_order_button.grid(row=3, column=4, sticky="e")
order_delivered_button.grid(row=10, column=4, sticky="e")

ingredient_option_dropdown.grid(row=6, column=1, sticky="w")
ingredient_quantity_label.grid(row=6, column=2, sticky="w")
ingredient_quantity_entry.grid(row=6, column=3, sticky="w")
add_ingredient_button.grid(row=6, column=4, sticky="w")
generate_list_button.grid(row=9, column=3, sticky="e")

generate_report_button.grid(row=13, column=3, sticky="e")

generate_log_button.grid(row=11, column=3, sticky="e")


# Start the main event loop

app.after(1000, update_timer)
app.mainloop()
