from app.database import execute_query


def main():
    print("\n1. ALL TABLES")
    tables = execute_query(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name;
        """
    )

    for table in tables:
        print(table)


    print("\n2. ALL CUSTOMERS")

    customers = execute_query(
        """
        SELECT *
        FROM customers;
        """
    )

    for customer in customers:
        print(customer)


    print("\n3. CUSTOMERS FROM DELHI")

    delhi_customers = execute_query(
        """
        SELECT customer_name, city
        FROM customers
        WHERE city = ?;
        """,
        ("Delhi",)
    )

    for customer in delhi_customers:
        print(customer)

    print("\n4. TOTAL SPENDING PER CUSTOMER")

    customer_spending = execute_query(
        """
        SELECT
            customers.customer_name,
            SUM(order_items.quantity * order_items.unit_price) AS total_spent
        FROM customers
        JOIN orders
            ON customers.customer_id = orders.customer_id
        JOIN order_items
            ON orders.order_id = order_items.order_id
        WHERE orders.status = 'completed'
        GROUP BY customers.customer_id, customers.customer_name
        ORDER BY total_spent DESC;
        """
    )

    for customer in customer_spending:
        print(customer)


if __name__ == "__main__":
    main()