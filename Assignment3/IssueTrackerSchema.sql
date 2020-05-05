DROP TABLE IF EXISTS A3_ISSUE;
DROP TABLE IF EXISTS A3_USER;

CREATE TABLE A3_USER
(
	USER_ID SERIAL primary key,
	USERNAME VARCHAR(100) not null,
	FIRSTNAME VARCHAR(100) not null, 
	LASTNAME VARCHAR(100) not null
);

Insert into A3_USER (USERNAME,FIRSTNAME,LASTNAME) values ('-','not','assigned');			-- 1
Insert into A3_USER (USERNAME,FIRSTNAME,LASTNAME) values ('Chris', 'Christopher','Smith');  -- 2
Insert into A3_USER (USERNAME,FIRSTNAME,LASTNAME) values ('Dave', 'David','Jones');         -- 3
Insert into A3_USER (USERNAME,FIRSTNAME,LASTNAME) values ('Vlad', 'Vladimir','Putin');      -- 4

CREATE TABLE A3_ISSUE 
(
	ISSUE_ID SERIAL primary key,
	TITLE VARCHAR(100),  
	DESCRIPTION VARCHAR(1000),
	CREATOR INTEGER not null REFERENCES A3_USER, 
	RESOLVER INTEGER REFERENCES A3_USER, 
	VERIFIER INTEGER REFERENCES A3_USER
);

Insert into A3_ISSUE (TITLE,DESCRIPTION,CREATOR,RESOLVER,VERIFIER) values ('Factorial with addition anomaly','Performing a factorial and then addition produces an off by 1 error',2,3,4);
Insert into A3_ISSUE (TITLE,DESCRIPTION,CREATOR,RESOLVER,VERIFIER) values ('Division by zero','Division by 0 doesn''t yield error or infinity as would be expected. Instead it results in -1.',2,3,1);
Insert into A3_ISSUE (TITLE,DESCRIPTION,CREATOR,RESOLVER,VERIFIER) values ('Incorrect BODMAS order','Addition occurring before multiplication',3,1,1);

commit;