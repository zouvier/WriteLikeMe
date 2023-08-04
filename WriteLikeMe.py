import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True
    
if check_password():
    @st.cache_data()
    def fetch_content_from_link(link):
        response = requests.get(link)
        soup = BeautifulSoup(response.content, "html.parser")
        text = ' '.join([p.text for p in soup.find_all('p')])
        return text

    def get_input():
        input_type = st.selectbox("Select input type", ["Text","Link", "File"])
        if input_type == 'Text':
            return st.text_area("Enter the text:"), input_type
        elif input_type == "File":
            uploaded_file = st.file_uploader("Upload a file:")
            if uploaded_file:
                text = uploaded_file.read().decode('utf-8')
                return text, input_type
            else:
                return None, input_type
        elif input_type == "Link":
            link = st.text_input("Enter the link:")
            if link:
                text = fetch_content_from_link(link)
                print(text)
                return text, input_type
            else:
                return None, input_type
        

    def get_prompt():
        return st.text_input("Enter the prompt:")

    def send_to_openai_api(input_data, input_type, prompt):
        # Process input_data and send it to OpenAI API using the prompt
        custom_instruction = f"Use the following {input_type.lower()} as a reference to learn my writting style: {input_data} \n\n"
        full_prompt = f"{custom_instruction}\n{prompt}"

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                    {"role": "user", "content": prompt}
                ],
            n=1,
            stop=None,
            temperature=0.7,
        )

        # Return the AI-generated text
        return response.choices[0].message.content

    def main():
        st.title("WriteLikeMe!")
        input_data, input_type = get_input()
        prompt = "respond to the following using my writting style: " + get_prompt()
        
        previous_outputs = []
        if "previous_outputs" in st.session_state:
            previous_outputs = st.session_state.previous_outputs

        if st.button("Submit"):
            ai_response = send_to_openai_api(input_data, input_type, prompt)
            st.write(ai_response)
            previous_outputs.append(ai_response)
            st.session_state.previous_outputs = previous_outputs

        st.sidebar.title("Previous Outputs")
        for i, output in enumerate(previous_outputs):
            with st.sidebar.expander(f"Output {i + 1}"):
                st.write(output)

    if __name__ == "__main__":
        main()