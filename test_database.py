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
from datetime import datetime

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
        self.connection.commit()
        for table in self.tables:
            rv = self.dbquery(f'select * from {table}',
                              msg=f'select * from {table}:')
            for row in rv:
                print(row)
            self.dbexec(self.create_drop_statement(table))
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

    def dbget_table(self, table):
        return self.dbexec(f'select * from {table}', f'get table {table}')

    def run_multiple_inserts(self, table, columns, value_error_pairs):
        for vals, err in value_error_pairs:
            if err is None:
                self.dbinsert(table, columns, vals)
            else:
                with pytest.raises(err):
                    self.dbinsert(table, columns, vals, msg='insert row, should fail')

    def TODO_menu_insert(self):
        # TODO this test needs to be worked out. It is not really acceptable right now.
        # must not allow a menu to be inserted before any menu items that are contained in that menu are inserted. (may change later)
        with pytest.raises(Exception):
            self.dbinsert('menu', ('MenuId', 'Description'), (0, 'desc'))

        # must have at least one menuitem first
        menucolumns = 'MenuItemId', 'Name', 'Price', 'Description', 'IsA'
        values = [
            ((0, 'dish', 31.89, None, 'Main'), None),
            ((1, 'dish', 37.21, 'description', 'Side'), None),
            ((2, 'dish', 37.21, 'description', 'Dessert'), None),
        ]
        self.run_multiple_inserts('MenuItem', menucolumns, values)

        # function so we can test that it works at least one way around
        def insert_menus():
            columns = 'MenuId', 'Description'
            value_error_pairs = [
                ((0, 'this is a short description'), None),
                ((0, 'this is a short description'), Exception),
                ((1, 'this is a longer description, it spans approx 100 characters. bla bla bla bla bla la bla bla bla bla'), None),
                ((1, 'desc'), UniqueViolation),
                ((2, None), None),  # should allow null descriptions
            ]
            self.run_multiple_inserts('menu', columns, value_error_pairs)

        def insert_contains():
            columns = 'MenuId', 'MenuItemId'
            value_error_pairs = [
                ((0, 0), None),
                ((0, 0), Exception),
                ((0, 5), Exception),
                ((2, 0), None),
                ((1, 0), None),
            ]
            self.run_multiple_inserts('Contains', columns, value_error_pairs)

        try:
            insert_menus()
            insert_contains()
        except Exception:
            insert_contains()
            insert_menus()

    def test_menuitem_insert(self):
        menucolumns = 'MenuItemId', 'Name', 'Price', 'Description', 'IsA'
        values = [
            # test name not null
            ((0, None, 10, 'desc', 'Main'), NotNullViolation),
            # test name and price not unique
            ((0, 'name', 10, 'desc', 'Main'), None),
            ((1, 'name', 10, 'desc', 'Main'), None),
            # test name length
            ((3, 'a' * 30, 10, 'desc', 'Main'), None),
            ((4, 'a' * 400, 10, 'desc', 'Main'), Exception),

            # test id not null
            ((None, 'name', 10, 'desc', 'Main'), NotNullViolation),
            # test id is unique
            ((3, 'name', 10, 'desc', 'Main'), UniqueViolation),

            # test price not null
            ((5, 'name', None, 'desc', 'Main'), NotNullViolation),
            # test price is number
            ((5, 'name', 'abc', 'desc', 'Main'), Exception),
            # test price cant have .001 cents
            ((5, 'name', 10.001, 'desc', 'Main'), Exception),
            # test price can have cents
            # ((5, 'name', 10.30, 'desc', 'Main'), Exception),

            # test description can be null
            ((5, 'name', 10, 'desc', 'Main'), None),

            # test isa is one of ('Main', 'Side', 'Dessert')
            ((7, 'name', 10, 'desc', 'Main'), None),
            ((8, 'name', 10, 'desc', 'Side'), None),
            ((9, 'name', 10, 'desc', 'Dessert'), None),
            ((10, 'name', 10, 'desc', 'main'), Exception),
            ((10, 'name', 10, 'desc', 'side'), Exception),
            ((10, 'name', 10, 'desc', 'dessert'), Exception),
            ((10, 'name', 10, 'desc', 'otheritem'), Exception),
        ]
        self.run_multiple_inserts('MenuItem', menucolumns, values)

    def test_customer(self):
        columns = 'CustomerId', 'MobileNo', 'FirstName', 'LastName', 'Address'
        values = [
            ((0, '0488888888', 'john', 'smith', '3 street street'), None),

            # test customerid unique
            ((0, '0488888888', 'john', 'smith', '3 street street'), Exception),
            # test customerid not null
            ((None, '0488888888', 'john', 'smith', '3 street street'), Exception),

            # test mobileno not unique
            ((1, '0488888888', 'john', 'smith', '3 street street'), None),
            # test mobileno not null
            ((2, None, 'john', 'smith', '3 street street'), Exception),
            # test mobileno is the right length
            ((2, '4' * 11, 'john', 'smith', '3 street street'), Exception),
            ((2, '4' * 9, 'john', 'smith', '3 street street'), Exception),
            ((2, '4' * 10, 'john', 'smith', '3 street street'), None),
            # test mobileno is a number
            ((3, False, 'john', 'smith', '3 street street'), Exception),
            ((3, 'a' * 10, 'john', 'smith', '3 street street'), Exception),

            # test firstname and lastname not null
            ((3, '0488888888', None, 'smith', '3 street street'), Exception),
            ((3, '0488888888', 'john', None, '3 street street'), Exception),

            # test address can be null
            ((3, '0488888888', 'john', 'smith', None), None),
        ]
        self.run_multiple_inserts('Customer', columns, values)

    def test_staff(self):
        columns = 'StaffId', 'Position', 'Name'
        values = [
            ((0, 'pos', 'name'), None),

            # staffid is unique
            ((0, 'pos', 'name'), Exception),
            # staffid is not null
            ((None, 'pos', 'name'), Exception),

            # position can be null
            ((1, None, 'name'), None),

            # name is not null
            ((2, 'pos', None), Exception),
        ]
        self.run_multiple_inserts('Staff', columns, values)

    def test_courier(self):
        columns = 'CourierId', 'Name', 'Address', 'Mobile'
        values = [
            ((0, 'name', 'address', '4829574820'), None),

            # test courierid is unique
            ((0, 'name', 'address', '8' * 10), Exception),
            # test courierid not null
            ((None, 'name', 'address', '8' * 10), Exception),

            # test name not null
            ((1, None, 'address', '8' * 10), Exception),
            # test name not unique
            ((1, 'name', 'address', '8' * 10), None),

            # test address can be null
            ((2, 'name', None, '8' * 10), None),
            # test address not unique
            ((3, 'name', 'address', '8' * 10), None),

            # test mobile not unique
            ((4, 'name', 'address', '8' * 10), None),
            # test mobile not null
            ((5, 'name', 'address', None), Exception),
            # test mobile is the right length
            ((5, 'name', 'address', '8' * 9), Exception),
            ((5, 'name', 'address', '8' * 11), Exception),
            ((5, 'name', 'address', '8' * 10), None),
            # test mobile is a number
            ((6, 'name', 'address', 'a' * 10), None),
        ]
        self.run_multiple_inserts('Courier', columns, values)

    def test_delivery(self):
        columns = 'DeliveryId', 'TimeReady', 'TimeDelivered', 'CourierId'
        # will only pass if test_courier passes.
        self.test_courier()
        # values in courier should be:
        # 0, 'name', 'address', '4829574820'
        # 1, 'name', 'address', '8' * 10
        # 2, 'name', None, '8' * 10
        # 3, 'name', 'address', '8' * 10
        # 4, 'name', 'address', '8' * 10
        # 5, 'name', 'address', '8' * 10
        # 6, 'name', 'address', 'a' * 10
        values = [
            ((0, datetime(2020, 1, 1, 1, 1, 29), datetime(2020, 1, 1, 1, 2, 0), 0), None),

            # test deliveryid not null
            ((None, datetime(2020, 1, 1, 1, 1, 29), datetime(2020, 1, 1, 1, 2, 0), 0), NotNullViolation),
            # test deliveryid unique
            ((0, datetime(2020, 1, 1, 1, 1, 29), datetime(2020, 1, 1, 1, 2, 0), 0), UniqueViolation),

            # test timeready not null
            ((1, None, datetime(2020, 1, 1, 1, 2, 0), 0), NotNullViolation),
            # test timeready is datetime
            ((1, 'abc', datetime(2020, 1, 1, 1, 2, 0), 0), Exception),

            # test timedelivered not null
            ((1, datetime(2020, 1, 1, 1, 2, 0), None, 0), NotNullViolation),
            # test timedelivered is datetime
            ((1, datetime(2020, 1, 1, 1, 2, 0), 'abc', 0), Exception),
            # test timedelivered > timeready
            ((1, datetime(2020, 1, 1, 1, 1, 29), datetime(2020, 1, 1, 1, 2, 0), 0), None),
            # test timedelivered not < timeready
            ((2, datetime(2020, 1, 1, 1, 5, 29), datetime(2020, 1, 1, 1, 2, 0), 0), Exception),

            # test courierid exists in courier
            ((2, datetime(2020, 1, 1, 1, 5, 29), datetime(2020, 1, 1, 1, 2, 0), 10), Exception),
        ]
        self.run_multiple_inserts('Staff', columns, values)
