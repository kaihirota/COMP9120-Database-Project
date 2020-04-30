Begin;
insert into menuitem(menuitemid, name, price, description) values (10, 'name', 30, 'desc');
Commit;
BEGIN;
insert into Menu(menuid, description) values (1, 'description');
insert into Contains(menuid, menuitemid) values (1, 10);
Commit;
BEGIN;
insert into Contains(menuid, menuitemid) values (2, 10);
insert into Menu(menuid, description) values (2, 'description');
Commit;

BEGIN;
insert into Menu(menuid, description) values (3, 'description');
Commit; -- should fail

BEGIN;
insert into Contains(menuid, menuitemid) values (3, 10);
Commit; -- should fail
