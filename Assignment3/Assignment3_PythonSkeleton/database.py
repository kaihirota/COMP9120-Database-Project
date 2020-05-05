#!/usr/bin/env python3
import psycopg2

#####################################################
##  Database Connect
#####################################################

'''
Connects to the database using the connection string
'''
def openConnection():
# connection parameters - ENTER YOUR LOGIN AND PASSWORD HERE
    userid = "y20s1c9120_unikey"
    passwd = "password"
    myHost = "soit-db-pro-2.ucc.usyd.edu.au"

    # Create a connection to the database
    conn = None
    try:
        # Parses the config file and connects using the connect string
        conn = psycopg2.connect(database=userid,
                                    user=userid,
                                    password=passwd,
                                    host=myHost)
    except psycopg2.Error as sqle:
        print("psycopg2.Error : " + sqle.pgerror)
    
    # return the connection to use
    return conn

'''
List all the user associated issues in the database for a given user 
See assignment description for how to load user associated issues based on the user id (user_id)
'''
def checkUserCredentials(userName):
    # TODO - get user info for user 
    print(userName)

    userInfo = ['2', 'Chris', 'Christopher', 'Smith']

    return userInfo
    
'''
List all the user associated issues in the database for a given user 
See assignment description for how to load user associated issues based on the user id (user_id)
'''
def findUserIssues(user_id):
    # TODO - list all user associated issues from db using sql
    print(user_id)
    issue_db = [
        ['1', 'Division by zero', 'Chris', 'Dave', 'Vlad', 'Division by 0 doesn\'t yield error or infinity as would be expected. Instead it results in -1.'],
        ['2', 'Factorial with addition anomaly', 'Chris', 'Dave', '-', 'No description']
    ]

    issue = [{
        'issue_id': row[0],
        'title': row[1],
        'creator': row[2],
        'resolver': row[3],
        'verifier': row[4],
        'description': row[5]
    } for row in issue_db]

    return issue

'''
Find the associated issues for the user with the given userId (user_id) based on the searchString provided as the parameter, and based on the assignment description
'''
def findIssueBasedOnExpressionSearchOnTitle(searchString):

    # TODO - find necessary issues using sql database based on search input
    print("search string '" + searchString + "'")
    issue_db = [
        ['1', 'Division by zero', 'Chris', 'Dave', 'Vlad', 'Division by 0 doesn\'t yield error or infinity as would be expected. Instead it results in -1.']
    ]

    issue = [{
        'issue_id': row[0],
        'title': row[1],
        'creator': row[2],
        'resolver': row[3],
        'verifier': row[4],
        'description': row[5]
    } for row in issue_db]

    return issue

#####################################################
##  Issue (new_issue, get all, get details)
#####################################################
#Add the details for a new issue to the database - details for new issue provided as parameters
def addIssue(title, creator, resolver, verifier, description):
    # TODO - add an issue
    # Insert a new issue to database
    # return False if adding was unsuccessful 
    # return True if adding was successful

    return True

#Update the details of an issue having the provided issue_id with the values provided as parameters
def updateIssue(issue_id, title, creator, resolver, verifier, description):

    # TODO - update the issue using db

    # return False if adding was unsuccessful 
    # return True if adding was successful
    return True
