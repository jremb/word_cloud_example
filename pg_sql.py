def list_tables() -> str:
    """
    List all user created tables in the database.
    """
    return "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
