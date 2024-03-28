import os
import pickle
import tempfile

import streamlit as st

from median.file_reader import main as read_file
from median.generate_quizz import quiz

st.set_page_config(
    page_title="Add New Flashcard - Median",
    page_icon="🧊",
    layout="wide",
)


def save_flashcard_data(flashcard_data):
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False)

    # Use pickle to serialize the flashcard_data
    with open(temp_file.name, "wb") as f:
        pickle.dump(flashcard_data, f)

    return temp_file.name


def load_flashcard_data(temp_file_name):
    # Check if the file exists
    if not os.path.exists(temp_file_name):
        # If not, create it and write an empty list to it
        with open(temp_file_name, "wb") as f:
            pickle.dump([], f)

    # Load the flashcard_data from the temporary file
    with open(temp_file_name, "rb") as f:
        flashcard_data = pickle.load(f)

    return flashcard_data


def modify_flashcard_data(temp_file_name, new_flashcard):
    # Load the existing flashcard_data
    flashcard_data = load_flashcard_data(temp_file_name)

    # Modify the flashcard_data
    flashcard_data.append(new_flashcard)

    # Save the modified flashcard_data
    save_flashcard_data(flashcard_data)


def add_flashcard_data(temp_file_name, question, answer):
    # Load the existing flashcard_data
    flashcard_data = load_flashcard_data(temp_file_name)

    # Create new flashcard
    new_flashcard = {"question": question, "answer": answer}

    # Add the new flashcard to flashcard_data
    flashcard_data.append(new_flashcard)

    # Save the modified flashcard_data
    save_flashcard_data(flashcard_data)


st.title("Create New Flashcard")
topics = None
quiz_collection = None
with st.form("my_form"):
    flashcard_name = st.text_input("Flashcard Name")

    data = st.file_uploader("Upload data file", type=["pdf", "docx", "md", "txt"])

    submit = st.form_submit_button("Create Flashcard")
    if submit:
        if flashcard_name == "":
            st.error("Flashcard name is required")
        elif data is None:
            st.error("Data file is required")

if submit & (data is not None) & (flashcard_name != ""):
    content = read_file(data, data.type)
    quiz_collection, topics = quiz(content)
st.write("Outside the form")


if quiz_collection and topics:
    # HTML content with styling
    html_content = f"""
    <div>
        <span ><b>Topics:   </b> </span> 
        <span style="font-weight: bold; color: #008080;">{topics[0].upper()} ,</span>
        <span style="font-weight: bold; color: #FFA500;">{topics[1].upper()} ,</span>
        <span style="font-weight: bold; color: #FF7F50;">{topics[2].upper()} , </span>
        <span style="font-weight: bold; color: #708090;">{topics[3].upper()} ,</span>
        <span style="font-weight: bold; color: #808000;">{topics[4].upper()} \n</span> 
    </div>
    """

    # Display the HTML content in Streamlit
    st.markdown(html_content, unsafe_allow_html=True)

    for q in quiz_collection:
        # add on flashcard_data
        add_flashcard_data("temp.txt", q["question"], q["answer"])


# Load the flashcard_data from the temporary file
flashcard_data = load_flashcard_data("temp.txt")

# Print the flashcard_data
for flashcard in flashcard_data:
    print(flashcard)
