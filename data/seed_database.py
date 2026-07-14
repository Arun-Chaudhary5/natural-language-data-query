import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).parent / "ecommerce.db"


def create_connection():
    return sqlite3.connect(DATABASE_PATH)


def create_tables(connection):
    cursor = connection.cursor()

    cursor.executescript(
        """
        DROP TABLE IF EXISTS order_items;
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS customers;
        DROP TABLE IF EXISTS categories;

        CREATE TABLE categories (
            category_id INTEGER PRIMARY KEY,
            category_name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            city TEXT NOT NULL,
            signup_date TEXT NOT NULL
        );

        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            price REAL NOT NULL CHECK (price >= 0),

            FOREIGN KEY (category_id)
                REFERENCES categories(category_id)
        );

        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            status TEXT NOT NULL,

            FOREIGN KEY (customer_id)
                REFERENCES customers(customer_id)
        );

        CREATE TABLE order_items (
            order_item_id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            unit_price REAL NOT NULL CHECK (unit_price >= 0),

            FOREIGN KEY (order_id)
                REFERENCES orders(order_id),

            FOREIGN KEY (product_id)
                REFERENCES products(product_id)
        );
        """
    )

    connection.commit()


def insert_sample_data(connection):
    cursor = connection.cursor()

    categories = [
        (1, "Electronics"),
        (2, "Clothing"),
        (3, "Books"),
        (4, "Home"),
    ]

    customers = [
        (1, "Aarav Sharma", "aarav@example.com", "Delhi", "2024-01-10"),
        (2, "Riya Mehta", "riya@example.com", "Mumbai", "2024-02-15"),
        (3, "Kabir Singh", "kabir@example.com", "Delhi", "2024-03-20"),
        (4, "Ananya Gupta", "ananya@example.com", "Bengaluru", "2024-04-05"),
        (5, "Vihaan Patel", "vihaan@example.com", "Ahmedabad", "2024-05-12"),
    ]

    products = [
        (1, "Laptop", 1, 75000),
        (2, "Smartphone", 1, 30000),
        (3, "T-Shirt", 2, 1200),
        (4, "Jeans", 2, 2500),
        (5, "Python Book", 3, 800),
        (6, "SQL Book", 3, 650),
        (7, "Desk Lamp", 4, 1500),
        (8, "Office Chair", 4, 9000),
    ]

    orders = [
        (1, 1, "2025-01-10", "completed"),
        (2, 2, "2025-01-15", "completed"),
        (3, 1, "2025-02-05", "completed"),
        (4, 3, "2025-02-20", "cancelled"),
        (5, 4, "2025-03-12", "completed"),
        (6, 5, "2025-03-25", "completed"),
        (7, 2, "2025-04-10", "completed"),
        (8, 3, "2025-05-05", "completed"),
    ]

    order_items = [
        (1, 1, 1, 1, 75000),
        (2, 1, 5, 2, 800),
        (3, 2, 2, 1, 30000),
        (4, 3, 7, 2, 1500),
        (5, 4, 4, 1, 2500),
        (6, 5, 8, 1, 9000),
        (7, 6, 3, 3, 1200),
        (8, 7, 6, 2, 650),
        (9, 8, 1, 1, 75000),
        (10, 8, 7, 1, 1500),
    ]

    cursor.executemany(
        "INSERT INTO categories VALUES (?, ?)",
        categories,
    )

    cursor.executemany(
        "INSERT INTO customers VALUES (?, ?, ?, ?, ?)",
        customers,
    )

    cursor.executemany(
        "INSERT INTO products VALUES (?, ?, ?, ?)",
        products,
    )

    cursor.executemany(
        "INSERT INTO orders VALUES (?, ?, ?, ?)",
        orders,
    )

    cursor.executemany(
        "INSERT INTO order_items VALUES (?, ?, ?, ?, ?)",
        order_items,
    )

    connection.commit()


def main():
    connection = create_connection()

    try:
        create_tables(connection)
        insert_sample_data(connection)

        print(f"Database created successfully at: {DATABASE_PATH}")

    finally:
        connection.close()


if __name__ == "__main__":
    main()