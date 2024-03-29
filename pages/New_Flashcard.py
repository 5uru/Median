from datetime import datetime

import streamlit as st

from median.database import insert_flashcard_data
from median.file_reader import main as read_file
from median.generate_quizz import quiz

st.set_page_config(
    page_title="Add New Flashcard - Median",
    page_icon="🧊",
    layout="wide",
)


# Initialization
if "flashcard_data" not in st.session_state:
    st.session_state["flashcard_data"] = []

if "topics" not in st.session_state:
    st.session_state["topics"] = []

if "rerun" not in st.session_state:
    st.session_state["rerun"] = False


st.title("Create New Flashcard")
topics = None
quiz_collection = None
rerun = False
with st.form("my_form"):
    flashcard_name = st.text_input("Flashcard Name")

    data = st.file_uploader("Upload data file", type=["pdf", "docx", "md", "txt"])
    col1, col2 = st.columns(2)
    with col1:
        submit = st.form_submit_button("Generate Cards")
        if submit:
            if flashcard_name == "":
                st.error("Flashcard name is required")
            elif data is None:
                st.error("Data file is required")
            else:
                st.session_state["rerun"] = True
    with col2:
        if st.session_state["rerun"]:
            rerun = st.form_submit_button("Regenerate Cards")

if submit & (data is not None) & (flashcard_name != ""):
    content = read_file(data, data.type)
    quiz_collection, topics = quiz(content)
    st.session_state["topics"] = topics
    st.session_state["flashcard_data"] = quiz_collection

if rerun and (data is not None) and (flashcard_name != ""):
    content = read_file(data, data.type)
    quiz_collection, topics = quiz(content)
    st.session_state["topics"] = topics
    st.session_state["flashcard_data"].extend(quiz_collection)


if st.session_state["flashcard_data"] and st.session_state["topics"]:

    col1, col2 = st.columns([9, 1])

    with col1:
        # HTML content with styling
        html_content = f"""
        <div>
            <span ><b>Topics:   </b> </span> 
            <span style="font-weight: bold; color: #008080;">{st.session_state["topics"][0].upper()} ,</span>
            <span style="font-weight: bold; color: #FFA500;">{st.session_state["topics"][1].upper()} ,</span>
            <span style="font-weight: bold; color: #FF7F50;">{st.session_state["topics"][2].upper()} , </span>
            <span style="font-weight: bold; color: #708090;">{st.session_state["topics"][3].upper()} ,</span>
            <span style="font-weight: bold; color: #808000;">{st.session_state["topics"][4].upper()} \n</span> 
        </div>
        """

        # Display the HTML content in Streamlit
        st.markdown(html_content, unsafe_allow_html=True)
    with col2:
        with st.popover("Add Card", use_container_width=True):
            new_question = st.text_area("New Question")
            new_answer = st.text_area("New Answer")
            if st.button("Add", type="primary"):
                st.session_state["flashcard_data"].insert(
                    0, {"question": new_question, "answer": new_answer}
                )
                st.rerun()


# Load the flashcard_data from the temporary file
if st.session_state["flashcard_data"]:
    for quiz_index, flashcard_quiz in enumerate(st.session_state["flashcard_data"]):
        st.divider()
        with st.container():
            st.write("#### Question: ")
            st.write(flashcard_quiz["question"])
            st.write("#### Answer: ")
            st.write(flashcard_quiz["answer"])
            col1, col2 = st.columns(2)
            with col2:
                if st.button(
                    "Delete", use_container_width=True, type="primary", key=quiz_index
                ):
                    st.session_state["flashcard_data"].pop(quiz_index)
                    st.rerun()

            with col1:
                with st.popover("Edit Card", use_container_width=True):
                    st.write("#### Question: ")
                    new_question = st.text_area(
                        "New Question",
                        flashcard_quiz["question"],
                        key=f"{quiz_index}new_question",
                    )
                    st.write("#### Answer: ")
                    new_answer = st.text_area(
                        "New Answer",
                        flashcard_quiz["answer"],
                        key=f"{quiz_index}new_answer",
                    )
                    if st.button("Update", key=f"{quiz_index}_replace"):
                        st.session_state["flashcard_data"][quiz_index][
                            "question"
                        ] = new_question
                        st.session_state["flashcard_data"][quiz_index][
                            "answer"
                        ] = new_answer
                        st.rerun()

    st.divider()
    if st.button("Create Flashcards", use_container_width=True, type="primary"):
        for flashcard_quiz in st.session_state["flashcard_data"]:
            insert_flashcard_data(
                question=flashcard_quiz["question"],
                answer=flashcard_quiz["answer"],
                model=str((4.0, 4.0, 24.0)),
                last_test=datetime.now(),
                total=0,
                flashcard_name=flashcard_name,
            )
