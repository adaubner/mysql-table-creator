import pyodbc
import logging
import os
import re
import json

def clean_reserved_words(value: str) -> str:
    if value.upper() in sql_literals["reserved_words"]:
        return f"`{value}`"
    return value


def allowed_type(type: str) -> str:
    """Check if a sql data type is allowed, prevents sql injection

    The datatype is checked agains a list of allowed data types in MySQL 8.1

    Args:
        type (str): The sql data type to check

    Raises:
        ValueError: If the data type is not allowed

    Returns:
        str: the data type (made lowercase) if it is allowed
    """
    # Create a list with all data types of MySQL 8.1
    if any(
        [re.match(datatype, type.upper()) for datatype in sql_literals["datatypes"]]
    ):
        return type.lower()
    else:
        logging.error(f"Type {type} not allowed")
        raise ValueError(f"Type {type} not allowed")


def allowed_constraint(constraint: str) -> str:
    """Check if a sql constraint is allowed, prevents sql injection

    Args:
        constraint (str): The sql constraint to check

    Raises:
        ValueError: If the constraint is not allowed

    Returns:
        str: the constraint (made uppercase) if it is allowed
    """
    if any([
            re.match(allowed_constraint, constraint.upper())
            for allowed_constraint in sql_literals["constraints"]
    ]):
        return constraint.upper()
    else:
        logging.error(f"Constraint {constraint} not allowed")
        raise ValueError(f"Constraint {constraint} not allowed")


def allowed_value_table(value: str) -> str:
    """Check if a table name is allowed, prevents sql injection

    Args:
        value (str): The table name to check

    Raises:
        ValueError: If the table name is not allowed

    Returns:
        str: the table name if it is allowed
    """
    # Only allow strings where the first letter is uppercase and where the rest is either uppercase or lowercase
    if re.match(r"^[A-Z][a-zA-Z_]*$", value):
        return clean_reserved_words(value)
    else:
        logging.error(f"Value {value} not allowed")
        raise ValueError(f"Value {value} not allowed")


def allowed_value_column(value: str) -> str:
    """Check if a column name is allowed, prevents sql injection

    Args:
        value (str): The column name to check

    Raises:
        ValueError: If the column name is not allowed

    Returns:
        str: the column name if it is allowed
    """
    # Only allow strings where every letter is lowercase or an underscore
    if re.match(r"^[a-z_]*$", value):
        return clean_reserved_words(value)
    else:
        logging.error(f"Value {value} not allowed")
        raise ValueError(f"Value {value} not allowed")


def convert_to_python_type(value):
    """Converts a value to the correct python type if possible

    Args:
        value (any): The value to convert

    Returns:
        any: The converted value, or the original value if it could not be converted
    """
    value = str(value)
    regex_int = r"^[0-9]+$"
    regex_float = r"^[0-9]+\.[0-9]+$"
    regex_bool = r"^(true|false)$"
    regex_null = r"^null$"
    if re.match(regex_int, value):
        logging.debug(f"Value {value} converted to int")
        return int(value)
    elif re.match(regex_float, value):
        logging.debug(f"Value {value} converted to float")
        return float(value)
    elif re.match(regex_bool, value):
        logging.debug(f"Value {value} converted to bool")
        return bool(value)
    elif re.match(regex_null, value):
        logging.debug(f"Value {value} converted to None")
        return None
    else:
        logging.debug(f"Value {value} not converted")
        return value


##################### USER ACCESSIBLE METHODS #####################

