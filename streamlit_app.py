# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title("🥤Customize Your Smoothie!🥤")
st.write("Choose the fruits you want in your Smoothie!")

name_on_order = st.text_input('Name on Smoothie')
st.write('The name on your smoothie will be:', name_on_order)

# Get the Snowpark session
cnx = st.connection("snowflake")
session = cnx.session()

# Query the fruit names
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))

# Convert to a list of strings
fruit_list = [row["FRUIT_NAME"] for row in my_dataframe.collect()]

# Use in Streamlit multiselect
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)
if ingredients_list:

    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    #st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """','"""+name_on_order+"""')"""

    #st.write(my_insert_stmt)
    time_to_insert = st.button("Submit Order")
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered, " + name_on_order + "!", icon="✅")

# New section to display smoothiefroot nutrition information
import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response)
