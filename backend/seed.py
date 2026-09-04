from .database import SessionLocal, engine, Base
from .models import MenuItem

Base.metadata.create_all(bind=engine)

def seed_menu():
    db = SessionLocal()
    
    # Check if menu items are already seeded
    existing = db.query(MenuItem).first()
    if existing:
        print("Menu items already exist in the database.")
        db.close()
        return
    initial_menu = [
        {"name": "Espresso", "price": 10.00},
        {"name": "Americano", "price": 12.00},
        {"name": "Latte", "price": 15.00},
        {"name": "Cappuccino", "price": 18.00},
        {"name": "Mocha", "price": 20.00},
        {"name": "Affogato", "price": 22.00},
        {"name": "Iced Americano", "price": 14.00},
        {"name": "Iced Latte", "price": 16.00},
        {"name": "Pretty in Pink", "price": 12.00},
    ]


    for item in initial_menu:
        db.add(MenuItem(name = item["name"], price =item["price"]))
    db.commit()
    print("Database successfully seeded with menu items!")
    db.close()


    if __name__ == "__main__":
        seed_menu()