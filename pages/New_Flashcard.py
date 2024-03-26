import streamlit as st

from median.file_reader import main as read_file
from median.generate_quizz import quiz

st.set_page_config(
    page_title="Add New Flashcard - Median",
    page_icon="🧊",
    layout="wide",
)


@st.cache(allow_output_mutation=True)
def get_flashcards():
    # Initialize an empty list for flashcards
    flashcards = []
    return flashcards


def add_flashcard(flashcards, question, answer):
    # Add a new flashcard to the list
    flashcards.append({"question": question, "answer": answer})


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
    # Get the cached list of flashcards
    flashcard_data = get_flashcards()

    for q in quiz_collection:
        # add pn flashcard_data
        add_flashcard(flashcard_data, q["question"], q["answer"])
        with st.form(f"{q['question']}"):
            st.write(f"Question: {q['question']}")
            st.write(f"Answer: {q['answer']}")
            # Every form must have a submit button.
            submitted = st.form_submit_button("Delete")
            if submitted:
                flashcard_data.remove(q)
                st.success("Flashcard deleted")
                st.rerun()

    st.write(flashcard_data)
