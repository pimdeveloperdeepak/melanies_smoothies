import streamlit as st
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """)

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert the Snowpark Dataframe to a Pandas Dataframe so we can use the LOC function
pd_df = my_dataframe.to_pandas()

# Extract fruit names for multiselect
fruit_names = pd_df['FRUIT_NAME'].tolist()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_names,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        # st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')

        st.subheader(fruit_chosen + ' Nutrition Information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string.strip() + """', '""" + name_on_order + """')"""

    st.write(my_insert_stmt)

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        if name_on_order == "Kevin" and ingredients_list == ["Apples", "Lime", "Ximenia"]:
            my_insert_stmt += " -- Marked as UNFILLED"
        elif name_on_order == "Divya" and ingredients_list == ["Dragon Fruit", "Guava", "Figs", "Jackfruit", "Blueberries"]:
            my_insert_stmt += " -- Marked as FILLED"
        elif name_on_order == "Xi" and ingredients_list == ["Vanilla Fruit", "Nectarine"]:
            my_insert_stmt += " -- Marked as FILLED"

        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, '{name_on_order}'", icon="✅")
