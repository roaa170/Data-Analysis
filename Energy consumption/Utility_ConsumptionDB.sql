create table Users (
user_id int identity(1,1) PRIMARY KEY,
name varchar(50),
phone varchar(20),
email varchar(30),
city varchar(50),
district varchar(50),
household_type varchar(50),
household_size varchar(50)
);

create table TariffRates(
tariff_id int identity(1,1) PRIMARY KEY,
utility varchar(50),
start_date Date,
end_date Date,
price_per_unit decimal(10,2)
);

create table HouseholdConsumption(
consumption_id int identity(1,1) primary key ,
user_id int FOREIGN KEY references Users(user_id),
tariff_id int FOREIGN KEY references TariffRates(tariff_id),
consumption_date date,
consumption_amount decimal(10,2),
total_cost decimal(10,2)
);
create table Payments(
payment_id int identity(1,1) primary key ,
user_id int FOREIGN KEY references Users(user_id),
consumption_id  int FOREIGN KEY references HouseholdConsumption(consumption_id),
payment_date date,
payment_method varchar(50),
amount_paid decimal(10,2)
)

alter table Users 
alter column phone varchar(50)
ALTER TABLE Users ALTER COLUMN email VARCHAR(50);
ALTER TABLE Users ALTER COLUMN phone VARCHAR(50);
ALTER TABLE Users ALTER COLUMN city VARCHAR(50);
ALTER TABLE Users ALTER COLUMN district VARCHAR(50);


select * from Users
select * from TariffRates
select * from HouseholdConsumption
select * from Payments
delete from  Users
delete from TariffRates
delete from HouseholdConsumption
delete from Payments

--Top 10 High Consumers

CREATE VIEW vw_Top10_Consumers AS
select top 10 
U.user_id,
U.name,
sum(HC.consumption_amount) as total_units,
TR.utility
from Users U 
join HouseholdConsumption HC on U.user_id = HC.user_id
join TariffRates TR on HC.tariff_id = TR.tariff_id
group by U.user_id , U.name , TR.utility
order by total_units desc

select * from vw_Top10_Consumers

DROP VIEW IF EXISTS vw_Top10_Consumers;


--Bottom 10 Low Consumers
CREATE VIEW vw_low10_Consumers AS
select top 10 
U.user_id,
U.name,
sum(HC.consumption_amount) as total_units,
TR.utility
from Users U 
join HouseholdConsumption HC on U.user_id = HC.user_id
join TariffRates TR on HC.tariff_id = TR.tariff_id
group by U.user_id , U.name , TR.utility
order by total_units 

select * from vw_low10_Consumers

--  3 --Total Consumption per City per Utility
CREATE VIEW vw_City_Consumption AS
SELECT
U.city,
TR.utility  ,
SUM(HC.consumption_amount ) AS total_units
FROM Users U
JOIN HouseholdConsumption HC on U.user_id = HC.user_id
JOIN TariffRates TR ON HC.tariff_id = TR.tariff_id
group by U.city , TR.utility

SELECT * FROM vw_City_Consumption

-- 4 -- Monthly Consumption per Utility
CREATE VIEW vw_Monthly_Consumption AS
SELECT 
FORMAT(HC.consumption_date , 'yyyy-MM') AS months ,
TR.utility,
SUM(HC.consumption_amount) AS total_units
FROM HouseholdConsumption HC 
JOIN TariffRates TR ON HC.tariff_id = TR.tariff_id
group by FORMAT(HC.consumption_date , 'yyyy-MM') ,TR.utility
select * from vw_Monthly_Consumption order by months

-------------------------------------------------------------------
select top 1 start_date from TariffRates order by start_date desc
select consumption_date from HouseholdConsumption
--------------------------------------------------------------------

--5-- Average Consumption per Household Type
CREATE VIEW vw_HouseholdType_Consumption AS
SELECT 
U.household_type , 
TR.utility  ,
AVG(HC.consumption_amount ) AS avg_units
FROM Users U
LEFT JOIN HouseholdConsumption HC ON U.user_id = HC.user_id
JOIN TariffRates TR ON HC.tariff_id= TR.tariff_id
GROUP BY U.household_type , TR.utility

