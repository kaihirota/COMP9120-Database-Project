import json
import sys
import re
from psycopg2 import connect
from psycopg2.extensions import connection as Connection
from typing import List, Sequence, Generator
import pytest

Value = str



class Test_db_constraints:
    @staticmethod
    def create_insert_statement(table, columns, values):
        insert_smt = '''INSERT INTO {table}{columns} VALUES {values}'''
        rv = insert_smt.format(
            table=table,
            columns=f'({",".join(columns)})' if columns is not None else '',
            values='(' + ','.join(['%s'] * len(values)) + ')'
        )
        return rv

    @staticmethod
    def create_drop_statement(table):
        return f'drop table if exists {table} cascade;'

    def setup_method(self):
        # (primitively) parse tables from source
        tables: List[str] = []
        with open('ddl.sql', 'r') as f:
            for line in f.readlines():
                if 'CREATE TABLE' in line.upper():
                    match = re.search(r'.*?create table ([\w"]+)', line, re.IGNORECASE)
                    if match:
                        tables.append(match.group(1))
                    else:
                        raise ValueError(f'Could not parse line in ddl.sql: {line}')
        self.tables = tables

        # connect to database
        with open(f'SQL_CREDENTIALS.json') as creds_file:
            sql_creds = json.load(creds_file)
        self.connection = connect(database='comp9120_a2', **sql_creds)
        if not self.connection:
            raise RuntimeError(f'could not connect to db with creds {sql_creds}')

        # clear and recreate database from DDL file
        with open('ddl.sql', 'r') as f:
            ddl = f.read()

        for table in self.tables:
            self.dbexec(self.create_drop_statement(table), msg=f'drop table {table}')
        self.dbexec(ddl, msg='create all tables from ddl')

    def teardown_method(self):
        self.connection.close()

    def dbquery(self,
                sql: str,
                args: Sequence[str] = None,
                msg: str = ''):
        print(msg, 'starting...')
        rv = []
        with self.connection:
            with self.connection.cursor() as cur:
                cur.execute(sql, args)
                for record in cur:
                    rv.append(record)
        return rv

    def dbexec(self, sql: str, args: Sequence[str] = None, msg: str = ''):
        print(msg, 'starting...')
        with self.connection:
            with self.connection.cursor() as cur:
                cur.execute(sql, args)

    def test_insert_staff_correct(self):
        values = ('31', 'manager', 'joe')
        qry = self.create_insert_statement('Staff',
                                           ('staffid', 'position', 'name'),
                                           values)
        self.dbexec(qry, values, 'insert staff member')

    def test_insert_staff_incorrect(self):
        values = ('31', 'manager', 'joe', 'briggs')
        qry = self.create_insert_statement('Staff',
                                           ('staffid', 'position', 'firstname', 'lastname'),
                                           values)
        with pytest.raises(Exception):
            self.dbquery(qry, values, 'insert staff member incorrectly')
