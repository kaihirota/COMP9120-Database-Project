# 1. Fields in a tuple related to dates and times should always have values.
# 2. All fields in a tuple relating to details about a name (eg: Menu Item Name, First Name, etc)
#    should always have a value.
# 3. The total charge of an order, the quantity and charge for an order item, and the price for a
#    menu item should always have values.
# 4. Customers must have a specified mobile number.
# 5. The TimeDelivered time/date should always be after TimeReady.


# please use the same names as in the ER diagram for naming tables and attributes)
import json
import re
from psycopg2 import connect
from psycopg2.errors import UniqueViolation, NotNullViolation
from typing import List, Sequence
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
        print(msg)
        rv = []
        with self.connection:
            with self.connection.cursor() as cur:
                cur.execute(sql, args)
                for record in cur:
                    rv.append(record)
        return rv

    def dbexec(self, sql: str, args: Sequence[str] = None, msg: str = ''):
        print(msg)
        with self.connection:
            with self.connection.cursor() as cur:
                cur.execute(sql, args)

    def dbinsert(self, table, columns, values, msg=None):
        if msg is None:
            msg = 'insert row'
        self.dbexec(self.create_insert_statement(table, columns, values),
                    values,
                    '(' + ','.join(map(repr, values)) + ') ' + msg)

    def run_multiple_inserts(self, table, columns, value_error_pairs):
        for vals, err in value_error_pairs:
            if err is None:
                self.dbinsert(table, columns, vals)
            else:
                with pytest.raises(err):
                    self.dbinsert(table, columns, vals, msg='insert row, should fail')



    def test_insert_staff_correct(self):
        values = '31', 'manager', 'joe'
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

    def test_insert_courier(self):
        columns = 'CourierId', 'Name', 'Address', 'MobileNumber'
        values = [
            # values , error
            (('1', 'abdul', '35 street street', '0487888888'), None),
            (('1', 'james', '35 street street', '0485639676'), UniqueViolation),
            (('2', 'abdul', '35 street street', '0475749507'), None),
            (('3', None, '35 street street', '0475869403'), NotNullViolation),
            (('3', 'null', '35 street street', 475869403), Exception)
        ]
        self.run_multiple_inserts('courier', columns, values)


