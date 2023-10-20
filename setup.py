from setuptools import setup

setup(
    name="mysql-table-creator",
    version="0.0.1",
    description="A package to create and append rows to a MySQL table",
    url="https://github.com/adaubner/mysql-table-creator",
    author="Andy Daubner, Che Hang Ng",
    license="MIT",
    packages=["mysql_table_creator"],
    install_requires=["pyodbc"],
)
