import streamlit as st
from datetime import datetime, timedelta
from groq import Groq
# Set page config to wide mode and add custom title
st.set_page_config(
    page_title="PyAI Chatbot",
    page_icon="gear",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define all functions at the top
def search_chats(query):
    results = []
    for chat_id, chat_data in st.session_state.chat_history.items():
        # Search in chat title
        if query.lower() in chat_data["title"].lower():
            results.append((chat_id, chat_data))
            continue
        
        # Search in messages
        for message in chat_data["messages"]:
            if query.lower() in message["content"].lower():
                results.append((chat_id, chat_data))
                break
    
    return results

def reset_session_state():
    st.session_state.chat_history = {}  # {chat_id: {"title": str, "messages": list, "created_at": datetime}}
    st.session_state.current_chat_id = None
    st.session_state.messages = []

def create_new_chat():
    # Check if there's an empty chat we can use
    for chat_id, chat_data in st.session_state.chat_history.items():
        if not chat_data["messages"]:
            st.session_state.current_chat_id = chat_id
            st.session_state.messages = []
            return chat_id

    # If no empty chat found, create a new one
    chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.chat_history[chat_id] = {
        "title": "New Chat",
        "messages": [],
        "created_at": datetime.now()
    }
    st.session_state.current_chat_id = chat_id
    st.session_state.messages = []
    return chat_id

# Initialize session state variables
if 'chat_history' not in st.session_state:
    reset_session_state()
    create_new_chat()  # Create initial chat
if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'show_search' not in st.session_state:
    st.session_state.show_search = False
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

SYSTEM_MESSAGE = {
    "role": "system",
    "content": ""
}

chat_messages = [SYSTEM_MESSAGE]

# Ensure all chat history entries have created_at field
for chat_id, chat_data in st.session_state.chat_history.items():
    if isinstance(chat_data, dict) and 'created_at' not in chat_data:
        chat_data['created_at'] = datetime.now()
    elif not isinstance(chat_data, dict):
        # Convert old format to new format
        st.session_state.chat_history[chat_id] = {
            "title": chat_data,
            "messages": [],
            "created_at": datetime.now()
        }

def update_chat_title(chat_id, messages):
    if messages:
        for message in messages:
            if message["role"] == "user":
                title = message["content"][:30] + "..." if len(message["content"]) > 30 else message["content"]
                st.session_state.chat_history[chat_id]["title"] = title
                break

def get_categorized_chats():
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
        created_at = chat_data.get("created_at", now)  # Default to now for old entries
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

    # Sort chats within each category
    for category in categories.values():
        category.sort(key=lambda x: x[1].get('created_at', datetime.now()), reverse=True)

    return categories


# Add user menu at the top of the app
col1, col2 = st.columns([3, 1])

# Add container for main content
main_content = st.container()

with main_content:
    st.header("PyAI: Your Assistant Chatbot :rocket:")
    st.text("An AI Chatbot made using Python, Groq and Streamlit.")
    # Sidebar
    with st.sidebar:
        # Logo and title
        st.title("PyAI")
        groq_api_key = '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'
        client = Groq(api_key= groq_api_key )
        # New chat and search buttons
        col1, col2 = st.columns([5, 1])
        with col1:
            with st.container():
                if st.button("+ New chat", use_container_width=True, key="new_chat_btn"):
                    new_chat_id = create_new_chat()
                    st.rerun()
        with col2:
            if st.button("🔍", key="search_btn", help="Search in chat history"):
                st.session_state.show_search = True
                st.rerun()

        # Search interface
        if st.session_state.show_search:
            search_query = st.text_input("Search chats", value=st.session_state.search_query, key="search_input")
            if search_query != st.session_state.search_query:
                st.session_state.search_query = search_query
                st.rerun()

            if search_query:
                search_results = search_chats(search_query)
                if search_results:
                    st.markdown("### Search Results")
                    for chat_id, chat_data in search_results:
                        is_active = chat_id == st.session_state.current_chat_id
                        if st.button(
                            chat_data["title"],
                            key=f"search_{chat_id}",
                            use_container_width=True,
                            type="secondary",
                            disabled=is_active,
                        ):
                            st.session_state.current_chat_id = chat_id
                            st.session_state.messages = chat_data["messages"]
                            st.rerun()
                else:
                    st.info("No results found")
            
            if st.button("Clear Search", key="clear_search"):
                st.session_state.show_search = False
                st.session_state.search_query = ""
                st.rerun()

        # Display categorized chat history
        if not st.session_state.show_search:
            categories = get_categorized_chats()
            
            for category, chats in categories.items():
                if chats:  # Only show categories that have chats
                    st.markdown(f"<div class='chat-history-category'>{category}</div>", unsafe_allow_html=True)
                    for chat_id, chat_data in chats:
                        title = chat_data["title"]
                        is_active = chat_id == st.session_state.current_chat_id
                        
                        if st.button(
                            title,
                            key=f"chat_{chat_id}",
                            use_container_width=True,
                            type="secondary",
                            disabled=is_active,
                        ):
                            st.session_state.current_chat_id = chat_id
                            st.session_state.messages = chat_data["messages"]
                            st.rerun()

# Main chat interface
if st.session_state.current_chat_id is None:
    st.markdown("# What can I help with?")
    # Create a default chat if none exists
    if not st.session_state.chat_history:
        create_new_chat()
else:
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Let us chat together"):
    
    
        if not groq_api_key.startswith("gsk_"):
            st.warning("There must be error from Server.", icon="⚠")

        if groq_api_key.startswith("gsk_"):
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": prompt})
            chat_messages.append({
                "role": "user",
                "content": prompt
            })
            chat_completion = client.chat.completions.create(
                messages=chat_messages,
                model="llama-3.3-70b-versatile",
                temperature=0.5,
                max_completion_tokens=1024,
                top_p=1,
                stop=None,
                stream=False,
            )

            st.session_state.messages.append({"role": "assistant", "content": chat_completion.choices[0].message.content})
            chat_messages.append({
                "role": "assiatant",
                "content": chat_completion.choices[0].message.content
            })
            # Update the chat history
            current_chat_id = st.session_state.current_chat_id
            st.session_state.chat_history[current_chat_id]["messages"] = st.session_state.messages
            
            # Update the chat title if it's still "New Chat"
            if st.session_state.chat_history[current_chat_id]["title"] == "New Chat":
                update_chat_title(current_chat_id, st.session_state.messages)
            
            st.rerun()