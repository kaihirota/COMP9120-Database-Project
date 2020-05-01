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
        try:
            self.commit()
        except InFailedSqlTransaction:
            pass
        for table in self.tables:
            self.dbget_table(table)
            self.dbexec(self.create_drop_statement(table))
        self.commit()
        self.connection.close()

    def commit(self):
        try:
            self.connection.commit()
        except Exception:
            raise

    def rollback(self):
        try:
            self.connection.rollback()
        except:
            raise

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

    def run_multiple_inserts(self, table, columns, value_error_pairs):
        for vals, err in value_error_pairs:
            if err is None:
                self.dbinsert(table, columns, vals)
            else:
                with pytest.raises(err):
                    self.dbinsert(table, columns, vals, msg=f'insert row to {table}, should fail')
            self.commit()

    def test_menu_contains_insert(self):
        # menu contains at least one menuitem on commit
        menucolumns = 'MenuId', 'Description'
        self.dbinsert('menu', menucolumns, (0, 'description'))
        with pytest.raises(Exception):
            self.commit()
        self.rollback()
        # insert menuitem first
        self.dbinsert('Main', None, (8,))
        self.dbinsert('MenuItem', ('MenuItemId', 'Name', 'Price'), (8, 'name', 20))
        self.commit()

        # insert menu that contains that menuitem
        self.dbinsert('contains', ('menuid', 'menuitemid'), (0, 8))
        self.dbinsert('Menu', menucolumns, (0, 'desc'))
        self.commit()

        # insert menu that contains that menuitem (other way around)
        self.dbinsert('Menu', menucolumns, (1, 'desc'))
        self.dbinsert('contains', ('menuid', 'menuitemid'), (1, 8))
        self.commit()

    def test_menuitem_heirarchy(self):
        menuitemcols = 'MenuItemId', 'Name', 'Price', 'Description'
        types = 'Main', 'Side', 'Dessert'

        icount = 0
        # allows insertion of menuitem first
        self.dbinsert('MenuItem',
                      menuitemcols,
                      (0, 'name', 20, 'desc'))
        with pytest.raises(Exception):
            self.commit()

        for t in types:
            self.dbinsert(t, ('MenuItemId',), (0,))
            with pytest.raises(Exception):
                self.commit()

            # insert a row MenuItem First
            self.dbinsert('MenuItem',
                          menuitemcols,
                          (icount, f'name {icount}', 20, f'desc {icount}'))
            self.dbinsert(t, ('MenuItemId',), (icount,))
            self.commit()
            icount += 1

            self.dbinsert(t, ('MenuItemId',), (icount,))
            self.dbinsert('MenuItem',
                          menuitemcols,
                          (icount, f'name {icount}', 20, f'desc {icount}'))
            self.commit()
            icount += 1

        # output now looks like this:
        # get table MenuItem
        # > (0, 'name 0', Decimal('20.00'), 'desc 0')
        # > (1, 'name 1', Decimal('20.00'), 'desc 1')
        # > (2, 'name 2', Decimal('20.00'), 'desc 2')
        # > (3, 'name 3', Decimal('20.00'), 'desc 3')
        # > (4, 'name 4', Decimal('20.00'), 'desc 4')
        # > (5, 'name 5', Decimal('20.00'), 'desc 5')

        # get table Main
        # > (0,)
        # > (1,)

        # get table Side
        # > (2,)
        # > (3,)

        # get table Dessert
        # > (4,)
        # > (5,)

        # cant make an entry multiple types
        for t, i in zip(types * 2, (2, 4, 0, 5, 1, 3)):
            with pytest.raises(Exception):
                self.dbinsert(t, None, (i,))
                self.commit()  # TODO this should fail at insert not at commit.
        # database is the same as previous output
        # cant delete the type when menuitem exists
        for t, i in zip(types, (0, 2, 4)):
            with pytest.raises(Exception):
                self.dbexec('''
                DELETE FROM {t} WHERE menuItemId = %s
                ''', (i,), msg=f'remove row ({i},) from {t}')

    def test_menuitem_insert(self):
        mi_cols = 'MenuItemId', 'Name', 'Price', 'Description'

        def mi_insert(vals, err):
            if err is not None:
                with pytest.raises(err):
                    self.dbinsert('MenuItem', mi_cols, vals)
                self.commit()
            else:
                self.dbinsert('MenuItem', mi_cols, vals)

        # test name not null
        mi_insert((0, None, 10, 'desc'), NotNullViolation)
        self.rollback()
        # test name length
        mi_insert((3, 'a' * 20, 10, 'desc'), None)
        self.dbinsert('Main', None, (3,))
        self.commit()
        mi_insert((4, 'a' * 400, 10, 'desc'), Exception),
        self.rollback()

        # test id not null
        mi_insert((None, 'name', 10, 'desc'), NotNullViolation),
        self.rollback()
        # test id is unique
        mi_insert((3, 'name', 10, 'desc'), UniqueViolation),
        self.rollback()

        # test price not null
        mi_insert((5, 'name', None, 'desc'), NotNullViolation),
        self.rollback()
        # test price is number
        mi_insert((5, 'name', 'abc', 'desc'), Exception),
        self.rollback()
        # test price cant have .001 cents
        mi_insert((5, 'name', 10.001, 'desc'), None),
        # test price can have cents
        # ((5, 'name', 10.30, 'desc'), Exception),

        # test description can be null
        mi_insert((6, 'name', 10, 'desc'), None),
        self.dbinsert('Main', None, (5,))
        self.dbinsert('Main', None, (6,))
        self.commit()

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

    def test_order_insert(self):
        # all should fail before customer
        columns = 'OrderId', 'DateTime', 'TotalCharge', 'CustomerId', 'DeliveryId', 'StaffId'
        d = datetime(2020, 1, 1, 1, 1, 0)
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
            ((10, d, 20, 0, 20, 0), ForeignKeyViolation),
            ((20, d, 20, 0, 0, 20), ForeignKeyViolation),
        ]
        self.run_multiple_inserts('"Order"', columns, values)

    def test_orderitem_insert(self):
        columns = 'OrderItemId', 'OrderId', 'CustomerId', 'MenuItemId', 'Quantity', 'Charge'

        # make sure each FK must be there (as bold lines)
        values = [
            ((None, 0, 0, 0, 1, 20), NotNullViolation),
            ((0, None, 0, 0, 1, 20), NotNullViolation),
            ((0, 0, None, 0, 1, 20), NotNullViolation),
            ((0, 0, 0, None, 1, 20), NotNullViolation),
        ]
        self.run_multiple_inserts('OrderItem', columns, values)

        self.test_menuitem_insert()
        # get table MenuItem
        # > (3, 'aaaaaaaaaaaaaaaaaaaa', Decimal('10.00'), 'desc')
        # > (5, 'name', Decimal('10.00'), 'desc')
        # > (6, 'name', Decimal('10.00'), 'desc')

        self.test_order_insert()
        self.dbget_table('"Order"', ('OrderId', 'CustomerId'))
        # get table "Order"
        # > (0, 0)
        # > (1, 0)
        # > (0, 1)

        values = [
            # check all foreign keys
            ((0, 2, 0, 3, 2, 20), ForeignKeyViolation),
            ((0, 0, 2, 3, 2, 20), ForeignKeyViolation),
            ((0, 0, 0, 0, 2, 20), ForeignKeyViolation),
            ((0, 0, 0, 0, 2, 20), ForeignKeyViolation),
            # check it can insert
            ((0, 0, 0, 3, 2, 20), None),
            # check qty of 0 is not allowed
            ((1, 0, 0, 5, 0, 20), Exception),
            # check ordering the same item with different orderItems is not allowed
            ((1, 0, 0, 3, 2, 20), Exception),  # Fails here. check if this should be fixed.
        ]
        self.run_multiple_inserts('OrderItem', columns, values)
