import pyodbc
from faker import Faker
from datetime import date
import random

faker = Faker()

conn = pyodbc.connect(
    'DRIVER={SQL SERVER};'
    'SERVER=DESKTOP-918T9GA\SQLEXPRESS;'
    'DATABASE=Utility_Consumption;'
    'Trusted_Connection=yes;'
)
cursor = conn.cursor()

# ----------------------------
# Users
# ----------------------------
user_ids = []
for _ in range(500):
    name = faker.name()
    phone = faker.phone_number()
    email = faker.free_email()
    city = faker.city()
    district = faker.state()
    household_type = faker.random_element([
        'Apartment', 'House', 'Villa', 'Duplex', 'Townhouse',
        'Studio', 'Bungalow', 'Penthouse', 'Cottage', 'Loft'
    ])
    household_size = faker.random_int(1, 10)

    cursor.execute('''
        INSERT INTO Users (name, phone, email, city, district, household_type, household_size)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, phone, email, city, district, household_type, household_size))

    conn.commit()
    cursor.execute("SELECT TOP 1 user_id FROM Users ORDER BY user_id DESC")
    user_id = int(cursor.fetchone()[0])
    user_ids.append(user_id)

# ----------------------------
# TariffRates
# ----------------------------
tariff_ids = []
for _ in range(500):
    utility = faker.random_element(['Electricity', 'Water', 'Gas'])
    start_date = faker.date_between(start_date=date(2024, 1, 1), end_date=date(2024, 12, 1))
    end_date = faker.date_between(start_date=start_date, end_date=date(2024, 12, 31))
    price_per_unit = round(random.uniform(0.2, 1.0), 2)

    cursor.execute('''
        INSERT INTO TariffRates (utility, start_date, end_date, price_per_unit)
        VALUES (?, ?, ?, ?)
    ''', (utility, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), float(price_per_unit)))

    conn.commit()
    cursor.execute("SELECT TOP 1 tariff_id FROM TariffRates ORDER BY tariff_id DESC")
    tariff_id = int(cursor.fetchone()[0])
    tariff_ids.append(tariff_id)

# ----------------------------
# HouseholdConsumption
# ----------------------------
consumption_ids = []
for user_id in user_ids:
    for _ in range(random.randint(3, 6)):
        tariff_id = random.choice(tariff_ids)
        amount = round(random.uniform(10, 500), 2)

        cursor.execute("SELECT price_per_unit FROM TariffRates WHERE tariff_id = ?", (tariff_id,))
        price_per_unit = float(cursor.fetchone()[0])

        total_cost = round(amount * price_per_unit, 2)
        consumption_date = faker.date_between(start_date=date(2024, 1, 1), end_date=date(2024, 12, 31))
        consumption_date_str = consumption_date.strftime('%Y-%m-%d')

        cursor.execute('''
            INSERT INTO HouseholdConsumption (user_id, tariff_id, consumption_date, consumption_amount, total_cost)
            VALUES (?, ?, ?, ?, ?)
        ''', (int(user_id), int(tariff_id), consumption_date_str, float(amount), float(total_cost)))

        conn.commit()
        cursor.execute("SELECT TOP 1 consumption_id FROM HouseholdConsumption ORDER BY consumption_id DESC")
        consumption_id = int(cursor.fetchone()[0])
        consumption_ids.append((user_id, consumption_id))

# ----------------------------
# Payments
# ----------------------------
payment_methods = ['Credit Card', 'Cash', 'Bank Transfer']

for user_id, consumption_id in consumption_ids:
    for _ in range(random.randint(1, 2)):
        cursor.execute("SELECT total_cost FROM HouseholdConsumption WHERE consumption_id = ?", (consumption_id,))
        total_cost = float(cursor.fetchone()[0])
        amount_paid = round(random.uniform(1, total_cost), 2)

        payment_date = faker.date_between(start_date='-6m', end_date='today').strftime('%Y-%m-%d')
        payment_method = random.choice(payment_methods)

        cursor.execute('''
            INSERT INTO Payments (user_id, consumption_id, payment_date, payment_method, amount_paid)
            VALUES (?, ?, ?, ?, ?)
        ''', (int(user_id), int(consumption_id), payment_date, payment_method, float(amount_paid)))

conn.commit()
conn.close()
