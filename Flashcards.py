import ast
from datetime import datetime

import streamlit as st

from median.database import (
    select_all_unique_flashcard_names,
    select_flashcard_by_name,
    update_flashcard_data,
)
from median.spaced_repetition import recall_prediction, update_model

st.set_page_config(
    page_title="Flashcard - Median",
    page_icon="🧊",
    layout="wide",
)


col1, col2 = st.columns([2, 8])

with col1:
    option = st.selectbox(
        "Select a flashcard to view",
        select_all_unique_flashcard_names(),
        index=None,
    )

with col2:
    if option:
        st.markdown(f"## {option}")
        flashcard_data = select_flashcard_by_name(option)

        database = []
        for q in flashcard_data:
            try:
                model = ast.literal_eval(q[4])
                database.append(dict(factID=q[0], model=model, lastTest=q[5]))
            except SyntaxError:
                print(f"Invalid literal: {q[4]}")

        recall_list = recall_prediction(database)
        factID = recall_list[0]["factID"]
        if quizz := next((q for q in flashcard_data if q[0] == factID), None):
            st.divider()
            st.write(quizz[2])
            with st.status("Show Answer"):
                st.divider()
                st.write(quizz[3])
                st.divider()
                c1, c2, c3 = st.columns(3)
                result = None
                with c1:
                    st.write("< 1 min")
                    if st.button("Again"):
                        result = 0
                with c2:
                    st.write("< 10 min")
                    if st.button("Good"):
                        result = 1
                with c3:
                    st.write("2 days")
                    if st.button("Easy"):
                        result = 2

                if result is not None:
                    st.write(quizz)
                    new_model = update_model(
                        model=ast.literal_eval(quizz[4]),
                        result=result,
                        total=quizz[6] + 1,
                        last_test=quizz[5],
                    )

                    update_flashcard_data(
                        id_=quizz[0],
                        question=quizz[1],
                        answer=quizz[2],
                        model=new_model,
                        last_test=datetime.now(),
                        total=quizz[6] + 1,
                        flashcard_name=option,
                    )
                    st.rerun()
