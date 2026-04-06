import streamlit as st
from src.agent.agent import ReActAgent
from src.core.gemini_provider import GeminiProvider
from chatbot_baseline import GeminiChatbot

st.set_page_config(
    page_title="Shopping Deal Assistant",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 Shopping Deal Assistant")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    mode = st.radio(
        "Choose Mode:",
        ("🤖 Agent (Real-time API)", "💬 Chatbot (Training Data)")
    )
    
    if mode == "🤖 Agent (Real-time API)":
        max_steps = st.slider("Max Steps:", 3, 10, 5)
    else:
        max_steps = None
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖" if message["role"] == "agent" else "💬"):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Nhập câu hỏi của bạn..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    # Process response
    with st.chat_message("agent" if mode == "🤖 Agent (Real-time API)" else "chatbot", avatar="🤖" if mode == "🤖 Agent (Real-time API)" else "💬"):
        with st.spinner("Thinking..."):
            try:
                if mode == "🤖 Agent (Real-time API)":
                    llm = GeminiProvider()
                    agent = ReActAgent(llm=llm, max_steps=max_steps)
                    result = agent.run(prompt)
                    response = result["response"]
                    role = "agent"
                else:
                    chatbot = GeminiChatbot()
                    result = chatbot.chat(prompt)
                    response = result["response"]
                    role = "chatbot"
                
                st.markdown(response)
                st.session_state.messages.append({
                    "role": role,
                    "content": response
                })
            
            except Exception as e:
                error_msg = f"❌ Lỗi: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "agent" if mode == "🤖 Agent (Real-time API)" else "chatbot",
                    "content": error_msg
                })