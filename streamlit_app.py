import streamlit as st
from src.agent.agent import ReActAgent
from src.core.gemini_provider import GeminiProvider
from src.core.openai_provider import OpenAIProvider
from chatbot_baseline import OpenAIChatbot, GeminiChatbot
from src.telemetry.logger import logger


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Shopping Deal Assistant",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 Shopping Deal Assistant")


# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.header("⚙️ Settings")

    mode = st.radio(
        "Choose Mode:",
        ("🤖 Agent (Real-time API)", "💬 Chatbot (Training Data)")
    )

    provider_choice = st.radio(
        "LLM Provider:",
        ("Auto (Gemini → OpenAI)", "Gemini", "OpenAI")
    )

    if mode == "🤖 Agent (Real-time API)":
        max_steps = st.slider("Max Steps:", 3, 10, 5)
        cache_ttl = st.slider("Thời gian lưu Cache (giây):", 0, 3600, 300, 10)
    else:
        max_steps = None

    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()


# =========================
# SESSION STATE
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================
# DISPLAY CHAT HISTORY
# =========================
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])


# =========================
# FALLBACK LOGIC
# =========================
def run_with_fallback(prompt, mode, provider_choice, max_steps=None):
    """
    Run with:
    - Manual provider OR
    - Auto fallback (Gemini → OpenAI)
    """

    def run_gemini():
        if mode == "🤖 Agent (Real-time API)":
            llm = GeminiProvider()
            agent = ReActAgent(llm=llm, max_steps=max_steps)
            return agent.run(prompt)
        else:
            chatbot = GeminiChatbot()
            return chatbot.chat(prompt)

    def run_openai():
        if mode == "🤖 Agent (Real-time API)":
            llm = OpenAIProvider()
            agent = ReActAgent(llm=llm, max_steps=max_steps)
            return agent.run(prompt)
        else:
            chatbot = OpenAIChatbot()
            return chatbot.chat(prompt)

    # =====================
    # MANUAL MODE
    # =====================
    if provider_choice == "Gemini":
        return run_gemini(), "Gemini"

    if provider_choice == "OpenAI":
        return run_openai(), "OpenAI"

    # =====================
    # AUTO FALLBACK MODE
    # =====================
    try:
        result = run_gemini()
        return result, "Gemini"

    except Exception as gemini_error:
        logger.log_event("FALLBACK_TRIGGERED", {
            "provider": "gemini",
            "error": str(gemini_error)
        })

        print("⚠️ Gemini failed → switching to OpenAI")

        try:
            result = run_openai()
            return result, "OpenAI (fallback)"

        except Exception as openai_error:
            return {
                "response": f"""❌ Both providers failed:

**Gemini Error:** {str(gemini_error)}

**OpenAI Error:** {str(openai_error)}
"""
            }, "error"


# =========================
# CHAT INPUT
# =========================
if prompt := st.chat_input("Nhập câu hỏi của bạn..."):
    # User message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Assistant response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
<<<<<<< HEAD
                result, provider_used = run_with_fallback(
                    prompt, mode, provider_choice, max_steps
                )

                response = result["response"]

                # Show provider info
                if "fallback" in provider_used:
                    st.warning(f"⚠️ Fallback activated → {provider_used}")
=======
                if mode == "🤖 Agent (Real-time API)":
                    llm = GeminiProvider()
                    agent = ReActAgent(llm=llm, max_steps=max_steps, cache_ttl=cache_ttl)
                    result = agent.run(prompt)
                    response = result["response"]
                    
                    if result.get("cached"):
                        response += "\n\n> ⚡ *Kết quả được tự động lấy từ bộ nhớ đệm (Lịch sử truy vấn) - Tokens: 0*"
                        
                    role = "agent"
>>>>>>> 8f9cebbe1372552b8a6f7795f417a03d3279af71
                else:
                    st.caption(f"Provider: {provider_used}")

                st.markdown(response)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })

            except Exception as e:
                error_msg = f"❌ System Error: {str(e)}"

                st.error(error_msg)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })