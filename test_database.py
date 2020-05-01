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
from psycopg2.extensions import connection as Connection
from psycopg2.errors import UniqueViolation, NotNullViolation, ForeignKeyViolation, InFailedSqlTransaction
from typing import List, Sequence
import pytest
from datetime import datetime, timedelta

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
        self.connection: Connection = connect(database='comp9120_a2', **sql_creds)

        if not self.connection:
            raise RuntimeError(f'could not connect to db with creds {sql_creds}')

        # clear and recreate database from DDL file
        with open('ddl.sql', 'r') as f:
            ddl = f.read()

        for table in self.tables:
            self.dbexec(self.create_drop_statement(table), msg=f'drop table {table}')
        self.dbexec(ddl, msg='create all tables from ddl')
        self.commit()

    def teardown_method(self):
        print('starting teardown')
        try:
            self.commit()
        except InFailedSqlTransaction:
            pass
        print('committed.')
        for table in self.tables:
            self.dbget_table(table)
            self.dbexec(self.create_drop_statement(table))
        self.commit()
        self.connection.close()

    def commit(self):
        self.connection.commit()

    def dbquery(self,
                sql: str,
                args: Sequence[str] = None,
                msg: str = ''):
        print(msg)
        rv = []
        with self.connection.cursor() as cur:
            cur.execute(sql, args)
            for record in cur:
                rv.append(record)
        return rv

    def dbexec(self, sql: str, args: Sequence[str] = None, msg: str = ''):
        print(msg)
        with self.connection.cursor() as cur:
            cur.execute(sql, args)

    def dbinsert(self, table, columns, values, msg=None):
        if msg is None:
            msg = f'insert row to {table}'
        self.dbexec(self.create_insert_statement(table, columns, values),
                    values,
                    '(' + ','.join(map(repr, values)) + ') ' + msg)

    def dbget_table(self, table, columns=None):
        if columns is None:
            colstr = '*'
        else:
            colstr = f"{','.join(columns)}"
        rv = self.dbquery(f'select {colstr} from {table}', None, f'get table {table}')
        for row in rv:
            print('>', row)
        return rv

    def run_multiple_inserts(self, table, columns, value_error_pairs, commits=True):
        for vals, err in value_error_pairs:
            if err is None:
                self.dbinsert(table, columns, vals)
            else:
                with pytest.raises(err):
                    self.dbinsert(table, columns, vals, msg=f'insert row to {table}, should fail')
            if commits:
                self.commit()

    def test_menu_contains_insert(self):
        # menu gets inserted first, as the 'at least one' constraint is deferred
        menucolumns = 'MenuId', 'Description'
        with pytest.raises(Exception):
            self.dbinsert('menu', menucolumns, (0, 'description'))
            self.commit()

    def test_menuitem_insert(self):
        # TODO this needs menuitem fails
        menucolumns = 'MenuItemId', 'Name', 'Price', 'Description'
        values = [
            # test name not null
            ((0, 'name', 10, 'desc'), None),
        ]
        self.run_multiple_inserts('MenuItem', menucolumns, values)
        columns = 'MenuItemId',
        values = [
            ((0,), None),
            ((0,), Exception),
        ]
        self.run_multiple_inserts('Main', columns, values)
        return
        values = [
            ((1,), None),
            ((0,), Exception),
            ((1,), Exception),
        ]
        self.run_multiple_inserts('Side', columns, values)
        values = [
            ((2,), None),
            ((0,), Exception),
            ((1,), Exception),
            ((2,), Exception),
        ]
        self.run_multiple_inserts('Side', columns, values)
        return
        values = [
            # test name not null
            ((0, None, 10, 'desc'), NotNullViolation),
            # test name and price not unique
            ((0, 'name', 10, 'desc'), None),
            ((1, 'name', 10, 'desc'), None),
            # test name length
            ((3, 'a' * 30, 10, 'desc'), None),
            ((4, 'a' * 400, 10, 'desc'), Exception),

            # test id not null
            ((None, 'name', 10, 'desc'), NotNullViolation),
            # test id is unique
            ((3, 'name', 10, 'desc'), UniqueViolation),

            # test price not null
            ((5, 'name', None, 'desc'), NotNullViolation),
            # test price is number
            ((5, 'name', 'abc', 'desc'), Exception),
            # test price cant have .001 cents
            ((5, 'name', 10.001, 'desc'), None),
            # test price can have cents
            # ((5, 'name', 10.30, 'desc'), Exception),

            # test description can be null
            ((6, 'name', 10, 'desc'), None),

            # test isa is one of ('Main', 'Side', 'Dessert')
            ((7, 'name', 10, 'desc'), None),
            ((8, 'name', 10, 'desc'), None),
            ((9, 'name', 10, 'desc'), None),
            ((10, 'name', 10, 'desc'), Exception),
            ((10, 'name', 10, 'desc'), Exception),
            ((10, 'name', 10, 'desc'), Exception),
            ((10, 'name', 10, 'desc'), Exception),
        ]
        self.run_multiple_inserts('MenuItem', menucolumns, values)

        # item 5 must not retain the extra decimal
        menuitems = self.dbget_table('MenuItem', columns=('menuItemId', 'price'))
        assert list(filter(lambda x: x[0] == 5, menuitems))[0][1] == 10

    def test_customer_insert(self):
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
            # TODO ((2, '4' * 9, 'john', 'smith', '3 street street'), Exception),
            ((2, '4' * 10, 'john', 'smith', '3 street street'), None),
            # test mobileno is a number
            # TODO ((3, False, 'john', 'smith', '3 street street'), Exception),
            # TODO ((3, 'a' * 10, 'john', 'smith', '3 street street'), Exception),

            # test firstname and lastname not null
            ((3, '0488888888', None, 'smith', '3 street street'), Exception),
            ((3, '0488888888', 'john', None, '3 street street'), Exception),

            # test address cant be null
            ((3, '0488888888', 'john', 'smith', None), Exception),
        ]
        self.run_multiple_inserts('Customer', columns, values)

    def test_staff_insert(self):
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

    def test_courier_insert(self):
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
            # TODO ((5, 'name', 'address', '8' * 9), Exception),
            ((5, 'name', 'address', '8' * 11), Exception),
            ((5, 'name', 'address', '8' * 10), None),
            # test mobile is a number
            # TODO ((6, 'name', 'address', 'a' * 10), Exception),
        ]
        self.run_multiple_inserts('Courier', columns, values)

    def test_delivery_insert(self):
        columns = 'DeliveryId', 'TimeReady', 'TimeDelivered', 'CourierId'
        values = [
            ((0, datetime(2020, 1, 1, 1, 1, 29), datetime(2020, 1, 1, 1, 2, 0), 0), Exception),
            ((None, datetime(2020, 1, 1, 1, 1, 29), datetime(2020, 1, 1, 1, 2, 0), 0), Exception),
        ]
        self.run_multiple_inserts('Delivery', columns, values)
        # will only pass if test_courier_insert passes.
        self.test_courier_insert()
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
        self.run_multiple_inserts('Delivery', columns, values)

    def TODO_order_insert(self):
        # all should fail before customer
        columns = 'OrderId', 'DateTime', 'TotalCharge', 'CustomerId', 'DeliveryId', 'StaffId'
        d = datetime(2020, 1, 1, 1, 1, 0)
        dp = d + timedelta(seconds=20)
        values = [
            ((0, d, 20, 0, 0, 0), Exception),
        ]
        self.run_multiple_inserts('order', columns, values)
        self.test_customer_insert()

        # database should now contain these customers
        # 0, 'john', 'smith', '3 street street', '0488888888'
        # 1, 'john', 'smith', '3 street street', '0488888888'
        # 2, 'john', 'smith', '3 street street', '4444444444'

        # should fail again as the other foreign keys must be constrained
        self.run_multiple_inserts('order', columns, values)

        self.test_staff_insert()
        # should /still/ fail as the other foreign key must be constrained
        self.run_multiple_inserts('order', columns, values)

        self.test_delivery_insert()
        values = [
            ((0, d, 20, 0, 0, 0), None),

            # primary keys must be only 'OrderId' and 'CustomerId'
            ((0, d, 20, 0, 1, 0), UniqueViolation),
            ((0, d, 20, 0, 0, 1), UniqueViolation),
            ((1, d, 20, 0, 0, 0), None),
            ((0, d, 20, 1, 0, 0), None),

            # not null on all foreign keys
            ((1, d, 20, None, 0, 0), NotNullViolation),
            ((1, d, 20, 0, None, 0), NotNullViolation),
            ((1, d, 20, 0, 0, None), NotNullViolation),

            # all foreign keys must exist
            ((1, d, 20, 20, 0, 0), ForeignKeyViolation),
            ((1, d, 20, 0, 20, 0), ForeignKeyViolation),
            ((1, d, 20, 0, 0, 20), ForeignKeyViolation),
        ]
        self.run_multiple_inserts('"Order"', columns, values)

    def TODO_orderitem_insert(self):
        columns = 'OrderItemId', 'OrderId', 'CustomerId', 'Quantity', 'Charge'
        self.test_menuitem_insert()
        values = [
        ]