def connect() -> tuple[pyodbc.Connection, pyodbc.Cursor]:
    """Connects to a MySQL database using pyodbc

    Requires the MySQL ODBC 8.1 Unicode Driver to be installed

    Uses the environment variables:
        DATABASE_IP: The IP address of the database
        DATABASE_PORT: The port of the database
        DATABASE_USERNAME: The username of the database
        DATABASE_PASSWORD: The password of the database
        DATABASE_DATABASE: The name of the database

    Returns:
        tuple: A tuple containing the connection and cursor object

    Raises:
        Exception: If any of the required environment variables are missing
    """

    # load sql literals from file, provides sql_literals["datatypes"] and sql_literals["reserved_words"]
    global sql_literals

    lib_dir = os.path.dirname(os.path.abspath(__file__))
    with open(lib_dir + "/sql_literals.json", "r") as f:
        sql_literals = json.load(f)

    ip = os.getenv("DATABASE_IP")
    port = os.getenv("DATABASE_PORT")
    username = os.getenv("DATABASE_USERNAME")
    password = os.getenv("DATABASE_PASSWORD")
    database = os.getenv("DATABASE_DATABASE")

    if not (ip and port and username and password and database):
        raise Exception("Missing environment variables")

    con_string = f"DRIVER={{MySQL ODBC 8.1 Unicode Driver}};SERVER={ip};PORT={port};DATABASE={database};UID={username};PWD={password};"

    con = pyodbc.connect(con_string)
    logging.info("Connected to database")

    cursor = con.cursor()

    return con, cursor

def table_creator(table_schema: dict, con: pyodbc.Connection, cursor: pyodbc.Cursor):
    """Creates a table in the database using a json schema

    Args:
        table_schema (dict): The schema of the table to create
        con (pyodbc.Connection): Connection object
        cursor (pyodbc.Cursor): Cursor object

    example_schema:
    {
        "name": "Person",
        "columns": [
            {
                "name": "id",
                "datatype": "INT",
                "constraints": ["NOT NULL", "AUTO_INCREMENT", "PRIMARY KEY"]
            },
            {
                "name": "name",
                "datatype": "VARCHAR(255)",
                "constraints": ["NOT NULL"]
            },
            {
                "name": "age",
                "datatype": "INT",
                "constraints": ["NOT NULL"]
            },
            {
                "name": "is_active",
                "datatype": "BOOLEAN",
                "constraints": ["NOT NULL"]
            }
        ],
        "foreign_keys": [
            {
                "name": "person_id",
                "references_table": "Person",
                "references_column": "id",
            }
        ]
    }
    """

    query = f"CREATE TABLE IF NOT EXISTS {allowed_value_table(table_schema['name'])} ("

    for column in table_schema["columns"]:
        query += f"{allowed_value_column(column['name'])} {allowed_type(column['datatype'])} "
        for constraint in column["constraints"]:
            query += f"{allowed_constraint(constraint)} "
        query += ", "
    if "foreign_keys" in table_schema:
        for foreign_key in table_schema["foreign_keys"]:
            query += f"FOREIGN KEY ({allowed_value_column(foreign_key['name'])}) REFERENCES {allowed_value_table(foreign_key['references_table'])}({allowed_value_column(foreign_key['references_column'])}) "
            query += ", "
    query = query.removesuffix(", ")

    query += ");"

    cursor.execute(query)
    con.commit()


def append_row(
    table_name: str,
    column_names: list[str],
    row: list,
    con: pyodbc.Connection,
    cursor: pyodbc.Cursor,
):
    """Appends a row to an arbitrary table in the database

    Args:
        table_name (str): The name of the table, must follow the convention Some_Table_Name
        column_names (list[str]): The names of the columns, must follow the convention some_column_name
        row (list): The values in the row, can be any datatype, but must be the same length as column_names
        con (pyodbc.Connection): Connection object
        cursor (pyodbc.Cursor): Cursor object
    """
    for i, entry in enumerate(row):
        row[i] = convert_to_python_type(entry)

    query = f"INSERT INTO {allowed_value_table(table_name)} ("
    query += ", ".join([allowed_value_column(column) for column in column_names])
    query += ") VALUES ("
    query += "?, " * len(row)
    query = query.removesuffix(", ")
    query += ");"
    cursor.execute(query, row)
    con.commit()
