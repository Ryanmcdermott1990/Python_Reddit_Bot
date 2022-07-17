![Example 1](https://github.com/Ryanmcdermott1990/redditBot/blob/main/Examples/login.gif)

#+++++#-----#+++++#-----#+++++#-----#+++++#-----#+++++#-----#+++++#

![Example 2](https://github.com/Ryanmcdermott1990/redditBot/blob/main/Examples/Python_Data.gif)

#+++++#-----#+++++#-----#+++++#-----#+++++#-----#+++++#-----#+++++#

![Example 2](https://github.com/Ryanmcdermott1990/redditBot/blob/main/Examples/signup.gif)

# Python - Reddit Bot
Through this project I learned how to use Flask, a very robust and easy to use Python backend framework that allows for defining routes, rendering templated inforamtion in the front-end and even has a login manager to make logging in and out your users safe, robust and simple to configure / refactor.   

The main points that I learned in this project were

- Using Python to make a call to an external API (Reddit) using PRAW, the Python Reddit API Wrapper 
- Taking values fethed from the API and passing them to a Postgres database 
- Passing values from the backend to the front end using Flask routes and templating engine 
- Using ChartJS in the front end to create dynamic charts using data fetched from the Reddit API 
- Creating a model for users in Python to store and use user details to signup and login users 
- Learning how to hash passwords and how to compare the hashed result to authenticate using Flask login 

Things I can improve on this app are;

- Code Management 
In the next version of this app I will be refactoring the Python and splitting it up in to seperate files. This wasn't done in this MVP as the purpose of this project was to get familiar with Python Flask and as it was my first experience in authentication with a full stack app, I was learning as I was going along. Next time more time will be spent on the planning of the architecture of the application

- Code Resusabillty
This goes hand in hand with Code Management, there are some parts of the application which could and should have been wrapped in functions to reduce code and make the app easier to refactor. 



# How To Run the App on Your Local Machine
After cloning the repo to your local machine, cd into the project directory folder and then execute the following command

### `FLASK_APP=main.py flask run`

This will run the app on localhost:5000, make sure you navigate to /signup route to create your first user. 

This assumes you have insalled the following dependencies on your machine you can pip install each of these, (Python is required for this)

- Flask 
- Flask login 
- Pyscopg 
- SQL Alchemy 
- Pandas
- werkzeug
- Praw



