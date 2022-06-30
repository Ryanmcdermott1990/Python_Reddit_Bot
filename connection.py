import praw
from flask import Flask, request, render_template
import pandas as pd
import config
import psycopg2
from sqlalchemy import create_engine
# from config import config


conn_string = 'postgresql://Ryan:root@localhost:5432/postgres'
db = create_engine(conn_string)
conn = db.connect()
conn = psycopg2.connect(conn_string)
c = conn.cursor()
    
    
def closeConnection():
    conn.close()
    c.close()
    

