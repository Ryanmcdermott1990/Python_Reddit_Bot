from cmath import e
from logging import error
from pkgutil import iter_modules
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

# Global variables, limit
limitvar = 10
reddit = config.reddit
c = connection.c
db = connection.db
subredd = "askreddit"


#Config variables, these are to be moved to the config.py for better code management
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = '{dbname}://{username}:{password}@{localhost:port}/{postgres}'
app.config['SECRET_KEY'] = '{Secret Key}'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


#init the db with SQL alchemy and initialise the app
dbat = SQLAlchemy(app)
dbat.init_app(app)


#Assign login manager to new instance of Login manager consutructor
#Initialise the app with the login manager instance
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


# This will load the user's details from the session 
# Since the user_id is just the primary key of our user table, use it in the query for the user
@login_manager.user_loader
def load_user(userid):
    return Users.query.get(userid)


#The user model consists of the following values 
#This should be moved to a models directory for better code management

class Users (UserMixin, dbat.Model):
    userid = dbat.Column(dbat.Integer, primary_key=True,
    autoincrement=True, nullable=False)
    firstname = dbat.Column(dbat.String(120), unique=False, nullable=False)
    lastname = dbat.Column(dbat.String(120), unique=False, nullable=False)
    email = dbat.Column(dbat.String(120), unique=True, nullable=False)
    username = dbat.Column(dbat.String(120), nullable=False)
    pass_word = dbat.Column(dbat.String(120), nullable=False)

    def get_id(self):
        return (self.userid)
    #Bind the fields from the uesr model to Self in order to initialise the user model with Flask Login
    def __init__(self, userid, firstname, lastname, email, username, pass_word):
        self.userid = userid
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.username = username
        self.pass_word = pass_word

#Making the call to Reddit's API using PRAW
def callApi(limitvar, subredd):
    subreddit = reddit.subreddit(subredd)
    df = pd.DataFrame([vars(post) for post in subreddit.hot(limit=limitvar)])
    df = df[["id", "title", "score", "num_comments", "created_utc", "url"]]
    df['created_utc'] = pd.to_datetime(df['created_utc'], unit='s')
    df.to_sql('posts', db, if_exists='replace', index=False)
    # csv_file = "./reddit.csv"
    # df.to_csv(csv_file, index=False, encoding='utf-8')

#This is where all the routes are kept, ideally this should be in a seperate routes directory
#Tihs is the index route 
@app.route('/index', methods=['POST', 'GET'])
@login_required
def index():
    #This passes the value of an input on the frront end to the limit variable that is passed to the CallApi funciton, (above) 
    if request.method == 'POST':
        limitvar = int(request.form['records'])
        subredd = request.form['Sub-reddit']
        callApi(limitvar, subredd)
    subr = []
    #Iterate through the array of subreddits and append that to an array list that is passed in to the front end to be selected in a dropdown 
    for subreddit in reddit.subreddits.default(limit=10):
        subr.append(subreddit.display_name)
    return render_template('index.html', subr=subr)


#The data route is used to render the data that is grabbed from the API in to a table in the front end
@app.route('/data')
#Login is required to access this conent so the @ syntax dressing is used 
@login_required
#This function defines the db parameters, this should be wrapped in a function for better code readability and reusability 
def data():
    conn_string = '{dbname}://{username}:{password}@{localhost:port}/{postgres}'
    db = create_engine(conn_string)
    conn = db.connect()
    conn = psycopg2.connect(conn_string)
    c = conn.cursor()
    
    #Once the cursor object is assigned to the variable c, we can use it to executre queries on the database
    #These queries should be assigned as seperate variables for better code readabiity and maintainability
    c.execute('SELECT * FROM users')
    result = c.fetchall()
    print(result)
    c.execute('CREATE TABLE IF NOT EXISTS posts (id text, title text, score integer, num_comments integer, created_utc date, url text)')
    c.execute('''  
SELECT * FROM posts
          ''')
    data1 = c.fetchall()
    c.execute('''  
SELECT id, num_comments FROM posts GROUP BY id, num_comments LIMIT 10
          ''')
    data = c.fetchall()
    c.execute('''
  SELECT * FROM posts ORDER BY created_utc LIMIT 10         
  ''')
    #Grabbing all of the labels that are to be passed to a canvas element and charted with Chart JS
    labels = c.fetchall()
    #The connection is closed so as to stop the database connection hanging 
    connection.closeConnection()
    return render_template('data.html', data1=data1, labels=labels, data=data, len=len(labels))

#This is the signup route to render the page 
@app.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')

#This is the signup route to execute the query on the db
@app.route('/signup', methods=['POST'])
def signup_post():

    #Database connection, should be wrapped in a funciton and called 
    conn_string = '{dbname}://{username}:{password}@{localhost:port}/{postgres}'
    db = create_engine(conn_string)
    conn = db.connect()
    conn = psycopg2.connect(conn_string)
    c = conn.cursor()

    #This is to assign an id to each of the users that are added to the database 
    c.execute('SELECT userid FROM users ORDER BY userid DESC LIMIT 1')
    result = c.fetchall()
    
    c.execute('SELECT username FROM users')
    usernameval = c.fetchall()
    usernameset = list(chain.from_iterable(usernameval))

    #If there is a user id fetched from the db, then asssign the first index in the array of result to intresult, parse this to an int value
    #Set the userid as this + 1 
    #If there isn't a user id in the db, then set the default as 1
    if result:
        intresult = result[0]
        intintresult = int(intresult[0])
        userid = intintresult + 1
    else:
        userid = 1
        
    #Taking user data from the HTML form in the front end and passing these values to the db, making sure to hash the password using a sha256 encryption method
    if request.method == 'POST':
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        email = request.form["email"]
        username = request.form["username"]
        pass_word = request.form["pass_word"]
        entry = Users(userid, firstname, lastname, email, username,
                      pass_word=generate_password_hash(pass_word, method='sha256'))

        #If the username already exists in the db, then display a message to the userm then redirect to the signup page
        if username in usernameset:
            flash("Username already exists, please enter a unique username!")
            return redirect(url_for('signup'))
        #Otherwise post this information to the database and save the users login credentials
        else:
            print(username, usernameval, usernameset)
            dbat.session.add(entry)
            dbat.session.commit()
            dbat.create_all()
            return redirect(url_for('signup'))

   
#Route for rendering login information
@app.route('/login')
def login():
    return render_template('login.html')

#This route takes the information posted from the HTML form in the front end
#I will most likely in future also set remember to True or False to remember your login session with a checkbox or something like that
@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    pass_word = request.form.get('pass_word')

    # Check if the user actually exists
    # Take the user-supplied password, hash it, and compare it to the hashed password in the database
    # if the user doesn't exist or password is wrong, reload the page
    # if the above check passes, then we know the user has the right credentials
    user = Users.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.pass_word, pass_word):
        flash('Please check your login details and try again.')
        return redirect(url_for('login'))

    login_user(user)
    return redirect(url_for('index'))

#Logout route, Flask makes this very easy, you just need to call the logout_user() method, this then redirects the user to the login page
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
