#!/usr/bin/env python3
import os
import psycopg2
from psycopg2 import sql
import re
import json


def openConnection():
    # connection parameters - ENTER YOUR LOGIN AND PASSWORD HERE
    with open('credentials.json') as f:
        creds = json.load(f)

    # create a connection to the database
    conn = None
    try:
        # Parses the config file and connects using the connect string
        conn = psycopg2.connect(**creds)
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
    userInfo = cursor.fetchone()
    if userInfo is None:
        return None
    userInfo = list(userInfo)

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
        SELECT issue.issue_id
            , issue.title
            , c.username AS creator
            , r.username AS resolver
            , v.username AS verifier
            , issue.description
        FROM A3_ISSUE AS issue
        JOIN A3_USER AS c ON issue.creator = c.user_id
        LEFT JOIN A3_USER AS r ON issue.resolver = r.user_id
        LEFT JOIN A3_USER AS v ON issue.verifier = v.user_id
        WHERE %s in (creator, resolver, verifier)
        ORDER BY issue.title
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
    Find the associated issues for the user with the given userId (user_id)
    based on the searchString provided as the parameter, and based on the
    assignment description
    '''
    conn = openConnection()
    cursor = conn.cursor()

    # TODO: this is case sensitive. leave it as is? or make it insensitive
    query = """
        SELECT issue_id, title, creator, resolver, verifier, description
        FROM A3_ISSUE
        WHERE title LIKE %s
        ORDER BY title
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


def addIssue(title, creator, resolver, verifier, description):
    """
    Insert a new issue to database

    returns:
        status: True if insert successful, else False
    """
    # TODO: catch errors

    conn = openConnection()
    cursor = conn.cursor()

    query = """
        INSERT INTO A3_ISSUE (title, creator, resolver, verifier, description) VALUES (%s, %s, %s, %s, %s)
    """

    cursor.execute(query, [title, creator, resolver, verifier, description])

    if cursor.rowcount > 0:
        status = True
    else:
        status = False

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

    conn = openConnection()
    cursor = conn.cursor()

    query = """
        UPDATE A3_ISSUE
        SET title = %s,
            creator = %s,
            resolver = %s,
            verifier = %s,
            description = %s
        WHERE issue_id = %s
    """
    data = [title, creator, resolver, verifier, description, issue_id]

    cursor.execute(query, data)

    if cursor.rowcount > 0:
        status = True
    else:
        status = False

    if status == True:
        conn.commit()

    cursor.close()
    conn.close()

    return status


title = 'Test title'
description = 'test description',
creator = 3
resolver = None
verifier = None
status = addIssue(title, creator, resolver, verifier, description)
print(status)

# issue_id = 300
# title = 'updated title'
# description = 'updated description',
# creator = 3
# resolver = 3
# verifier = 4
# status = updateIssue(issue_id, title, creator, resolver, verifier, description)
# print(status)
