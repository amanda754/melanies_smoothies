# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title("🥤Customize Your Smoothie!🥤")
st.write("Choose the fruits you want in your Smoothie!")

name_on_order = st.text_input('Name on Smoothie')
st.write('The name on your smoothie will be:', name_on_order)

# Get the Snowpark session (only once!)
session = get_active_session()

# Query the fruit names
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col("SEARCH_ON"))

# Convert to Pandas for easier manipulation
pd_df = my_dataframe.to_pandas()

# Use in Streamlit multiselect
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    # Cleanly join ingredients into a single string
    ingredients_string = ' '.join(ingredients_list)

    for fruit_chosen in ingredients_list:
        # Get the corresponding search value
        search_on_row = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON']
        search_on = search_on_row.iloc[0] if not search_on_row.empty else fruit_chosen

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Safely call the SmoothieFroot API
        try:
            response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on, timeout=10)
            response.raise_for_status()
            data = response.json()
            st.dataframe(data['nutrition'], use_container_width=True)
        except requests.exceptions.RequestException as e:
            st.error(f"Could not retrieve nutrition info for {fruit_chosen}.")
            st.caption(f"Error: {e}")

    # Prepare SQL insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Submit order
    time_to_insert = st.button("Submit Order")
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
