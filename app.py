import streamlit as st
import sqlite3
import pandas as pd
import time
import requests # for getting info from apis

st.set_page_config(
    page_title="TeluLex",
    page_icon="favicon.png",
    # layout="wide" if we need full display to use then this code does wide page to use 
)


st.image("nav.png")
# connect the database if exist or else create it and connect
conn = sqlite3.connect("dictionary.db")

# A cursor is the object we use to talk to the database
cursor = conn.cursor()

# without a cursor python can't execute SQL commands
# id INTEGER PRIMARY KEY AUTOINCREMENT for serial number with integer as well as uniuqe each other (primary key) and autoincrement for every row
# execute is used to send this sql query to the sqlite 
cursor.execute("""
create table if not exists
dictionary(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            english TEXT,
            telugu TEXT,
            example TEXT     
               )

""")

# save all the changes permanently, without commit the data may disappear when the program ends. 
conn.commit()

# for title and style
# st.markdown(
#     "<h1 style='text-align: center; color: black;'>My Personal Dictionary</h1><br>",unsafe_allow_html=True
# )

# unsafe html true is used to render raw HTML and CSS instead of displaying it as plain text

# search button
with st.container(border=True):
  search = st.text_input("🔍 Search",placeholder="Search by English or Telugu...")

# number_input is a streamlit function it creates a number input box instead of textbox
# then user can type number or click increase or decrease custom buttons
# why min value 1 beacuse we keep that in sql query autoincrement it default starting value is 1
# delete_id = st.number_input("ENTER ID to Delete",min_value=1,step=1)

# if st.button("🚮 Delete"):
#   cursor.execute("DELETE FROM dictionary WHERE id=?",(delete_id,))
    # without commit delete works temporary and that again exists deleted word
#   conn.commit()
#    st.success("Word Deleted Successfully!")
# one thing to remember after we delete that word through id but the next word id is not renumbered for ex i delete second id and then they dont show id 2 and continue with three
# beacuse autoincrement always remembers the highest ID it has ever used
# we leave that exactly how it does so keep it all unique

st.divider() # this automatically draws a horizontal  line across the page

if "active_session" not in st.session_state:
    st.session_state.active_session = None # beacuse we dont know until the user selects the option from thiis container

co1,co2,co3 = st.columns(3)
with co1:
    if st.button(":green[➕ New Word]",use_container_width=True):
        st.session_state.active_session = "new" # this holds new key for comfirmation of new word click
with co2:
    if st.button(":green[📝 Edit / Update]",use_container_width=True):
        st.session_state.active_session = "edit"
with co3:
    if st.button("🗑️ Delete",type="primary",use_container_width=True):
        st.session_state.active_session = "delete"

# show only the selected section

if st.session_state.active_session == "new":
    with st.form("new_entry",clear_on_submit=True):
        st.subheader(""" 📝 New Entry """)
        col1, col2 = st.columns(2)
        with col1:
            english = st.text_input("English Word:red[*]") # if you want to color any label or word then we must  use ":colorname[text]" 
        with col2:
            telugu = st.text_input("Telugu word:red[*]")
        example = st.text_input("Example Sentence")

        # session state is stores values while the app is running, even through streamlit reruns your script every time you click a button or type somethin

        saved = False # this for success msg identify holder
        checkEng = False
        checkTel = False

        c1,c2,c3 = st.columns([2,1,2]) # i divided three columns and making that save button at middle with size one (half of the other two)
        with c2:
            submitted = st.form_submit_button("Save",type="primary")
            if submitted: # primary for img btns which has extra apperece than secondarary and default is secondarary
                # before save first we need to validate wether they gave eng word 
                if not english.strip():
                    checkEng = True
                elif not telugu.strip():
                    checkTel = True
                else:
                    cursor.execute(
                    "INSERT INTO dictionary(english, telugu, example, created_at) VALUES(?,?,?,date('now','localtime'))",(english,telugu,example)
                    )
                    conn.commit()
                    saved = True # for making that success out of the with c2 then only it shows its full width otherwise it takes under its 1 size
                    
        if saved:
            msg = st.empty() # this perform as a placeholder with empty value stored in msg
            msg.success("✔️ Saved Successfully")
            time.sleep(2)
            msg.empty()
        elif checkEng:
            st.error("Please Enter an English word.")
        elif checkTel:
            st.error("Please Enter a Telugu word.")
    # for close form
    if st.button("❌ Close"):
        st.session_state.active_session = None
        st.rerun()
    
elif st.session_state.active_session == "edit":
    with st.container(border=True):
        st.subheader("Update word")
        update_search = st.text_input("search word to update", placeholder="type a word")

        if update_search:
            cursor.execute("SELECT id, english, telugu, example FROM dictionary WHERE english LIKE ? OR telugu LIKE ?",("%"+update_search+"%","%"+update_search+"%")) #  for finding that search word in db
            result = cursor.fetchone()
        # if result exist in db then the below statement executes

            if result:
                english = st.text_input("English",value = result[1],key="edit_english") # key values are useful whenever edit an eng or tel or example after that search we need to clear that data from inputs by using del
                telugu = st.text_input("Telugu",value=result[2],key="edit_telugu")
                example = st.text_input("Example",value=result[3],key="edit_example")
                # value=result[1] that automatically fills the input with the existing value so we can edit what we want 

                # then we edit that word and keep one update button to make changes in db

                if st.button("Update",type="primary"):
        # set does set these columns to new values and english ? says replace english column with the new english value if we only edit telugu word then remove two from set 
                    cursor.execute("UPDATE dictionary SET english = ?, telugu = ?, example =? WHERE id = ?",(english,telugu,example,result[0]))
                    conn.commit()
                    msg = st.empty()
                    msg.success("Word Updated Successfully!")
                    time.sleep(2)
