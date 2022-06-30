from cmath import e
from logging import error
from pkgutil import iter_modules
import praw
from flask import Flask, request, render_template, redirect, url_for, flash
import pandas as pd
import psycopg2
import config
import connection
from sqlalchemy import create_engine, inspect, select
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from itertools import chain
from flask_login import login_required, current_user, LoginManager, UserMixin, login_user, logout_user

# global variables, limit
limitvar = 10
reddit = config.reddit
c = connection.c
db = connection.db
subredd = "askreddit"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://Ryan:root@localhost:5432/postgres'
app.config['SECRET_KEY'] = 'njfDV949FDSth3iSF483nknJk'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

dbat = SQLAlchemy(app)
# app.run(threaded=True)

dbat.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return Users.query.get(userid)

class Users (UserMixin, dbat.Model):
    userid = dbat.Column(dbat.Integer, primary_key=True, autoincrement=True, nullable=False)
    firstname = dbat.Column(dbat.String(120), unique=False, nullable=False)
    lastname = dbat.Column(dbat.String(120), unique=False, nullable=False)
    email = dbat.Column(dbat.String(120), unique=True, nullable=False)
    username = dbat.Column(dbat.String(120), nullable=False)
    pass_word = dbat.Column(dbat.String(120), nullable=False)
    
    def get_id(self):
           return (self.userid)
    
   
    def __init__(self, userid, firstname, lastname, email, username, pass_word):
        self.userid = userid
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.username = username
        self.pass_word = pass_word


def callApi(limitvar, subredd):
    subreddit = reddit.subreddit(subredd)
    df = pd.DataFrame([vars(post) for post in subreddit.hot(limit=limitvar)])
    df = df[["id", "title", "score", "num_comments", "created_utc", "url"]]
    df['created_utc'] = pd.to_datetime(df['created_utc'], unit='s')
    df.to_sql('posts', db, if_exists='replace', index=False)
    
    
    # csv_file = "./reddit.csv"
    # df.to_csv(csv_file, index=False, encoding='utf-8')

@app.route('/index', methods = ['POST', 'GET'])
@login_required

def index():
    if request.method == 'POST':
        limitvar = int(request.form['records'])
        subredd = request.form['Sub-reddit']
        callApi(limitvar, subredd)
        
    subr = []
    
    for subreddit in reddit.subreddits.default(limit=10):
        subr.append(subreddit.display_name)
    return render_template('index.html', subr=subr)

@app.route('/data')
@login_required
def data():
    conn_string = 'postgresql://Ryan:root@localhost:5432/postgres'
    db = create_engine(conn_string)
    conn = db.connect()
    conn = psycopg2.connect(conn_string)
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    result = c.fetchall()
    print (result)
    c.execute('CREATE TABLE IF NOT EXISTS posts (id text, title text, score integer, num_comments integer, created_utc date, url text)')
    c.execute('''  
SELECT * FROM posts
          ''')
    data1 = c.fetchall()
    c.execute('''  
SELECT id, num_comments FROM posts GROUP BY id, num_comments LIMIT 10
          ''')
    data = c.fetchall()
# c.execute('''
# SELECT id, num_comments FROM posts GROUP BY id, num_comments LIMIT 10
#           ''')
    c.execute('''
  SELECT * FROM posts ORDER BY created_utc LIMIT 10         
  ''')
    labels = c.fetchall()
    connection.closeConnection()

    return render_template('data.html', data1=data1, labels=labels, data=data, len=len(labels))
# for row in c.fetchall():
#     print (row)

@app.route('/signup', methods = ['GET'])
def signup(): 
        return render_template('signup.html')

@app.route('/signup', methods = ['POST'])  
def signup_post():
    
    conn_string = 'postgresql://Ryan:root@localhost:5432/postgres'
    db = create_engine(conn_string)
    conn = db.connect()
    conn = psycopg2.connect(conn_string)
    c = conn.cursor()
    
    c.execute('SELECT userid FROM users ORDER BY userid DESC LIMIT 1')
    result = c.fetchall()
    
    c.execute('SELECT username FROM users')
    usernameval = c.fetchall()
    usernameset = list(chain.from_iterable(usernameval))

    if result:
        intresult = result[0]
        intintresult = int(intresult[0])
        userid = intintresult + 1
    else:
        userid = 1
        
    if request.method == 'POST':
            firstname = request.form["firstname"]
            lastname = request.form["lastname"]
            email = request.form["email"]
            username = request.form["username"]
            pass_word = request.form["pass_word"]
            entry = Users(userid, firstname, lastname, email, username, pass_word=generate_password_hash(pass_word, method='sha256'))
                         
            
            if username in usernameset:
                 flash ("username already exists, please enter a unique email")
                 return redirect(url_for('signup'))
             
            else:
                print (username, usernameval, usernameset)
                dbat.session.add(entry)
                dbat.session.commit()  
                dbat.create_all() 
                return redirect(url_for('signup'))             
  
            # if this returns a user, then the email already exists in database       

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods = ['POST'])
def login_post():
    username = request.form.get('username')
    pass_word = request.form.get('pass_word')
    # remember = True 

    user = Users.query.filter_by(username=username).first()
    
    if not user or not check_password_hash(user.pass_word, pass_word):
        flash('Please check your login details and try again.')
        return redirect(url_for('login'))
    
    # if not user:
    #     return redirect(url_for('login'))
    

    login_user(user)

    

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    
         # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login')) 