-- example
CREATE TABLE Example(
    staffid INTEGER PRIMARY KEY,
    position VARCHAR(20) NOT NULL,
    name INTEGER DEFAULT 1,
    birthday DATE NULL,
    age INTEGER CHECK( age >= 0 AND age < 150),
    country VARCHAR(20),
    -- if composite PK
    PRIMARY KEY (sid,uos),
    FOREIGN KEY (sid) REFERENCES Student,

    -- the on delete cascade conveys
    -- that an enrolled row should be
    -- deleted when the student with sid
    -- that it refers to is deleted
    ON DELETE CASCADE

    -- the on update set default
    -- will attempt to update the
    -- value of sid to a default value
    -- that is specified as the default
    -- in this Enrolled schema definition
    ON UPDATE SET DEFAULT


    CONSTRAINT FK_sid_enrolled FOREIGN KEY (sid)
    REFERENCES Student ON DELETE CASCADE,
    CONSTRAINT FK_cid_enrolled FOREIGN KEY (uos)
    REFERENCES UnitOfStudy ON DELETE CASCADE,
    CONSTRAINT CK_grade_enrolled CHECK(grade IN ('F', 'A')),
    CONSTRAINT PK_enrolled PRIMARY KEY (sid,uos)
);
-- constraints: UNIQUE, NOT NULL, UNIQUE, DEFAULT, CHECK,

CREATE TABLE Staff(
    staffid INTEGER PRIMARY KEY,
    position VARCHAR(20),
    name VARCHAR(20)
);
CREATE TABLE Menu(
    menuId INTEGER PRIMARY KEY,
    description VARCHAR(100)
);
CREATE TABLE MenuItem(
    menuItemId INTEGER PRIMARY KEY,
    name VARCHAR(20),
    price FLOAT,
    description VARCHAR(100),
    itemType VARCHAR(10) NOT NULL
);
CREATE TABLE MenuContains(
    menuId INTEGER,
    menuItemId INTEGER,
    PRIMARY KEY (menuId, menuItemId),
    CONSTRAINT FK_menuId_MenuContains FOREIGN KEY (menuId) REFERENCES Menu
    CONSTRAINT FK_menuItemId_MenuContains FOREIGN KEY (menuItemId) REFERENCES MenuItem
);
CREATE TABLE OrderItem(

);
CREATE TABLE Order(

);
CREATE TABLE Customer(
    customerId INTEGER PRIMARY KEY,
    mobileNumber INTEGER,
    firstName VARCHAR(30),
    lastName VARCHAR(30),
    address VARCHAR(100)
);
CREATE TABLE Delivery(

);
CREATE TABLE Courier(
    courierId INTEGER PRIMARY KEY,
    name VARCHAR(20),
    address VARCHAR(100),
    mobileNumber INTEGER
);
