import json
from psycopg2 import connect

with open(f'SQL_CREDENTIALS.json') as creds_file:
    sql_creds = json.load(creds_file)


def test_connection():
    conn = connect(database='comp9120_a2', **sql_creds)

    if not conn:
        print('connection failed')
    else:
        return conn


conn = test_connection()
cursor = conn.cursor()
sql = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
"""

cursor.execute(sql)
for table in cursor.fetchall():
    print(table)
