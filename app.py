import streamlit as st
from src.agent.agent import ShoppingAgent
from src.core.gemini_provider import GeminiProvider

@st.cache_resource
def load_agent():
    llm = GeminiProvider()
    return ShoppingAgent(llm)

agent = load_agent()

st.title("🛍️ Shopping AI Agent")

# lưu lịch sử chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# hiển thị chat cũ
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# input người dùng
if prompt := st.chat_input("Nhập câu hỏi (vd: tai nghe dưới 1 triệu)"):
    # user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    with st.chat_message("user"):
        st.write(prompt)

    # gọi agent
    with st.chat_message("assistant"):
        with st.spinner("Đang tìm sản phẩm..."):
            try:
                result = agent.run(prompt)
            except Exception as e:
                result = f"Lỗi: {str(e)}"

        st.write(result)

    # lưu lại
    st.session_state.messages.append({
        "role": "assistant",
        "content": result
    })