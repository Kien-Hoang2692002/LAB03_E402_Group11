from agent.agent import ShoppingAgent
from core.gemini_provider import GeminiProvider

def main():
    llm = GeminiProvider()
    agent = ShoppingAgent(llm)

    query = "tìm tai nghe dưới 1 triệu"
    result = agent.run(query)

    print("Kết quả:", result)

if __name__ == "__main__":
    main()