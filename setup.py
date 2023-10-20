# Copyright (c) Andy Bruno Daubner (i6324958) and Che Hang Ng (i6309628)

from setuptools import setup

setup(
    name="mysql-table-creator",
    version="0.0.1",
    packages=["mysql_table_creator"],
    package_data={
        "mysql_table_creator": ["sql_literals.json"]
    },
    include_package_data=True,
    description="A package to create and append rows to a MySQL table",
    url="https://github.com/adaubner/mysql-table-creator",
    author="Andy Daubner, Che Hang Ng",
    license="MIT",
    install_requires=["pyodbc"],
)
