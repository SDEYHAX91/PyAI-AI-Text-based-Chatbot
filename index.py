
from groq import Groq
import streamlit as st
import time

SYSTEM_MESSAGE = {
    "role": "system",
    "content": "you are a helpful assistant."
}
chat_messages = [SYSTEM_MESSAGE]

st.set_page_config(
    page_title="Personal Assistant",
    page_icon=":robot_face:",
    layout="centered", 
    initial_sidebar_state="auto", 
    menu_items=None
)

st.header("Personal Assistant :rocket:")

with st.expander("Disclaimer"):
    st.write('''
        This is just for the learning purpose
    ''')

with st.sidebar:
    # new_chat = st.button(label="New Chat", type="secondary", help="Click here to start a new chat!")
    col1, col2 = st.columns(2)
    st.title("Groq API Key")
    groq_api_key = st.text_input("Groq API Key",type="password")
    with col1:
        st.logo(
            image="https://www.pantherschools.com/wp-content/uploads/2022/02/cropped-logoblack.png",
            size="large",
            link=None
        )

client = Groq(api_key= groq_api_key )

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "How can I help you today?"
    })

for history in st.session_state.messages:
    with st.chat_message(history['role']):
        st.write(history['content'])

def stream_data(chat_response):
    for word in chat_response:
        yield word
        time.sleep(0.02)

user_input = st.chat_input("Say something")
if user_input:

    if not groq_api_key.startswith("gsk_"):
        st.warning("Please enter your Groq API key!", icon="⚠")

    if groq_api_key.startswith("gsk_"):
        with st.chat_message("user"):
            st.write(user_input)
            st.session_state.messages.append({
                "role": "user",
                "content": user_input
            })
        chat_messages.append({
            "role": "user",
            "content": user_input
        })
        with st.chat_message("assistant"):
            chat_completion = client.chat.completions.create(
                messages=chat_messages,
                model="llama-3.3-70b-versatile",
                temperature=0.5,
                max_completion_tokens=1024,
                top_p=1,
                stop=None,
                stream=False,
            )
            bot_response = chat_completion.choices[0].message.content
            st.session_state.messages.append({
                "role": "assistant",
                "content": bot_response
            })
            st.write( bot_response )
            # st.write_stream( stream_data(bot_response))
            st.feedback(
                "thumbs"
            )
