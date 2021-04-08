import sqlite3 as sql

conn=sql.connect('database1.db')
print('Database Successfully Created')

c=conn.cursor()

c.execute(""" CREATE TABLE records1 (
    First_Name TEXT,
    Last_Name TEXT,
    Email TEXT,
    Password TEXT
)""")
conn.commit()
print('Table Successfully Created')

conn.close()