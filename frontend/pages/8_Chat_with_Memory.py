import streamlit as st
import requests
import time

st.set_page_config(page_title="Chat with Memory", page_icon="💬", layout="wide")

# Custom CSS for Glassmorphism and Animations
st.markdown("""
<style>
/* Base Theme */
.main {
    background-color: #0f1015;
    color: #e2e8f0;
}
/* Chat Container */
.chat-message {
    padding: 1.5rem; border-radius: 0.8rem; margin-bottom: 1.2rem; display: flex; align-items: flex-start;
    animation: fadeIn 0.5s ease-in-out;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.chat-message.user {
    background-color: rgba(108, 92, 231, 0.15);
    border: 1px solid rgba(108, 92, 231, 0.3);
    border-left: 5px solid #6c5ce7;
}
.chat-message.bot {
    background-color: rgba(0, 184, 148, 0.15);
    border: 1px solid rgba(0, 184, 148, 0.3);
    border-left: 5px solid #00b894;
}
.chat-message .avatar {
    width: 45px; height: 45px; border-radius: 50%;
    object-fit: cover; margin-right: 1.2rem;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.5rem;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
}
.chat-message.user .avatar { color: #6c5ce7; }
.chat-message.bot .avatar { color: #00b894; }
.chat-message .message {
    width: 100%;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

st.title("💬 Chat with Trust-Aware Memory")
st.markdown("""
<div style="background: rgba(108, 92, 231, 0.1); padding: 15px; border-radius: 10px; border-left: 4px solid #6c5ce7; margin-bottom: 30px;">
    <strong>Welcome to the Memory AI Assistant!</strong><br/>
    Ask any question, and the assistant will answer using <em>only</em> the verified facts stored in the Trust-Aware Memory database. It will completely ignore external unverified knowledge and cite its sources.
</div>
""", unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask about verified facts (e.g. 'When is GPT-5 releasing?')..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Prepare assistant response container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Add a sleek loading state
        with st.spinner("🧠 Querying verified memories..."):
            try:
                # Call backend API
                response = requests.post(
                    "http://localhost:8000/api/v1/chat", 
                    json={"query": prompt},
                    timeout=30
                )
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No response generated.")
                else:
                    answer = f"⚠️ Backend returned an error: {response.status_code}"
            except Exception as e:
                answer = f"⚠️ Connection error: Make sure the backend is running. Details: {str(e)}"
        
        # Simulate typing animation for a dynamic UI
        full_response = ""
        for chunk in answer.split(" "):
            full_response += chunk + " "
            time.sleep(0.04) # Typing speed
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(full_response + "▌")
        
        # Final response without cursor
        message_placeholder.markdown(full_response)
        
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
