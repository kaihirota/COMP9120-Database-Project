#!/usr/bin/env python3
import psycopg2
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
    with conn.cursor() as cursor:
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

    conn.close()

    return userInfo


def findUserIssues(user_id):
    '''
    List all the user associated issues in the database for a given user
    See assignment description for how to load user associated issues based on the user id (user_id)
    '''
    conn = openConnection()
    with conn.cursor() as cursor:

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
            'issue_id': str(row[0]),
            'title': row[1],
            'creator': row[2],
            'resolver': row[3],
            'verifier': row[4],
            'description': row[5]
        } for row in issue_db]

    conn.close()

    return issue


def findIssueBasedOnExpressionSearchOnTitle(searchString):
    '''
    Find the associated issues for the user with the given userId (user_id)
    based on the searchString provided as the parameter, and based on the
    assignment description
    '''
    conn = openConnection()
    with conn.cursor() as cursor:

        query = """
            SELECT issue.issue_id AS issue_id
                , issue.title AS title
                , c.username AS creator
                , r.username AS resolver
                , v.username AS verifier
                , issue.description AS description
            FROM A3_ISSUE AS issue
            JOIN A3_USER AS c ON issue.creator = c.user_id
            LEFT JOIN A3_USER AS r ON issue.resolver = r.user_id
            LEFT JOIN A3_USER AS v ON issue.verifier = v.user_id
            WHERE title LIKE %s
            -- AND %%s in (issue.creator, issue.resolver, issue.verifier)
            -- this is where we would check that the issue is related to the
            -- user. (the %% would be only one percent sign - it needs to be
            -- escaped as otherwise psycopg2 would try to insert an extra
            -- argument (that doesnt exist))
            ORDER BY title
        """

        # if not re.search('^%.*%$', searchString):
        searchString = f'%{searchString}%'

        # this is where we would pass the user_id to ensure it is related to this user.
        cursor.execute(query, (searchString,))  # user_id))
        issue_db = list(cursor.fetchall())

        issue = [{
            'issue_id': str(row[0]),
            'title': row[1],
            'creator': row[2],
            'resolver': row[3],
            'verifier': row[4],
            'description': row[5]
        } for row in issue_db]

    conn.close()

    return issue


def addIssue(title, creator, resolver, verifier, description):
    """
    Insert a new issue to database

    returns:
        status: True if insert successful, else False
    """

    query = """
        INSERT INTO A3_ISSUE (title, creator, resolver, verifier, description)
        VALUES (%s, get_uid(%s), get_uid(%s), get_uid(%s), %s)
    """

    status = True

    conn = openConnection()
    with conn.cursor() as cursor:

        try:
            cursor.execute(query,
                           [title, creator, resolver, verifier, description])
        except psycopg2.errors.RaiseException:
            status = False

        if not status or cursor.rowcount == 0:
            status = False

    if status is True:
        conn.commit()
    else:
        conn.rollback()

    conn.close()

    return status


def updateIssue(title, creator, resolver, verifier, description, issue_id):
    """
    Update the details of an issue having the provided issue_id with the values
    provided as parameters

    returns:
        status: True if update was successful, else False
    """

    query = """
        UPDATE A3_ISSUE
        SET title = %s,
            creator = get_uid(%s),
            resolver = get_uid(%s),
            verifier = get_uid(%s),
            description = %s
        WHERE issue_id = %s
    """
    data = [title, creator, resolver, verifier, description, issue_id]

    conn = openConnection()

    status = True
    with conn.cursor() as cursor:

        try:
            cursor.execute(query, data)
        except:
            conn.rollback()
            return False

        if cursor.rowcount == 0:
            conn.rollback()
            return False

    conn.commit()
    conn.close()

    return True
