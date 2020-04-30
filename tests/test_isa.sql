BEGIN;
insert into Main values (0);
insert into Side values (0);
insert into Dessert values (0);
insert into MenuItem(MenuItemId, Name, Price, Description) values (0, 'name', 10, 'desc');
Commit; -- should fail

BEGIN;
insert into Side values (0);
insert into Dessert values (0);
insert into MenuItem(MenuItemId, Name, Price, Description) values (0, 'name', 10, 'desc');
Commit; -- should fail

BEGIN;
insert into Main values (0);
insert into Dessert values (0);
insert into MenuItem(MenuItemId, Name, Price, Description) values (0, 'name', 10, 'desc');
Commit; -- should fail

BEGIN;
insert into Main values (0);
insert into Side values (0);
insert into MenuItem(MenuItemId, Name, Price, Description) values (0, 'name', 10, 'desc');
Commit; -- should fail

BEGIN;
insert into Main values (0);
insert into MenuItem(MenuItemId, Name, Price, Description) values (0, 'name', 10, 'desc');
Commit;


BEGIN;
insert into Side values (1);
insert into MenuItem(MenuItemId, Name, Price, Description) values (1, 'name', 10, 'desc');
Commit;

BEGIN;
insert into Dessert values (2);
insert into MenuItem(MenuItemId, Name, Price, Description) values (2, 'name', 10, 'desc');
Commit;


