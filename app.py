import streamlit as st
import pandas as pd
import openai

# Setup the OpenAI API client using the secret API key
openai.api_key = st.secrets["API_key"]["api_key"]

# Function to generate response from GPT API
def generate_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,  # Increase max_tokens to allow for more detailed responses
        temperature=0.7,
    )
    return response.choices[0].message['content'].strip()

# Function to fetch response and store it in session state
def fetch_response(prompt, session_key):
    try:
        response = generate_response(prompt)
        st.session_state[session_key] = response
    except Exception as e:
        st.session_state[session_key] = f"Error: {str(e)}"

# Function to format dish details
def format_dish_details(details):
    lines = details.split('\n')
    formatted_details = ""
    for line in lines:
        if line.strip():
            if "Description:" in line:
                formatted_details += f"\n**Description:** {line.split('Description:')[1].strip()}\n"
            elif "Allergens:" in line:
                formatted_details += f"\n**Allergens:**\n"
            elif "Nutritional Facts:" in line:
                formatted_details += f"\n**Nutritional Facts:**\n"
            elif "Ingredients:" in line:
                formatted_details += f"\n**Ingredients:**\n"
            elif "Instructions:" in line:
                formatted_details += f"\n**Instructions:**\n"
            elif "Alternative Ingredients:" in line:
                formatted_details += f"\n**Alternative Ingredients:**\n"
            else:
                formatted_details += f"{line.strip()}\n"
    return formatted_details

# Main function to run the Streamlit app
def main():
    st.title("DishGenie")
    st.subheader("DishGenie allows users to find dishes based on their preferred cuisine and available ingredients using OpenAI GPT-3.5-turbo")
    st.text("Almera J. Valladolid\n"
            "BSCS 3-B AI\n"
            "West Visayas State University")
    
    # Initialize session state variables if they don't exist
    if 'level' not in st.session_state:
        st.session_state.level = 1
        st.session_state.prompt = []

    # Step 1: Ask the user for their preferred cuisine
    cuisines = ["Filipino", "Japanese", "Chinese", "Korean", "Italian"]
    if st.session_state.level == 1:
        cuisine = st.selectbox("Select your preferred cuisine:", cuisines)
        if st.button("Submit Cuisine", key="cuisine"):
            st.session_state.prompt.append(f"My preferred cuisine is {cuisine}.")
            st.session_state.level += 1

    # Step 2: Ask the user for the main ingredient and condiments
    if st.session_state.level == 2:
        main_ingredient = st.text_input("Enter the main ingredient you have:")
        condiments = st.text_input("Enter at least 3 condiments you have (comma-separated):")
        if st.button("Submit Ingredients", key="ingredients"):
            condiments_list = [condiment.strip() for condiment in condiments.split(",")]
            if len(main_ingredient) > 0 and len(condiments_list) >= 3:
                st.session_state.prompt.append(f"I have {main_ingredient} as the main ingredient and {', '.join(condiments_list)} as condiments.")
                st.session_state.level += 1
            else:
                st.warning("Please enter at least one main ingredient and at least three condiments.")

    # Step 3: Generate dish recommendations
    if st.session_state.level == 3:
        cuisine = st.session_state.prompt[0].split()[-1].strip(".")
        main_ingredient = st.session_state.prompt[1].split()[2]
        condiments_list = st.session_state.prompt[1].split("and")[1].strip().split(", ")
        prompt = f"Recommend the top 5 {cuisine} dishes that can be made with {main_ingredient} and the following condiments: {', '.join(condiments_list)}."
        
        if 'dish_recommendations' not in st.session_state:
            fetch_response(prompt, 'dish_recommendations')

        if 'dish_recommendations' in st.session_state:
            if st.session_state.dish_recommendations is None or "Error" in st.session_state.dish_recommendations:
                st.error(st.session_state.dish_recommendations)
            else:
                st.write("Here are the top 5 recommended dishes:")
                dish_recommendations = [line.strip() for line in st.session_state.dish_recommendations.split('\n') if line.strip() and not line.lower().startswith("here are") and not line.lower().startswith("these are just") and not line.lower().startswith("you can also")]
                selected_dish = st.radio("Select a dish to get more details:", dish_recommendations)
                if st.button("Submit Dish Choice", key="dish_choice"):
                    st.session_state.selected_dish = selected_dish
                    st.session_state.level += 1

    # Step 4: Provide detailed information about the selected dish
    if st.session_state.level == 4:
        selected_dish = st.session_state.selected_dish.split(". ")[1] if ". " in st.session_state.selected_dish else st.session_state.selected_dish
        prompt = f"Provide detailed information about the dish {selected_dish}, including its description, allergens, nutritional facts, ingredients, instructions, and alternative ingredients."
        
        if 'dish_details' not in st.session_state:
            fetch_response(prompt, 'dish_details')

        if 'dish_details' in st.session_state:
            if st.session_state.dish_details is None or "Error" in st.session_state.dish_details:
                st.error(st.session_state.dish_details)
            else:
                st.write(f"**{selected_dish}:**")
                formatted_details = format_dish_details(st.session_state.dish_details)
                st.markdown(formatted_details)

                # Provide a button to start over the process
                if st.button("Start Over"):
                    st.session_state.level = 1
                    st.session_state.prompt = []
                    st.session_state.dish_recommendations = None
                    st.session_state.selected_dish = None
                    st.session_state.dish_details = None
                    st.experimental_rerun()

if __name__ == "__main__":
    main()
