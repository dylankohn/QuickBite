import streamlit as st
import json
import requests
import re
import openai
import os

# Load settings from config.json
def load_settings():
    with open("config.json", "r") as f:
        return json.load(f)

settings = load_settings()

# Apply custom styles using Streamlit's Markdown
st.markdown(
    f"""
    <style>
        body {{
            background-color: {settings["background_color"]};
            color: {settings["text_color"]};
            font-family: {settings["font"]};
        }}
        .stApp {{
            background-color: {settings["background_color"]};
        }}
        .stSidebar {{
            background-color: {settings["sidebar_background"]};
        }}
        .stButton > button {{
            background-color: {settings["primary_color"]};
            color: white;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# File to store saved ingredients
SAVE_FILE = "saved_ingredients.json"

def load_saved_ingredients():
    try:
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_ingredients():
    with open(SAVE_FILE, "w") as f:
        json.dump(st.session_state.saved_ingredients, f)

def delete_ingredient(ingredient):
    if ingredient in st.session_state.saved_ingredients:
        st.session_state.saved_ingredients.remove(ingredient)
        save_ingredients()

if "saved_ingredients" not in st.session_state:
    st.session_state.saved_ingredients = load_saved_ingredients()

if "selected_ingredients" not in st.session_state:
    st.session_state.selected_ingredients = []

if "new_ingredient" not in st.session_state:
    st.session_state.new_ingredient = ""

# Helper function: Parse ingredient string and detect quantity
def parse_ingredient(ingredient):
    match = re.match(r"(\d+)?\s*(.*)", ingredient)
    quantity = match.group(1) if match.group(1) else ""
    name = match.group(2).strip() if match.group(2) else ingredient
    return quantity, name

# Function to fetch recipes using ChatGPT API
def get_recipe(ingredients):
    prompt = f"Given these ingredients: {', '.join(ingredients)}, suggest a simple recipe that I can make using these ingredients and give me the steps and ingredient quantities. Don't give me recipes that include ingredients other than the ingredients I provide."
    data = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    with st.spinner("Generating recipe..."):
        response = openai.ChatCompletion.create(**data)

    if response:
        return response["choices"][0]["message"]["content"]
    else:
        return "Error: Unable to fetch recipe."

# Function to handle Enter key for adding ingredients
def add_ingredient():
    new_ingredient = st.session_state.new_ingredient.strip()
    if new_ingredient and new_ingredient not in st.session_state.saved_ingredients:
        st.session_state.saved_ingredients.append(new_ingredient)
        save_ingredients()
    elif new_ingredient:
        st.sidebar.warning("Ingredient already saved.")

    st.session_state.new_ingredient = ""

# Streamlit UI
st.title("Recipe Generator")

st.sidebar.title("Saved Ingredients")

st.sidebar.text_input(
    "Add a new ingredient:",
    key="new_ingredient",
    on_change=add_ingredient
)

for ingredient in st.session_state.saved_ingredients:
    col1, col2 = st.sidebar.columns([4, 1])
    with col1:
        if st.button(ingredient):
            if ingredient not in st.session_state.selected_ingredients:
                st.session_state.selected_ingredients.append(ingredient)
    with col2:
        if st.button("X", key=f"delete_{ingredient}"):
            delete_ingredient(ingredient)
            st.rerun()

selected_ingredients_str = ", ".join(st.session_state.selected_ingredients)

ingredients = st.text_area("Enter ingredients (comma-separated):", value=selected_ingredients_str)

if st.button("Get Recipe"):
    if ingredients:
        ingredient_list = [parse_ingredient(ing.strip())[1] for ing in ingredients.split(",")]
        recipe = get_recipe(ingredient_list)
        st.subheader("Generated Recipe")
        st.write(recipe)
    else:
        st.error("Please enter at least one ingredient.")
