import streamlit as st
import requests
import json
import re
import openai
import os

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Helper function: Parse ingredient string and detect quantity
def parse_ingredient(ingredient):
    match = re.match(r"(\d+)?\s*(.*)", ingredient)
    quantity = match.group(1) if match.group(1) else ""
    name = match.group(2).strip() if match.group(2) else ingredient
    return quantity, name

# Function to fetch recipes using ChatGPT API
def get_recipe(ingredients):
    prompt = f"Given these ingredients: {', '.join(ingredients)}, suggest a simple recipe that I can make using these ingredients and give me the steps and ingredient quantities. Dont give me recipes that include ingredients other than the ingredients I provide."
    data = {
        "model": "gpt-4-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    response = openai.ChatCompletion.create(**data)
    
    if response:
        return response["choices"][0]["message"]["content"]
    else:
        return "Error: Unable to fetch recipe."

# Streamlit UI
st.title("AI-Powered Recipe Generator")

# Input for ingredients
ingredients = st.text_area("Enter ingredients (comma-separated):")

if st.button("Get Recipe"):
    if ingredients:
        ingredient_list = [parse_ingredient(ing.strip())[1] for ing in ingredients.split(",")]
        recipe = get_recipe(ingredient_list)
        st.subheader("Generated Recipe")
        st.write(recipe)
    else:
        st.error("Please enter at least one ingredient.")