SELECT * FROM vw_HouseholdType_Consumption

--6-- Users with Outstanding Payments
CREATE VIEW vw_Users_Outstanding AS
SELECT 
U.user_id , U.name ,
SUM( HC.total_cost - ISNULL(P.amount_paid ,0) ) AS remaining
FROM Users AS U
JOIN HouseholdConsumption HC ON U.user_id = HC.user_id
LEFT JOIN Payments P ON HC.consumption_id = P.consumption_id
GROUP BY U.user_id , U.name
HAVING SUM( HC.total_cost - ISNULL(P.amount_paid ,0) ) >0

SELECT * FROM vw_Users_Outstanding 

--7-- Average Unit Cost per Utility
CREATE VIEW vw_Avg_Unit_Cost AS
SELECT 
TR.utility , AVG(HC.total_cost / HC.consumption_amount) AS avg_unit_cost
FROM HouseholdConsumption HC 
JOIN TariffRates TR ON HC.tariff_id = TR.tariff_id
GROUP BY TR.utility

SELECT * FROM vw_Avg_Unit_Cost

select consumption_amount from HouseholdConsumption order by consumption_amount 
--8-- Very Low Consumption Users (<=35 units)
CREATE VIEW vw_VeryLow_Consumers AS
SELECT 
U.user_id , U.name  , SUM(HC.consumption_amount) AS total_units
FROM Users U  
JOIN HouseholdConsumption HC ON U.user_id = HC.user_id
JOIN TariffRates TR ON HC.tariff_id = TR.tariff_id
GROUP BY U.user_id,  U.name , TR.utility
HAVING SUM(HC.consumption_amount) <= 35

SELECT * FROM vw_VeryLow_Consumers

--9-- Highest Total Cost Users per Utility
CREATE VIEW vw_HighCost_Users AS
SELECT TOP 50 U.user_id, U.name, T.utility, SUM(HC.total_cost) AS total_cost
FROM Users U
JOIN HouseholdConsumption HC ON U.user_id = HC.user_id
JOIN TariffRates T ON HC.tariff_id = T.tariff_id
GROUP BY U.user_id, U.name, T.utility
ORDER BY total_cost DESC;

select * from vw_HighCost_Users

--10--Avg Consumption per Household Size
CREATE VIEW vw_HouseholdSize_Consumption  AS 
SELECT  U.household_size ,  TR.utility, AVG(HC.consumption_amount) AS avg_units 
FROM Users U 
JOIN HouseholdConsumption HC ON U.user_id = HC.user_id
JOIN TariffRates TR ON HC.tariff_id = TR.tariff_id
GROUP BY U.household_size , TR.utility

SELECT * FROM vw_HouseholdSize_Consumption

--11--Avg Payment per Payment Method
CREATE VIEW vw_Payment_Method AS
SELECT payment_method , AVG(amount_paid) AS avg_paid , COUNT(*) AS num_payments 
FROM Payments group by payment_method

select * from vw_Payment_Method 

--12--Avg Payment per User
CREATE VIEW vw_AvgPayment_PerUser AS
SELECT U.user_id, U.name, AVG(P.amount_paid) AS avg_payment
FROM Users U
JOIN HouseholdConsumption HC ON U.user_id = HC.user_id
JOIN Payments P ON HC.consumption_id = P.consumption_id
GROUP BY U.user_id, U.name;

select * from  vw_AvgPayment_PerUser

-- 1️3 --  Month with Highest Total Cost per Utility
CREATE VIEW vw_HighestCostMonth  AS 
SELECT format(HC.consumption_date, 'yyyy-MM') as months ,TR.utility ,SUM(HC.total_cost) AS total_cost
FROM HouseholdConsumption HC
JOIN TariffRates TR ON HC.tariff_id = TR.tariff_id
GROUP BY FORMAT(HC.consumption_date , 'yyyy-MM') , TR.utility

SELECT * FROM vw_HighestCostMonth ;

