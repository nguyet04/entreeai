CREATE DATABASE entreeai;
USE entreeai;

GRANT ALL PRIVILEGES on database.entreeai to 'root'@'localhost';
FLUSH PRIVILEGES;

-- Holds various food
CREATE TABLE IF NOT EXISTS food (
    food_id int NOT NULL auto_increment PRIMARY KEY,
    food_name varchar(64) NOT NULL
);

-- Mushrooms belong to pizza, hence foreign key, but can also belong to Calzone
CREATE TABLE IF NOT EXISTS ingredients (
    ingredient_id int NOT NULL auto_increment PRIMARY KEY,
    ingredient_name varchar(64) NOT NULL
);

CREATE TABLE IF NOT EXISTS food_ingredient (
    fi_id int NOT NULL auto_increment PRIMARY KEY,
    food_id int NOT NULL,
    ingredient_id int NOT NULL,
    FOREIGN KEY (food_id) REFERENCES food(food_id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id)
);
 
-- Examples would be like medium, large, x-large
-- 14 inches, 16 inches
CREATE TABLE IF NOT EXISTS units (
    unit_id int NOT NULL auto_increment PRIMARY KEY,
    unit_name varchar(64) NOT NULL,
    quantity int
);

