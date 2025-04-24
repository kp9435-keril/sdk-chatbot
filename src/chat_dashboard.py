import streamlit as st
from constants import *
from azure_openai_client import AzureOpenAIClient


def on_submit():
    """
    Handle the submit button click event.
    """
    if st.session_state.chat_input:

        chat_input = st.session_state.chat_input.strip()
        st.session_state.chat_input = ""

        st.session_state.messages.append({"role": "user", "content": chat_input})

        chat_response = get_response_for_query(chat_input)
        next_suggestions = get_updated_suggestions(chat_input)

        st.session_state.messages.append({"role": "assistant", "content": chat_response.output_text})
        st.session_state.previous_response_id = chat_response.id
        st.session_state.suggestions = [next_suggestions.suggestion1, next_suggestions.suggestion2, next_suggestions.suggestion3]

def get_response_for_query(query):
    """
    Get the response for the given query using Azure OpenAI.
    """
    client = AzureOpenAIClient()
    response = client.get_response_for_query(query, st.session_state.previous_response_id)
    return response

def get_updated_suggestions(query):
    """
    Get updated suggestions based on the query.
    """
    client = AzureOpenAIClient()
    response = client.get_suggestions(query)
    return response

st.set_page_config(
    page_title="Zebra Printers Chatbot",
    page_icon=":speech_balloon:",
    layout="wide",
)

if "messages" not in st.session_state:
    st.session_state.messages = INITAL_MESSAGE_LIST

if "suggestions" not in st.session_state:
    st.session_state.suggestions = INITIAL_SUGGESTIONS

if "previous_response_id" not in st.session_state:
    st.session_state.previous_response_id = None

for message in st.session_state.messages:
    if message["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(message["content"])
    else:
        with st.chat_message("user"):
            st.markdown(message["content"])

with st._bottom:

    with st.container(border=True):

        row1col1, row1col2, row1col3 = st.columns(3, gap="small", vertical_alignment="center")
        with row1col1:
            if st.button(st.session_state.suggestions[0], use_container_width=True):
                st.session_state.chat_input = st.session_state.suggestions[0]
        with row1col2:
            if st.button(st.session_state.suggestions[1], use_container_width=True):
                st.session_state.chat_input = st.session_state.suggestions[1]
        with row1col3:
            if st.button(st.session_state.suggestions[2] , use_container_width=True):
                st.session_state.chat_input = st.session_state.suggestions[2]

        row2col1, row2col2 = st.columns([10, 1], gap="small", vertical_alignment="bottom")
        with row2col1:
            st.text_input(
                key="chat_input",
                label="Enter your prompt here!",
                label_visibility="collapsed",
                placeholder="Type your message...",
                autocomplete="off",
            )
        with row2col2:
            st.button(
                "Submit",
                key="submit_button",
                use_container_width=True,
                on_click=on_submit,
            )
        
        st.write("Kindly wait after clicking submit button, it may take a few seconds to respond.")
        