CREATE DATABASE entreeai;
USE entreeai;

GRANT ALL PRIVILEGES on database.entreeai to 'root'@'localhost';
FLUSH PRIVILEGES;

-- Holds various food
CREATE TABLE IF NOT EXISTS food (
    food_id int NOT NULL auto_increment PRIMARY KEY,
    food_name varchar(64) NOT NULL,
    price DECIMAL(13,2)
);

CREATE TABLE IF NOT EXISTS flavors (
    flavor_id int NOT NULL auto_increment PRIMARY KEY,
    flavor_name varchar(64) NOT NULL,
    food_id int NOT NULL,
    FOREIGN KEY (food_id) REFERENCES food(food_id)
);

CREATE TABLE IF NOT EXISTS units (
    unit_id int NOT NULL auto_increment PRIMARY KEY,
    unit_name varchar(64) NOT NULL,
    food_id int NOT NULL,
    price DECIMAL (13, 2),
    FOREIGN KEY (food_id) REFERENCES food(food_id)
);

CREATE TABLE IF NOT EXISTS other_names (
    fo_id int NOT NULL auto_increment PRIMARY KEY,
    fo_name varchar(64) NOT NULL,
    food_id int NOT NULL,
    FOREIGN KEY (food_id) REFERENCES food(food_id)

);
 
--  CREATE TABLE IF NOT EXISTS food_units (
--     food_id int NOT NULL,
--     unit_id int NOT NULL,
--     price DECIMAL(13, 2),
--     FOREIGN KEY (food_id) REFERENCES food(food_id),
--     FOREIGN KEY (unit_id) REFERENCES units(unit_id)
-- );

-- Examples would be like medium, large, x-large
-- 14 inches, 16 inches
