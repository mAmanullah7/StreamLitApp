import streamlit as st
from dotenv import load_dotenv
import os
from openai import OpenAI
import json
from datetime import datetime 

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CHAT_FOLDER = "Chats"
os.makedirs(CHAT_FOLDER, exist_ok=True)
CHAT_INDEX_FILE = os.path.join(CHAT_FOLDER, "chat_index.json")
DEFAULT_SYSTEM_PROMPT = (
    "You are an Associate Data Scientist at Tredence. You have been working on a project to analyze customer feedback data for a retail company. "
    "Your task is to identify key themes and sentiments in the feedback, and provide actionable insights to improve customer satisfaction."
)

def save_chat(chat_name, messages):
    filepath = os.path.join(CHAT_FOLDER, chat_name)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=4)

def load_chat(Chat_name):
    filepath = os.path.join(CHAT_FOLDER, Chat_name)

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_chat_index():
    if not os.path.exists(CHAT_INDEX_FILE):
        return {}

    with open(CHAT_INDEX_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_chat_index(index):
    with open(CHAT_INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=4)


def create_chat_messages():
    return [{"role": "system", "content": DEFAULT_SYSTEM_PROMPT}]


def make_chat_title(messages, fallback_name):
    for message in messages:
        if message.get("role") == "user" and message.get("content"):
            title = message["content"].strip().splitlines()[0]
            return title[:40] + ("..." if len(title) > 40 else "")

    return fallback_name.replace(".json", "").replace("_", " ").title()


def ensure_chat_index_entry(chat_name, messages, pinned=False):
    index = load_chat_index()
    existing = index.get(chat_name, {})
    existing["title"] = make_chat_title(messages, chat_name)
    existing["pinned"] = existing.get("pinned", pinned)
    existing["updated_at"] = existing.get("updated_at", datetime.now().isoformat())
    index[chat_name] = existing
    save_chat_index(index)


def create_new_chat():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    chat_name = f"chat_{timestamp}.json"
    messages = create_chat_messages()
    st.session_state.chat_name = chat_name
    st.session_state.messages = messages
    save_chat(chat_name, messages)
    ensure_chat_index_entry(chat_name, messages)


def load_or_create_initial_chat():
    chat_files = [file_name for file_name in os.listdir(CHAT_FOLDER) if file_name.endswith(".json") and file_name != os.path.basename(CHAT_INDEX_FILE)]
    chat_files.sort(reverse=True)

    if "chat_name" in st.session_state and "messages" in st.session_state:
        return

    if chat_files:
        st.session_state.chat_name = chat_files[0]
        st.session_state.messages = load_chat(chat_files[0])
        ensure_chat_index_entry(chat_files[0], st.session_state.messages)
        return

    create_new_chat()


def get_chat_entries():
    index = load_chat_index()
    entries = []

    for file_name in os.listdir(CHAT_FOLDER):
        if not file_name.endswith(".json") or file_name == os.path.basename(CHAT_INDEX_FILE):
            continue

        file_path = os.path.join(CHAT_FOLDER, file_name)
        if not os.path.exists(file_path):
            continue

        messages = load_chat(file_name)
        metadata = index.get(file_name, {})
        title = metadata.get("title") or make_chat_title(messages, file_name)
        pinned = bool(metadata.get("pinned", False))
        updated_at = os.path.getmtime(file_path)

        index[file_name] = {
            "title": title,
            "pinned": pinned,
            "updated_at": metadata.get("updated_at", datetime.fromtimestamp(updated_at).isoformat()),
        }

        entries.append(
            {
                "name": file_name,
                "title": title,
                "pinned": pinned,
                "updated_at": updated_at,
            }
        )

    save_chat_index(index)
    entries.sort(key=lambda item: (not item["pinned"], -item["updated_at"], item["title"].lower()))
    return entries


def activate_chat(chat_name):
    if st.session_state.get("chat_name") != chat_name:
        st.session_state.chat_name = chat_name
        st.session_state.messages = load_chat(chat_name)


def toggle_pin(chat_name):
    index = load_chat_index()
    metadata = index.get(chat_name, {})
    metadata["pinned"] = not bool(metadata.get("pinned", False))
    metadata["title"] = metadata.get("title") or make_chat_title(load_chat(chat_name), chat_name)
    metadata["updated_at"] = metadata.get("updated_at", datetime.now().isoformat())
    index[chat_name] = metadata
    save_chat_index(index)


st.sidebar.title("Chats")

if st.sidebar.button("New Chat", use_container_width=True):
    create_new_chat()
    st.rerun()

load_or_create_initial_chat()

chat_entries = get_chat_entries()

st.sidebar.markdown("### Pinned")
pinned_entries = [entry for entry in chat_entries if entry["pinned"]]
if pinned_entries:
    for entry in pinned_entries:
        title_col, pin_col = st.sidebar.columns([0.82, 0.18])
        if title_col.button(entry["title"], key=f"open_{entry['name']}", use_container_width=True):
            activate_chat(entry["name"])
            st.rerun()
        if pin_col.button("Unpin", key=f"pin_{entry['name']}", use_container_width=True):
            toggle_pin(entry["name"])
            st.rerun()
else:
    st.sidebar.caption("No pinned chats yet.")

st.sidebar.markdown("### Recent")
recent_entries = [entry for entry in chat_entries if not entry["pinned"]]
if recent_entries:
    for entry in recent_entries:
        title_col, pin_col = st.sidebar.columns([0.82, 0.18])
        if title_col.button(entry["title"], key=f"open_{entry['name']}", use_container_width=True):
            activate_chat(entry["name"])
            st.rerun()
        if pin_col.button("Pin", key=f"pin_{entry['name']}", use_container_width=True):
            toggle_pin(entry["name"])
            st.rerun()
else:
    st.sidebar.caption("No chats found.")

st.title("Tredence Data Science Assistant")

for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
    
promt = st.chat_input("Enter your query or request for analysis here...")
if promt:
    st.chat_message("user").markdown(promt)
    st.session_state.messages.append({"role": "user", "content": promt})

    with st.spinner("Assistant is typing..."):
        response = client.responses.create(
            model="gpt-4o-mini",
            input=st.session_state.messages,
        )

        answer = response.output_text
        st.chat_message("assistant").markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

        save_chat(st.session_state.chat_name, st.session_state.messages)
    ensure_chat_index_entry(st.session_state.chat_name, st.session_state.messages, pinned=load_chat_index().get(st.session_state.chat_name, {}).get("pinned", False))

