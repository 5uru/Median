import streamlit as st

from median.file_reader import main as read_file
from median.generate_quizz import quiz

st.set_page_config(
    page_title="Add New Flashcard - Median",
    page_icon="🧊",
    layout="wide",
)


st.title("Create New Flashcard")


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
    st.write(quiz(content))
st.write("Outside the form")
