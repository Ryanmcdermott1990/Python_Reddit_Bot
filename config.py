import praw
from flask import Flask, request, render_template
import pandas as pd
import psycopg2
from sqlalchemy import create_engine

reddit = praw.Reddit(
    client_id="exuHx7RyoQLGG7aAwegocg",
    client_secret="XLml4bscH9DL8PPXcoFJFU3nYqjJGA",
    user_agent="macOS:com.dataAnalysis.myredditapp:v0.0.1 (by /u/SadMoney7025)",
)
