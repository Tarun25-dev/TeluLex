import streamlit as st
import sqlite3
import pandas as pd
from datetime import date,timedelta,datetime

st.set_page_config(page_icon="📊",page_title="DashBoard")
st.title("📊 Dictionary DashBoard")

conn =sqlite3.connect("dictionary.db")
cursor = conn.cursor() # cursor is the object that communicates with sqlite it sends sql commands to the db

# execute tells sqlite to run the sql query inside it
cursor.execute("""
SELECT DATE(created_at) as day, COUNT(*) AS words
FROM dictionary
WHERE created_at IS NOT NULL
GROUP BY DATE(created_at)
ORDER BY day;

""")
 # DATE has day with time as well to remove time so we write only date(created_at) as save as day 
#  count(*) returns the total no.of rows that days has and saves as words
# is not null does ignores the rows that dont have a timestamp
# it groups all the same date rows count as one row for every day
# order by makes things all the data sort in order

rows = cursor.fetchall() #  it does have all the rows returned from the sql query

df = pd.DataFrame(rows,columns=["📅 Date","Words Added"])
st.dataframe(df,hide_index=True,width="stretch",height=450)

# find streak and display
# rows data convert into a set beacuse u only need to know whether a date exists.
activity_days = {row[0] for row in rows} # it takes all the rows of first value only that has date 
# main imp thing is that all the rows is stored as strings then we need to convert into date object then only we compare with date package
my_dates = {datetime.strptime(day,"%Y-%m-%d").date() for day in activity_days}

today = date.today()
streak = 0


day = today
list =[]
while day in my_dates:
    
    streak += 1
    day = day - timedelta(days=1) # the loop runs upto start of the streak day and ends at yesterday of start of the streak day so if we want that start day streak then we add one day so we get the from to today

st.divider()

start_day = day + timedelta(days=1)
# we already have endday is in today

with st.container(border=True,width="content"):
   st.write("**Streak**")
   st.metric("Your Current Streak",f"🔥  {streak}")
   st.write(f"**From:** {start_day}")
   st.write(f"**To:** {today}")


