#!/usr/bin/env python3
import os
import psycopg2
import re
from psycopg2 import sql

#####################################################
##  Database Connect
#####################################################

'''
Connects to the database using the connection string
'''
def openConnection():
# connection parameters - ENTER YOUR LOGIN AND PASSWORD HERE
    database = 'test'
    user = 'Kai'
    password = os.getenv('DBPW')
    host = 'localhost'

    # Create a connection to the database
    conn = None
    try:
        # Parses the config file and connects using the connect string
        conn = psycopg2.connect(database=database,
                                    user=user,
                                    password=password,
                                    host=host)
    except psycopg2.Error as sqle:
        print("psycopg2.Error : " + sqle.pgerror)

    # return the connection to use
    return conn

def checkUserCredentials(userName):
    '''
    List all the user associated issues in the database for a given user
    See assignment description for how to load user associated issues based on the user id (user_id)
    '''

    conn = openConnection()
    cursor = conn.cursor()

    query = """
        SELECT user_id, username, firstname, lastname
        FROM A3_USER
        WHERE username = %s
    """
    cursor.execute(query, (userName,))
    userInfo = list(cursor.fetchone())

    cursor.close()
    conn.close()

    return userInfo

def findUserIssues(user_id):
    '''
    List all the user associated issues in the database for a given user
    See assignment description for how to load user associated issues based on the user id (user_id)
    '''
    conn = openConnection()
    cursor = conn.cursor()

    query = """
        SELECT issue_id, title, creator, resolver, verifier, description
        FROM A3_ISSUE
        WHERE creator = %s
    """

    cursor.execute(query, (user_id,))
    issue_db = list(cursor.fetchall())

    issue = [{
        'issue_id': row[0],
        'title': row[1],
        'creator': row[2],
        'resolver': row[3],
        'verifier': row[4],
        'description': row[5]
    } for row in issue_db]

    cursor.close()
    conn.close()

    return issue

def findIssueBasedOnExpressionSearchOnTitle(searchString):
    '''
    Find the associated issues for the user with the given userId (user_id) based on the searchString provided as the parameter, and based on the assignment description
    '''
    conn = openConnection()
    cursor = conn.cursor()

    #TODO: this is case sensitive. leave it as is? or make it insensitive
    query = """
        SELECT issue_id, title, creator, resolver, verifier, description
        FROM A3_ISSUE
        WHERE title LIKE %s
    """

    if not re.search('^%.*%$', searchString):
        searchString = f'%{searchString}%'

    cursor.execute(query, (searchString,))
    issue_db = list(cursor.fetchall())

    issue = [{
        'issue_id': row[0],
        'title': row[1],
        'creator': row[2],
        'resolver': row[3],
        'verifier': row[4],
        'description': row[5]
    } for row in issue_db]

    cursor.close()
    conn.close()

    return issue

#####################################################
##  Issue (new_issue, get all, get details)
#####################################################
def addIssue(title, creator, resolver, verifier, description):
    """
    Insert a new issue to database

    returns:
        status: True if insert successful, else False
    """
    #TODO: catch errors

    conn = openConnection()
    cursor = conn.cursor()

    query = """
        INSERT INTO A3_ISSUE (title, creator, resolver, verifier, description) VALUES (%s, %s, %s, %s, %s)
    """

    try:
        cursor.execute(query, [title, creator, resolver, verifier, description])
        status = True

    except:
        status = False

    finally:
        if status == True:
            conn.commit()

        cursor.close()
        conn.close()

        return status

def updateIssue(issue_id, title, creator, resolver, verifier, description):
    """
    Update the details of an issue having the provided issue_id with the values provided as parameters

    returns:
        status: True if update was successful, else False
    """

    # return False if adding was unsuccessful
    # return True if adding was successful
    # return True


title = 'Test title'
description = 'test description',
creator = 3
resolver = 3
verifier = 4
status = addIssue(title, creator, resolver, verifier, description)
print(status)
