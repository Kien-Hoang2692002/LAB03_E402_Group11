import streamlit as st
from src.agent.agent import ReActAgent
from src.core.gemini_provider import GeminiProvider
from src.core.openai_provider import OpenAIProvider
from chatbot_baseline import BaseChatbot
import statistics
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
# SIDEBAR & SESSION STATE
# =========================
# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "metrics" not in st.session_state:
    st.session_state.metrics = []

with st.sidebar:
    st.header("⚙️ Settings")    
    
    # Mode selection
    mode = st.radio(
        "Choose Mode:",
        ("🤖 Agent (Real-time API)", "💬 Chatbot (Training Data)")
    )

    # Provider selection
    provider_choice = st.radio(
        "LLM Provider:",
        ("Auto (Gemini → OpenAI)", "Gemini", "OpenAI")
    )
    
    provider_key = "gemini" if provider_choice == "Gemini" else ("openai" if provider_choice == "OpenAI" else "auto")

    if mode == "🤖 Agent (Real-time API)":
        max_steps = st.slider("Max Steps:", 3, 10, 5)
        cache_ttl = st.slider("Cache TTL (seconds):", 0, 3600, 300, 10)
    else:
        max_steps = None
        cache_ttl = None
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.session_state.metrics = []
        st.rerun()


# =========================
# FALLBACK LOGIC
# =========================
def run_with_fallback(prompt, mode, provider_choice, max_steps=None, cache_ttl=None):

    def run_gemini():
        if mode == "🤖 Agent (Real-time API)":
            llm = GeminiProvider()
            agent = ReActAgent(llm=llm, max_steps=max_steps, cache_ttl=cache_ttl)
            return agent.run(prompt)
        else:
            chatbot = GeminiChatbot()
            return chatbot.chat(prompt)

    def run_openai():
        if mode == "🤖 Agent (Real-time API)":
            llm = OpenAIProvider()
            agent = ReActAgent(llm=llm, max_steps=max_steps, cache_ttl=cache_ttl)
            return agent.run(prompt)
        else:
            chatbot = OpenAIChatbot()
            return chatbot.chat(prompt)

    # Manual mode
    if provider_choice == "Gemini":
        return run_gemini(), "Gemini"

    if provider_choice == "OpenAI":
        return run_openai(), "OpenAI"

    # Auto fallback mode
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
# DISPLAY CHAT HISTORY
# =========================
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else ("🤖" if mode == "🤖 Agent (Real-time API)" else "💬")
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])


# =========================
# CHAT INPUT
# =========================
if prompt := st.chat_input("Nhập câu hỏi của bạn..."):
    # Add and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Assistant response
    with st.chat_message("assistant", avatar="🤖" if mode == "🤖 Agent (Real-time API)" else "💬"):
        with st.spinner("Thinking..."):
            try:
                result, provider_used = run_with_fallback(
                    prompt, mode, provider_choice, max_steps, cache_ttl
                )
                
                response = result.get("response", "⚠️ No response returned")
                
                # Show fallback warning
                if "fallback" in provider_used:
                    st.warning(f"⚠️ Fallback activated → {provider_used}")

                # Extract metrics
                latency_ms = result.get("latency_ms", 0)
                tokens = result.get("tokens_used", 0)
                cost = result.get("cost", 0)
                
                # Show cache info
                if result.get("cached"):
                    response += "\n\n> ⚡ *Kết quả được lấy từ cache (0 tokens)*"
                
                st.markdown(response)
                st.caption(f"Provider: {provider_used}")
                
                # Store message and metrics
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.session_state.metrics.append({
                    "latency_ms": latency_ms,
                    "tokens": tokens,
                    "cost": cost
                })

            except Exception as e:
                error_msg = f"❌ System Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})


# =========================
# TELEMETRY & PERFORMANCE DASHBOARD
# =========================
if st.session_state.metrics:
    st.markdown("---")
    st.markdown("### 📊 Performance Dashboard")
    
    latencies = [m["latency_ms"] for m in st.session_state.metrics]
    tokens_list = [m["tokens"] for m in st.session_state.metrics]
    costs = [m["cost"] for m in st.session_state.metrics]
    
    p50_latency = statistics.median(latencies)
    p99_latency = latencies[int(len(latencies) * 0.99)] if len(latencies) > 1 else max(latencies)
    
    avg_latency = statistics.mean(latencies)
    avg_tokens = statistics.mean(tokens_list)
    total_cost = sum(costs)
    total_requests = len(st.session_state.metrics)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Requests", total_requests)
    with col2:
        st.metric("⏱️ Avg Latency", f"{avg_latency:.0f}ms")
    with col3:
        st.metric("📝 Avg Tokens", f"{avg_tokens:.0f}")
    with col4:
        st.metric("💰 Total Cost", f"${total_cost:.6f}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("⚡ P50 Latency", f"{p50_latency:.0f}ms")
    with col2:
        st.metric("🔴 P99 Latency", f"{p99_latency:.0f}ms")
    with col3:
        st.metric("📈 Min Latency", f"{min(latencies):.0f}ms")
    with col4:
        st.metric("📉 Max Latency", f"{max(latencies):.0f}ms")