import json
from psycopg2 import connect

with open(f'SQL_CREDENTIALS.json') as creds_file:
    sql_creds = json.load(creds_file)


def test_connection():
    connect(database='comp9120_a2', **sql_creds)
