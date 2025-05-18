import streamlit as st
from datetime import datetime, timedelta
from groq import Groq
import os
from dotenv import load_dotenv
import json

# Set page config to wide mode and add custom title
st.set_page_config(
    page_title="PyAI Chatbot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------ Utility Functions ------------------

def search_chats(query): #-------------------------- Search Chat
    results = []
    for chat_id, chat_data in st.session_state.chat_history.items():
        if query.lower() in chat_data["title"].lower():
            results.append((chat_id, chat_data))
            continue
        for message in chat_data["messages"]:
            if query.lower() in message["content"].lower():
                results.append((chat_id, chat_data))
                break
    return results

def reset_session_state(): #-------------------------- Reset Session Chat
    st.session_state.chat_history = {}
    st.session_state.current_chat_id = None
    st.session_state.messages = []

def create_new_chat(): #-------------------------- Create New Chat
    for chat_id, chat_data in st.session_state.chat_history.items():
        if not chat_data["messages"]:
            st.session_state.current_chat_id = chat_id
            st.session_state.messages = []
            return chat_id

    chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.chat_history[chat_id] = {
        "title": "New Chat",
        "messages": [],
        "created_at": datetime.now()
    }
    st.session_state.current_chat_id = chat_id
    st.session_state.messages = []
    return chat_id

def update_chat_title(chat_id, messages): #-------------------------- Update Chat Title
    for message in messages:
        if message["role"] == "user":
            title = message["content"][:30] + "..." if len(message["content"]) > 30 else message["content"]
            st.session_state.chat_history[chat_id]["title"] = title
            break

def get_categorized_chats():  #-------------------------- Categorize chat
    now = datetime.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)
    week_start = today - timedelta(days=today.weekday())
    last_week_start = week_start - timedelta(days=7)

    categories = {
        "Today": [],
        "Yesterday": [],
        "This Week": [],
        "Last Week": [],
        "Older": []
    }

    for chat_id, chat_data in st.session_state.chat_history.items():
        created_at = chat_data.get("created_at", now)
        if created_at >= today:
            categories["Today"].append((chat_id, chat_data))
        elif created_at >= yesterday:
            categories["Yesterday"].append((chat_id, chat_data))
        elif created_at >= week_start:
            categories["This Week"].append((chat_id, chat_data))
        elif created_at >= last_week_start:
            categories["Last Week"].append((chat_id, chat_data))
        else:
            categories["Older"].append((chat_id, chat_data))

    for cat in categories.values():
        cat.sort(key=lambda x: x[1].get('created_at', now), reverse=True)
    return categories

# ------------------ Initialize Session ------------------

if 'chat_history' not in st.session_state:
    reset_session_state()
    create_new_chat()

if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'show_search' not in st.session_state:
    st.session_state.show_search = False
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

# ------------------ Load Environment and Client ------------------

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = None
if api_key and api_key.startswith("gsk_"):
    client = Groq(api_key=api_key)

# ------------------ UI Layout ------------------

col1, col2 = st.columns([3, 1])
main_content = st.container()

with main_content:
    st.header("PyAI: Your Assistant Chatbot 🚀")
    st.text("An AI Chatbot made using Python, Groq and Streamlit.")

    if st.session_state.current_chat_id and st.session_state.messages:
        chat_data = st.session_state.messages

        export_format = st.selectbox("Export Format", ["Plain Text", "JSON"], key="export_format")

        if export_format == "Plain Text":
            export_content = ""
            for msg in chat_data:
                role = "You" if msg["role"] == "user" else "Assistant"
                export_content += f"{role}: {msg['content']}\n\n"
            mime = "text/plain"
            file_ext = "txt"

        else:  # JSON
            export_content = json.dumps(chat_data, indent=2)
            mime = "application/json"
            file_ext = "json"

        filename = f"chat_{st.session_state.current_chat_id}.{file_ext}"
        st.download_button(
            label="📥 Download Chat",
            data=export_content,
            file_name=filename,
            mime=mime,
            use_container_width=True
        )
    
    with st.sidebar:
        st.title("PyAI")

        col1, col2 = st.columns([5, 1])
        with col1:
            if st.button("+ New chat", use_container_width=True, key="new_chat_btn"):
                create_new_chat()
                st.rerun()
        with col2:
            if st.button("🔍", key="search_btn", help="Search in chat history"):
                st.session_state.show_search = True
                st.rerun()

        if st.session_state.show_search:
            search_query = st.text_input("Search chats", value=st.session_state.search_query, key="search_input")
            if search_query != st.session_state.search_query:
                st.session_state.search_query = search_query
                st.rerun()

            if search_query:
                results = search_chats(search_query)
                if results:
                    st.markdown("### Search Results")
                    for chat_id, chat_data in results:
                        is_active = chat_id == st.session_state.current_chat_id
                        if st.button(chat_data["title"], key=f"search_{chat_id}", use_container_width=True, disabled=is_active):
                            st.session_state.current_chat_id = chat_id
                            st.session_state.messages = chat_data["messages"]
                            st.rerun()
                else:
                    st.info("No results found")

            if st.button("Clear Search", key="clear_search"):
                st.session_state.show_search = False
                st.session_state.search_query = ""
                st.rerun()
        else:
            categories = get_categorized_chats()
            for category, chats in categories.items():
                if chats:
                    st.markdown(f"### {category}")
                    for chat_id, chat_data in chats:
                        is_active = chat_id == st.session_state.current_chat_id
                        if st.button(chat_data["title"], key=f"chat_{chat_id}", use_container_width=True, disabled=is_active):
                            st.session_state.current_chat_id = chat_id
                            st.session_state.messages = chat_data["messages"]
                            st.rerun()

# ------------------ Chat Interface ------------------

if st.session_state.current_chat_id is None:
    st.markdown("# What can I help with?")
    if not st.session_state.chat_history:
        create_new_chat()
else:
    # Display messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Input box
    if prompt := st.chat_input("Let us chat together"):
        if not api_key or not api_key.startswith("gsk_") or client is None:
            st.warning("Invalid or missing API key.", icon="⚠")
        else:
            # Append user message
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Generate response
            response = client.chat.completions.create(
                messages=st.session_state.messages,
                model="llama-3.3-70b-versatile",
                temperature=0.5,
                max_completion_tokens=1024,
                top_p=1,
                stream=False,
            )

            reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": reply})

            # Update chat history
            chat_id = st.session_state.current_chat_id
            st.session_state.chat_history[chat_id]["messages"] = st.session_state.messages

            # Update title
            if st.session_state.chat_history[chat_id]["title"] == "New Chat":
                update_chat_title(chat_id, st.session_state.messages)

            st.rerun()
