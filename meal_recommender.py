import streamlit as st
from generator import Generator
import pandas as pd
from streamlit_echarts import st_echarts

st.set_page_config(page_title="Meal Recommender", layout="wide")
nutrition_values = ['Calories', 'FatContent', 'SaturatedFatContent', 'CholesterolContent', 'SodiumContent',
                    'CarbohydrateContent', 'FiberContent', 'SugarContent', 'ProteinContent']
if 'generated' not in st.session_state:
    st.session_state.generated = False
    st.session_state.recommendations = None


class Recommendation:
    def __init__(self, nutrition_list, nb_recommendations, ingredients_include_txt, ingredients_exclude_txt):
        self.nutrition_list = nutrition_list
        self.nb_recommendations = nb_recommendations
        self.ingredients_include_txt = ingredients_include_txt
        self.ingredients_exclude_txt = ingredients_exclude_txt

    def generate(self, ):
        params = {'n_neighbors': self.nb_recommendations, 'return_distance': False}
        ingredients_include = self.ingredients_include_txt.split(';') if self.ingredients_include_txt else []
        ingredients_exclude = self.ingredients_exclude_txt.split(';') if self.ingredients_exclude_txt else []
        generator = Generator(self.nutrition_list, ingredients_include, ingredients_exclude, params)
        recommendations = generator.generate()
        recommendations = recommendations.json()['output']
        return recommendations


class Display:
    def __init__(self):
        self.nutrition_values = nutrition_values

    def display_recommendation(self, recommendations):
        st.subheader('Recommended recipes:')
        if recommendations is not None:
            rows = len(recommendations) // 5
            for column, row in zip(st.columns(5), range(5)):
                with column:
                    for recipe in recommendations[rows * row:rows * (row + 1)]:
                        recipe_name = recipe['Name']
                        expander = st.expander(recipe_name)
                        nutritions_df = pd.DataFrame({value: [recipe[value]] for value in nutrition_values})

                        expander.markdown(
                            f'<h5 style="text-align: center;font-family:sans-serif;">Nutritional Values (g):</h5>',
                            unsafe_allow_html=True)
                        expander.dataframe(nutritions_df)
                        expander.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Ingredients:</h5>',
                                          unsafe_allow_html=True)
                        for ingredient in recipe['RecipeIngredientParts']:
                            expander.markdown(f"""
                                        - {ingredient}
                            """)
                        expander.markdown(
                            f'<h5 style="text-align: center;font-family:sans-serif;">Recipe Instructions:</h5>',
                            unsafe_allow_html=True)
                        for instruction in recipe['RecipeInstructions']:
                            expander.markdown(f"""
                                        - {instruction}
                            """)
                        expander.markdown(
                            f'<h5 style="text-align: center;font-family:sans-serif;">Cooking and Preparation Time:</h5>',
                            unsafe_allow_html=True)
                        expander.markdown(f"""
                                - Cook Time       : {recipe['CookTime']}min
                                - Preparation Time: {recipe['PrepTime']}min
                                - Total Time      : {recipe['TotalTime']}min
                            """)
        else:
            st.info('Couldn\'t find any recipes with the specified ingredients', icon="🙁")

    def display_overview(self, recommendations):
        if recommendations is not None:
            st.subheader('Overview:')
            col1, col2, col3 = st.columns(3)
            with col2:
                selected_recipe_name = st.selectbox('Select a recipe', [recipe['Name'] for recipe in recommendations])
            st.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Nutritional Values:</h5>',
                        unsafe_allow_html=True)
            for recipe in recommendations:
                if recipe['Name'] == selected_recipe_name:
                    selected_recipe = recipe
            options = {
                "title": {"text": "Nutrition values", "subtext": f"{selected_recipe_name}", "left": "center"},
                "tooltip": {"trigger": "item"},
                "legend": {"orient": "vertical", "left": "left", },
                "series": [
                    {
                        "name": "Nutrition values",
                        "type": "pie",
                        "radius": "50%",
                        "data": [{"value": selected_recipe[nutrition_value], "name": nutrition_value} for
                                 nutrition_value in self.nutrition_values],
                        "emphasis": {
                            "itemStyle": {
                                "shadowBlur": 10,
                                "shadowOffsetX": 0,
                                "shadowColor": "rgba(0, 0, 0, 0.5)",
                            }
                        },
                    }
                ],
            }
            st_echarts(options=options, height="600px", )
            st.caption('You can select/deselect an item (nutrition value) from the legend.')


title = "<h1 style='text-align: center;'>Meal Recommender</h1>"
st.markdown(title, unsafe_allow_html=True)

display = Display()

with st.form("recommendation_form"):
    st.header('Nutritional values:')
    Calories = st.slider('Calories', 0, 2000, 500)
    FatContent = st.slider('FatContent', 0, 100, 50)
    SaturatedFatContent = st.slider('SaturatedFatContent', 0, 13, 0)
    CholesterolContent = st.slider('CholesterolContent', 0, 300, 0)
    SodiumContent = st.slider('SodiumContent', 0, 2300, 400)
    CarbohydrateContent = st.slider('CarbohydrateContent', 0, 325, 100)
    FiberContent = st.slider('FiberContent', 0, 50, 10)
    SugarContent = st.slider('SugarContent', 0, 40, 10)
    ProteinContent = st.slider('ProteinContent', 0, 40, 10)
    nutritions_values_list = [Calories, FatContent, SaturatedFatContent, CholesterolContent, SodiumContent,
                              CarbohydrateContent, FiberContent, SugarContent, ProteinContent]
    st.header('Recommendation options:')
    nb_recommendations = st.slider('Number of recommendations', 5, 20, step=5)
    ingredients_include_txt = st.text_input('Specify ingredients to include in the recommendations separated by ";" :',
                                            placeholder='Ingredient1;Ingredient2;...')
    ingredients_exclude_txt = st.text_input('Specify ingredients to exclude in the recommendations separated by ";" :',
                                            placeholder='Ingredient1;Ingredient2;...')
    st.caption('Example: Milk;eggs;butter;chicken...')
    generated = st.form_submit_button("Generate")
if generated:
    with st.spinner('Generating recommendations...'):
        recommendation = Recommendation(nutritions_values_list, nb_recommendations, ingredients_include_txt, ingredients_exclude_txt)
        recommendations = recommendation.generate()
        st.session_state.recommendations = recommendations
    st.session_state.generated = True

if st.session_state.generated:
    with st.container():
        display.display_recommendation(st.session_state.recommendations)
    with st.container():
        display.display_overview(st.session_state.recommendations)
