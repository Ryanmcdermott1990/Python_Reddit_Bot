import praw

#This file is used to store all configuration information 
#Look up how to create a Reddit App on how to get each of these details

reddit = praw.Reddit(
    client_id="{INSERT CLIENT ID}",
    client_secret="{INSERT CLIENT SECRET}",
    user_agent="{INSERT USER AGENT}", 
    
)