# for clear edit fields
                    del st.session_state["edit_english"]
                    del st.session_state["edit_telugu"]
                    del st.session_state["edit_example"]
                    st.session_state.active_session = None
                    st.rerun()

    if st.button("❌ Close"):
        st.session_state.active_session = None
        st.rerun()

elif st.session_state.active_session == "delete":
    with st.container(border=True):
        st.subheader("🚮!",help="delete word")
        delete_search = st.text_input("Search word to delete",placeholder="Type a word...")

        if delete_search:
            cursor.execute("SELECT id, english, telugu, example FROM dictionary WHERE english LIKE ? OR telugu LIKE ?",('%'+delete_search+'%','%'+delete_search+'%'))
            result = cursor.fetchone() # result stored like this (1, 'work', 'pani', 'i have work to do')

            if result:
                st.write("### Word Found")
                st.write("**English:**",result[1])
                st.write("**Telugu:**",result[2])
                st.write("**Example:**",result[3])

                if st.button("Delete",type="primary"):
                    cursor.execute("DELETE FROM dictionary WHERE id=?",(result[0],))
                    conn.commit()
                    msg = st.empty()
                    msg.success("Word deleted successfully!")
                    time.sleep(2)
                    st.rerun()

    if st.button("❌ Close"):
        st.session_state.active_session = None
        st.rerun()
        
st.divider()

# we need to calculate no.of words in the dictionary through query and use count() for getting how many rows exactly from the db and it returns tuple and it has only one number thats its len then we show in the page by index value 0
cursor.execute("SELECT COUNT(*) FROM dictionary")
total_words = cursor.fetchone()[0] # it returns tuple and that len value in index 0
st.metric("Total Words: ",total_words) # metric is an widget in streamlit to highlight an important number 

st.subheader("Saved Words")
# LIKE is used for to find similar words in english foe filter 
# '%'+search+'%', % is a wildcard anything can come before or after the word 
if search:
    cursor.execute(
        """SELECT id, english, telugu, example FROM dictionary
           WHERE english LIKE ?
           or telugu LIKE ?"""
           ,('%'+search+'%', '%'+search+'%'))
else:
    cursor.execute("SELECT id, english, telugu,example FROM dictionary")
    

# fetch all the rows in the database, if we need use fetchone for first row or fetchmany(n) for getting n rows
rows = cursor.fetchall()

# DataFrame creates a DataFrame object like used to building a table
df = pd.DataFrame(
    rows,
    columns=["ID", "English", "Telugu", "Example"]
)

# adding s.no
df.insert(0, "S.No", range(1,len(df)+1))

# i dont want to display the id column so i need to hide that like this 
display_df = df.drop(columns=["ID"]) # it hides the id column from db but it wont delete from db permanently it just take and filter this variable can do

# dataframe() is a streamlit function used to display a DataFrame on the webpage
st.dataframe(display_df, hide_index=True)


# why hide_index beacuse streamlit in built provies serial numbers for dataframe(), beacuse we already given seperate serial number column

st.divider()
st.subheader("Translate")
if "tel" not in st.session_state:
    st.session_state.tel = "" 

def translate():
    eng = st.session_state.eng # this stored user typed value from input field
    if eng.strip():
        url = f"https://api.mymemory.translated.net/get?q={eng}&langpair=en|te"
        response = requests.get(url) # this has data from api like json data

        if response.status_code == 200:# if in response from api has status code if it is 200 then it has our desired data inside
            data = response.json()# it converts that json data to the dictionary called data
            st.session_state.tel = data["responseData"]["translatedText"]  # whenever we click the function it executes and that telugu input field auto fill in input

# for clear input fields
def clear_fields():
    st.session_state["eng"] = ""
    st.session_state["tel"] = ""

with st.container(border=True):
    cl1, cl2 = st.columns(2)

    with cl1:
        st.text_input("English",key="eng",placeholder="type a word...")
    with cl2:
        st.text_input("Telugu",key="tel",placeholder="type a word...")
    # what does key is "Create a text input, and whatever the user types into it, 
    # automatically store it in st.session_state["english"]."
    cl3, cl4 = st.columns(2)
    with cl3:
        st.button("Translate",icon="🌐",on_click=translate,use_container_width=True)  
    with cl4:
        # clear button
        st.button("Clear",on_click=clear_fields,use_container_width=True)
            

    st.code(st.session_state.tel,language=None)


# User types "apple" in the English box.
# Telugu box is empty, so the user can type manually if they want.
# If the user clicks Translate, the callback runs before the page is redrawn, so st.session_state.telugu is updated.
# The Telugu input is automatically filled with ఆపిల్ (or whatever the API returns).

st.divider()















# delete removes records from dictionary db but table itself is exists table structure remains
# sqlite has a special hidden table called sqlite_sequence it stores the last autoincrement value for every table so whenever we again start from id 1 then we execute that query
# ⚠️ the below query deletes all the data 

# cursor.execute("DELETE FROM dictionary")
# cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'dictionary'")
# conn.commit()

# we need another column so we need to execute thiss query at once and then i commented that no need run every
# cursor.execute("""ALTER TABLE dictionary ADD COLUMN created_at TIMESTAMP""")
# conn.commit()
