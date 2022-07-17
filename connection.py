import psycopg2
from sqlalchemy import create_engine

#This file is to be used to store all the connection information

conn_string = '{dbname}://{username}:{password}@{localhost:port}/{postgres}'
db = create_engine(conn_string)
conn = db.connect()
conn = psycopg2.connect(conn_string)
c = conn.cursor()
    
    
def closeConnection():
    conn.close()
    c.close()
    

