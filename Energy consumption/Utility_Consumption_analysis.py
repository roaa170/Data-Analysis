import pyodbc
import pandas as pd
import matplotlib.pyplot as plt

conn = pyodbc.connect(
   'DRIVER={SQL SERVER};'
    'SERVER=DESKTOP-918T9GA\SQLEXPRESS;'
    'DATABASE=Utility_Consumption;'
    'Trusted_Connection=yes;'
)

users = pd.read_sql("SELECT * FROM Users", conn)
TariffRates = pd.read_sql("SELECT * FROM TariffRates", conn)
Consumption = pd.read_sql("SELECT * FROM HouseholdConsumption", conn)
Payments = pd.read_sql("SELECT * FROM Payments", conn)

TariffRates['start_date'] = pd.to_datetime(TariffRates['start_date'])
TariffRates['end_date'] = pd.to_datetime(TariffRates['end_date'])
Consumption['consumption_date'] = pd.to_datetime(Consumption['consumption_date'])
Payments['payment_date'] = pd.to_datetime(Payments['payment_date'])

consumption_trend = Consumption.merge(TariffRates, on="tariff_id")
consumption_trend['month'] = consumption_trend['consumption_date'].dt.to_period('M')
monthly_trend = consumption_trend.groupby(['month', 'utility'])['consumption_amount'].sum().reset_index()
monthly_trend_pivot = monthly_trend.pivot(index="month", columns="utility", values="consumption_amount")
monthly_trend_pivot.plot(kind='line', figsize=(10,5))
plt.title("Monthly Consumption Trend by Utility")
plt.ylabel("Units Consumed")
plt.xlabel("Month")
plt.grid(True)
plt.show()

consumption_users = Consumption.merge(users, on="user_id")
segmentation = consumption_users.groupby('household_size')['consumption_amount'].mean().reset_index()
segmentation = segmentation.sort_values('household_size')
segmentation.plot(kind='bar', x='household_size', y='consumption_amount', figsize=(8,5), color='skyblue')
plt.title("Average Consumption per Household Size")
plt.ylabel("Average Units")
plt.xlabel("Household Size")
plt.show()

top_consumers = consumption_users.groupby(['user_id','name'])['consumption_amount'].sum().reset_index()
top_consumers = top_consumers.sort_values('consumption_amount', ascending=False).head(10)
top_consumers.plot(kind='bar', x='name', y='consumption_amount', figsize=(10,5), color='orange')
plt.title("Top 10 High Consumers")
plt.ylabel("Total Units Consumed")
plt.xlabel("User")
plt.xticks(rotation=45)
plt.show()

payments_analysis = Consumption.merge(Payments, on="consumption_id", how="left")
payments_analysis.rename(columns={'user_id_x':'user_id'}, inplace=True)
payments_analysis['amount_paid'] = payments_analysis['amount_paid'].fillna(0)
payments_analysis['remaining'] = payments_analysis['total_cost'] - payments_analysis['amount_paid']
payments_analysis = payments_analysis.merge(users[['user_id','name']], on='user_id', how='left')

outstanding_users = payments_analysis.groupby(['user_id','name'])['remaining'].sum().reset_index()
outstanding_users = outstanding_users[outstanding_users['remaining']>0]
print(outstanding_users)

avg_unit_cost = consumption_trend.groupby('utility').apply(
    lambda x: (x['total_cost'].sum()/x['consumption_amount'].sum())
).reset_index(name='avg_unit_cost')
print(avg_unit_cost)

very_low_consumers = consumption_users.groupby(['user_id','name'])['consumption_amount'].sum().reset_index()
very_low_consumers = very_low_consumers[very_low_consumers['consumption_amount']<=35]
print(very_low_consumers)

avg_household_type = consumption_users.groupby('household_type')['consumption_amount'].mean().reset_index()
avg_household_type.plot(kind='bar', x='household_type', y='consumption_amount', figsize=(10,5), color='green')
plt.title("Average Consumption per Household Type")
plt.ylabel("Average Units")
plt.xlabel("Household Type")
plt.xticks(rotation=45)
plt.show()

payments_summary = payments_analysis.groupby('payment_method')['amount_paid'].mean().reset_index()
payments_summary.plot(kind='bar', x='payment_method', y='amount_paid', figsize=(8,5), color='purple')
plt.title("Average Payment per Payment Method")
plt.ylabel("Amount Paid")
plt.xlabel("Payment Method")
plt.show()


######
users.to_excel("Users.xlsx", index=False)
Consumption.to_excel("HouseholdConsumption.xlsx", index=False)
Payments.to_excel("Payments.xlsx", index=False)
monthly_trend.to_excel("MonthlyConsumption.xlsx", index=False)
top_consumers.to_excel("TopConsumers.xlsx", index=False)
outstanding_users.to_excel("OutstandingUsers.xlsx", index=False)