from app.memory import ConversationMemory


def main():
    memory = ConversationMemory(window_size=3)

    memory.add_turn(
        "Show all customers.",
        "SELECT * FROM customers;",
    )

    memory.add_turn(
        "Only customers from Delhi.",
        "SELECT * FROM customers WHERE city = 'Delhi';",
    )

    memory.add_turn(
        "Sort them by signup date.",
        """
        SELECT *
        FROM customers
        WHERE city = 'Delhi'
        ORDER BY signup_date;
        """,
    )

    print("\nAFTER 3 TURNS:\n")
    print(memory.format_for_prompt())

    memory.add_turn(
        "Show only their names.",
        """
        SELECT customer_name
        FROM customers
        WHERE city = 'Delhi'
        ORDER BY signup_date;
        """,
    )

    print("\nAFTER 4TH TURN:\n")
    print(memory.format_for_prompt())


if __name__ == "__main__":
    main()