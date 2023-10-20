# MySQL Table Creator

A Python script to interact with a MySQL database using pyodbc.

## Requirements

- Python 3.6 or above
- MySQL ODBC 8.1 Unicode Driver

## Installation

Use pip to install from github

```bash
pip install git+https://github.com/adaubner/mysql-table-creator.git
```

## Usage

Ensure that the MySQL ODBC 8.1 Unicode Driver is installed and the following environment variables are correctly configured:

- DATABASE_IP: The IP address of the database
- DATABASE_PORT: The port of the database
- DATABASE_USERNAME: The username of the database
- DATABASE_PASSWORD: The password of the database
- DATABASE_DATABASE: The name of the database

The script provides several functions for managing the MySQL database, read the docs for more information:

- `connect()`: Connects to a MySQL database.
- `drop_all(con, cursor)`: Drops the 'Project' database and creates a new one.
- `table_creator(table_schema, con, cursor)`: Creates a table in the database using a JSON schema.
- `append_row(table_name, column_names, row, con, cursor)`: Appends a row to an arbitrary table in the database.

## JSON schema example

The script utilizes a JSON schema for creating tables. Below is an example of the schema:  

```json
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
      "references_column": "id"
    }
  ]
}
```

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).  
  
Copyright (c) Andy Bruno Daubner (i6324958) and Che Hang Ng (i6309628)