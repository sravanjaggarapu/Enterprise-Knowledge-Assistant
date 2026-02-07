import streamlit as st
import requests
import os

st.set_page_config(page_title="Enterprise Knowledge Assistant", layout="wide")
st.title("🧠 Enterprise Knowledge Assistant")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sources" not in st.session_state:
    st.session_state.sources = []

# Display chat history
st.subheader("📝 Chat History")
for message in st.session_state.messages:
    with st.chat_message("user"):
        st.write(message["user"])
    with st.chat_message("assistant"):
        st.write(message["assistant"])

# Input section
st.subheader("💬 Ask a Question")
question = st.text_input("Type your question here:")

if st.button("Send") and question:
    # Add to chat history
    st.session_state.messages.append({"user": question, "assistant": ""})
    
    # Call backend
    try:
        response = requests.post(
            "http://backend:8000/ask",
            json={"question": question, "chat_history": st.session_state.messages[:-1]}
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "No answer received")
            sources = data.get("sources", [])
            
            # Update last message with answer
            st.session_state.messages[-1]["assistant"] = answer
            
            # Store sources
            if sources:
                st.session_state.sources = sources
            
            # Rerun to show updated chat
            st.rerun()
        else:
            st.error("Backend not running.")
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Please run: `python -m uvicorn backend.main:app --reload`")

# Display source documents
if st.session_state.sources:
    st.subheader("📄 Source Documents Used")
    for source in st.session_state.sources:
        filename = os.path.basename(source)
        st.info(f"📖 {filename}")

# Clear chat button
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.session_state.sources = []
    st.rerun()
