-- CREATE TABLE Example(
--     staffid INTEGER NOT NULL,
--     position VARCHAR(20) NOT NULL,
--
--     name INTEGER DEFAULT 1,
--     birthday DATE NULL,
--     country VARCHAR(20)
-- );

CREATE TABLE Staff(
    staffid INTEGER PRIMARY KEY,
    position VARCHAR(20) NOT NULL,
    name VARCHAR(20) NOT NULL
);
