
-- Below are the 5 tables are required.

CREATE TABLE abhibus_operator_master_id(operator VARCHAR(100),id INT);
CREATE TABLE redbus_operator_master_id(operator VARCHAR(100),id INT);
CREATE TABLE abhibus_operators_data_datewise(operator VARCHAR(100),pick_time VARCHAR(25),DATE VARCHAR(25),site VARCHAR(20), rid INT,route VARCHAR(200));
CREATE TABLE redbus_operators_data_datewise(operator VARCHAR(100),pick_time VARCHAR(25),DATE VARCHAR(25),site VARCHAR(20), rid INT,route VARCHAR(200));
CREATE TABLE both_operators(operator VARCHAR(100), no_of_services INT, id INT,site VARCHAR(100),route VARCHAR(200));
CREATE TABLE display_data(sno INT,operator VARCHAR(200),abhibus_inventory INT,redbus_inventory INT, difference INT,abhibus_operation_time VARCHAR(200),redbus_operation_time VARCHAR(200),status VARCHAR(200),comment VARCHAR(200),date VARCHAR(20),route VARCHAR(200));
CREATE TABLE bus_opr_count(date VARCHAR(20),route VARCHAR(200),bus_count INT,opr_count INT)
CREATE TABLE location(cityname varchar(200));
