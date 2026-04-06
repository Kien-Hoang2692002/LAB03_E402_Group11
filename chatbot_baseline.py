import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

# load env
load_dotenv()

class GeminiChatbot:
    def __init__(self, model_name="gemini-1.5-flash"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ Missing GEMINI_API_KEY in .env")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def chat(self, user_input: str, system_prompt: str = None) -> str:
        start_time = time.time()

        # simple prompt format
        if system_prompt:
            prompt = f"System: {system_prompt}\n\nUser: {user_input}"
        else:
            prompt = user_input

        response = self.model.generate_content(prompt)

        latency = int((time.time() - start_time) * 1000)

        text = response.text if response.text else ""

        print(f"\n⏱ Latency: {latency} ms")
        return text


def main():
    bot = GeminiChatbot()

    system_prompt = """
    Bạn là một trợ lý mua sắm.
    Nhiệm vụ:
    - Tư vấn sản phẩm theo yêu cầu người dùng
    - Ưu tiên sản phẩm giá rẻ
    - Trả lời ngắn gọn, dễ hiểu
    """

    print("🤖 Chatbot (baseline - no agent). Gõ 'exit' để thoát.\n")

    while True:
        user_input = input("👤 Bạn: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        response = bot.chat(user_input, system_prompt)

        print("🤖 Bot:", response)
        print("-" * 50)


if __name__ == "__main__":
    main()