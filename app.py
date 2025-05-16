import streamlit as st
import openai
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
from datetime import date as dt_date
import pickle
from pathlib import Path
import httpx
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI
http_client = httpx.Client()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=http_client
)

def load_family_preferences():
    try:
        with open('family_preferences.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

def save_family_preferences(preferences):
    with open('family_preferences.pkl', 'wb') as f:
        pickle.dump(preferences, f)

def get_weekly_menu(family_size, dietary_restrictions, family_details, leftover_ingredients):
    """Generate a weekly meal plan using OpenAI"""
    prompt = f"Create an easy healthy weekly meal plan for a family of {family_size} people.\n"
    prompt += "Focus only on breakfast and dinner for each day of the week.\n"
    prompt += "IMPORTANT: Use a limited set of ingredients across all meals to make shopping easier. Reuse ingredients in multiple meals when possible.\n"
    prompt += "Aim for simple recipes with 5-7 ingredients each.\n"
    if dietary_restrictions:
        prompt += f"Dietary restrictions: {dietary_restrictions}\n"
    if family_details:
        prompt += f"Family details: {family_details}\n"
    if leftover_ingredients:
        prompt += f"Use the following leftover ingredients: {leftover_ingredients}\n"
    prompt += "Format your response in two sections:\n"
    prompt += "1. MEAL PLAN: List each day with breakfast and dinner only. Format as: Day - Meal - Recipe Name - Main Ingredients (limit to 5-7 ingredients per recipe)\n"
    prompt += "2. SHOPPING LIST: Create a simplified, categorized shopping list with the minimum ingredients needed for the week. Consolidate similar ingredients and specify quantities.\n"
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

def find_photoshoot_studios(location, date, family_size):
    """Search for photoshoot studios on Shoott Photography website"""
    try:
        # Simulate real data from Shoott Photography
        studios = [
            {
                "name": "Shoott Photography Studio",
                "address": f"123 Photo St, {location}",
                "price": "$299",
                "rating": "4.8",
                "availability": True,
                "distance": "5 miles"
            },
            {
                "name": "Family Moments by Shoott",
                "address": f"456 Smile Ave, {location}",
                "price": "$399",
                "rating": "4.9",
                "availability": True,
                "distance": "3 miles"
            }
        ]
        return studios
    except Exception as e:
        st.error(f"Error searching for studios: {str(e)}")
        return []

def main():
    st.title("Family Helper App")
    st.write("Your AI-powered family meal prep and photoshoot booking assistant")

    # Create tabs for different features
    meal_prep, photoshoot = st.tabs(["Meal Prep", "Photoshoot Booking"])

    with meal_prep:
        st.header("Family Meal Prep")
        
        # Check if we have saved preferences
        saved_preferences = load_family_preferences()
        use_saved_preferences = False
        
        if saved_preferences:
            use_saved_preferences = st.checkbox("Use saved family preferences", value=True)
        
        # Family size and details
        st.subheader("Family Information")
        
        if use_saved_preferences:
            # Use saved preferences
            num_adults = saved_preferences["num_adults"]
            num_kids = saved_preferences["num_kids"]
            family_size = num_adults + num_kids
            st.info(f"Using saved preferences: {num_adults} adults and {num_kids} kids")
            
            # Generate family details string from saved preferences
            family_details = ""
            for member in saved_preferences["family_members"]:
                if member["type"] == "adult":
                    if member["name"] and member["preferences"]:
                        family_details += f"Adult: {member['name']}, Preferences: {member['preferences']}\n"
                else:  # kid
                    if member["name"]:
                        family_details += f"Child: {member['name']}, {member.get('age_group', 'Child')}, "
                        family_details += f"Preferences: {member['preferences']}\n"
            
            # Use saved dietary restrictions
            dietary_restrictions = saved_preferences["dietary_restrictions"]
            st.write(f"**Dietary Restrictions:** {dietary_restrictions if dietary_restrictions else 'None'}")
            
            # Show family members
            with st.expander("View Family Details"):
                for member in saved_preferences["family_members"]:
                    if member["name"]:
                        if member["type"] == "adult":
                            st.write(f"**{member['name']}** (Adult) - Preferences: {member['preferences']}")
                        else:  # kid
                            st.write(f"**{member['name']}** ({member.get('age_group', 'Child')}) - Preferences: {member['preferences']}")
        else:
            # Manual input
            col1, col2 = st.columns(2)
            with col1:
                num_adults = st.slider("Number of Adults", 1, 6, 2)
            with col2:
                num_kids = st.slider("Number of Kids", 0, 8, 2)
            
            family_size = num_adults + num_kids
            st.write(f"Total family size: {family_size}")
            
            # Expandable section for family member details
            with st.expander("Family Member Details (Optional)"):
                st.info("Add details about family members to personalize the meal plan.")
                family_details = ""
                
                # Adult details
                if num_adults > 0:
                    st.write("### Adults")
                    for i in range(num_adults):
                        col1, col2 = st.columns(2)
                        with col1:
                            name = st.text_input(f"Adult Name #{i+1}", key=f"adult_name_{i}")
                        with col2:
                            age = "Adult"
                        preferences = st.text_input(f"Food Preferences/Restrictions #{i+1}", key=f"adult_pref_{i}")
                        
                        if name or preferences:
                            family_details += f"Adult {i+1}: {name}, Preferences: {preferences}\n"
                
                # Kid details
                if num_kids > 0:
                    st.write("### Kids")
                    for i in range(num_kids):
                        col1, col2 = st.columns(2)
                        with col1:
                            name = st.text_input(f"Child Name #{i+1}", key=f"child_name_{i}")
                        with col2:
                            age = st.selectbox(f"Age Group #{i+1}", 
                                             ["Teen (13-18)", "Child (5-12)", "Young Child (1-4)", "Infant (< 1)"],
                                             key=f"child_age_{i}")
                        preferences = st.text_input(f"Food Preferences/Restrictions #{i+1}", key=f"child_pref_{i}")
                        
                        if name or preferences:
                            family_details += f"Child {i+1}: {name}, {age}, Preferences: {preferences}\n"
            
            # Dietary restrictions
            st.subheader("Dietary Information")
            dietary_restrictions = st.text_input("Family Dietary Restrictions (e.g., vegetarian, gluten-free)")
            
            # Save preferences
            if st.button("Save Family Preferences"):
                family_members = []
                for i in range(num_adults):
                    name = st.session_state.get(f"adult_name_{i}")
                    preferences = st.session_state.get(f"adult_pref_{i}")
                    if name or preferences:
                        family_members.append({"type": "adult", "name": name, "preferences": preferences})
                for i in range(num_kids):
                    name = st.session_state.get(f"child_name_{i}")
                    age = st.session_state.get(f"child_age_{i}")
                    preferences = st.session_state.get(f"child_pref_{i}")
                    if name or preferences:
                        family_members.append({"type": "kid", "name": name, "age_group": age, "preferences": preferences})
                save_family_preferences({"num_adults": num_adults, "num_kids": num_kids, "family_members": family_members, "dietary_restrictions": dietary_restrictions})
                st.success("Family preferences saved!")
        
        # Leftover ingredients
        st.subheader("Leftover Ingredients")
        st.info("Add ingredients you already have to reduce waste and save money.")
        leftover_ingredients = st.text_area("Leftover Ingredients to Use", 
                                        placeholder="Example: 2 bell peppers, half a bag of rice, chicken breast, etc.")
        
        # Generate menu
        if st.button("Generate Weekly Menu"):
            menu = get_weekly_menu(family_size, dietary_restrictions, family_details, leftover_ingredients)
            st.subheader("Your Weekly Menu")
            st.write(menu)

    with photoshoot:
        st.header("Photoshoot Booking")
        
        # Location input
        location = st.text_input("Location", "San Francisco, CA")
        
        # Date picker
        min_date = datetime.now().date() + timedelta(days=1)
        date = st.date_input("Desired Date", value=min_date, min_value=min_date)
        
        # Family size for photoshoot
        photoshoot_size = st.slider("Number of Family Members for Photoshoot", 1, 10, 4)
        
        # Search for studios
        if st.button("Find Photoshoot Studios"):
            studios = find_photoshoot_studios(location, date, photoshoot_size)
            st.subheader("Available Photoshoot Studios")
            for studio in studios:
                st.markdown(f"### {studio['name']}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Address:** {studio['address']}")
                    st.write(f"**Distance:** {studio['distance']}")
                with col2:
                    st.write(f"**Price:** {studio['price']}")
                    st.write(f"**Rating:** {studio['rating']}★")
                with col3:
                    if studio['availability']:
                        st.success("Available!")
                    else:
                        st.error("Not Available")
                st.write("---")
                
                # Add booking button
                if st.button(f"Book with Shoot Photography", key=f"book_{studio['name']}"):
                    st.success(f"Booking {studio['name']}...")
                    # In a real app, this would redirect to Shoott Photography's booking page
                    st.info(f"You'll be redirected to Shoott Photography's website to complete your booking.")

if __name__ == "__main__":
    main()
