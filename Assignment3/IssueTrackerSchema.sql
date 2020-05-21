DROP TABLE IF EXISTS A3_ISSUE;
DROP TABLE IF EXISTS A3_USER;

CREATE TABLE A3_USER
(
	USER_ID SERIAL PRIMARY KEY,
	USERNAME VARCHAR(100) NOT NULL,
	FIRSTNAME VARCHAR(100) NOT NULL,
	LASTNAME VARCHAR(100) NOT NULL
);

INSERT INTO A3_USER (USERNAME,FIRSTNAME,LASTNAME) VALUES ('-','not','assigned');			-- 1
INSERT INTO A3_USER (USERNAME,FIRSTNAME,LASTNAME) VALUES ('Chris', 'Christopher','Smith');  -- 2
INSERT INTO A3_USER (USERNAME,FIRSTNAME,LASTNAME) VALUES ('Dave', 'David','Jones');         -- 3
INSERT INTO A3_USER (USERNAME,FIRSTNAME,LASTNAME) VALUES ('Vlad', 'Vladimir','Putin');      -- 4

CREATE TABLE A3_ISSUE
(
	ISSUE_ID SERIAL PRIMARY KEY,
	TITLE VARCHAR(100),
	DESCRIPTION VARCHAR(1000),
	CREATOR INTEGER NOT NULL REFERENCES A3_USER,
	RESOLVER INTEGER REFERENCES A3_USER,
	VERIFIER INTEGER REFERENCES A3_USER
);

BEGIN;
	INSERT INTO A3_ISSUE (TITLE,DESCRIPTION,CREATOR,RESOLVER,VERIFIER) VALUES ('Factorial with addition anomaly','Performing a factorial and then addition produces an off by 1 error',2,3,4);
	INSERT INTO A3_ISSUE (TITLE,DESCRIPTION,CREATOR,RESOLVER,VERIFIER) VALUES ('Division by zero','Division by 0 doesn''t yield error or infinity as would be expected. Instead it results in -1.',2,3,1);
	INSERT INTO A3_ISSUE (TITLE,DESCRIPTION,CREATOR,RESOLVER,VERIFIER) VALUES ('Incorrect BODMAS order','Addition occurring before multiplication',3,1,1);
COMMIT;

-- -- update issues with no resolver or verifier assigned
-- CREATE OR REPLACE FUNCTION checkIssues()
--   RETURNS TRIGGER AS $checkIssues$
-- BEGIN
--     UPDATE A3_ISSUE
-- 	SET resolver = 1
-- 	WHERE resolver IS NULL;
--
-- 	UPDATE A3_ISSUE
-- 	SET verifier = 1
-- 	WHERE verifier IS NULL;
-- 	RETURN NULL;
-- END;
-- $checkIssues$ LANGUAGE plpgsql;

-- convert a username to its userid for insertions
CREATE OR REPLACE FUNCTION get_uid(required_username VARCHAR(100))
  RETURNS INTEGER AS $$
  DECLARE
  rval INTEGER;
BEGIN
  SELECT user_id INTO rval FROM A3_USER WHERE username = required_username LIMIT 1;
  IF rval is NULL THEN RAISE EXCEPTION 'User does not exist';
  END IF;
  return rval;
END;
$$ LANGUAGE plpgsql;

