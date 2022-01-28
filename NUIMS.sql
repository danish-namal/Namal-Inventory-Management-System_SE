create database NUIMS;
use NUIMS;
CREATE TABLE users (
    id int NOT NULL PRIMARY KEY AUTO_INCREMENT, 
    firstName varchar(255), 
    lastName varchar(255), 
    username varchar(255), 
    email varchar(255),
    designation varchar(255),
    pass varchar(255),
    picture varchar(255)
);

CREATE TABLE issueProducts (
    id int NOT NULL PRIMARY KEY AUTO_INCREMENT, 
    email varchar(255),
    productName varchar(255), 
    Image varchar(255), 
    productStatus int,
    designation varchar(255)
);

drop table issueProducts;

select * from issueProducts;

select * from users;

CREATE TABLE category (
    category_id int NOT NULL PRIMARY KEY AUTO_INCREMENT, 
    categoryName varchar(255)
);

select * from category;

CREATE TABLE items (
	item_id int NOT NULL PRIMARY KEY AUTO_INCREMENT,
	item_name varchar(255),
    quantity int,
    image varchar(255),
    category_name varchar(255)
);
select * from items;
drop table items;
-- ALTER TABLE items
-- 	ADD FOREIGN KEY (category_id) REFERENCES category(category_id);



drop database NUIMS;
select * from users;