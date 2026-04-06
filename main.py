from src.agent.agent import ReActAgent
from src.core.gemini_provider import GeminiProvider
from chatbot_baseline import GeminiChatbot
import json


def test_conversation():
    """Test multiple queries comparing Chatbot vs Agent."""
    
    test_queries = [
        "Tìm tai nghe Bluetooth dưới 2 triệu",
        "Tìm tai nghe dưới 2 triệu + áp mã FIRST20",
        "Tìm loa Bluetooth rẻ nhất",
    ]
    
    results = {
        "chatbot": [],
        "agent": [],
        "queries": test_queries
    }
    
    for i, query in enumerate(test_queries, 1):
        print("\n" + "="*80)
        print(f"📝 QUERY {i}: {query}")
        print("="*80)
        
        # Test CHATBOT
        print("\n📱 CHATBOT BASELINE (1 bước)\n" + "-"*80)
        try:
            chatbot = GeminiChatbot()
            chatbot_result = chatbot.chat(query)
            print(f"Response: {chatbot_result['response'][:200]}...")
            print(f"Metrics: {chatbot_result['tokens_used']} tokens | "
                  f"${chatbot_result['cost']:.6f} | {chatbot_result['latency_ms']}ms")
            results["chatbot"].append({
                "query": query,
                "response": chatbot_result['response'],
                "tokens": chatbot_result['tokens_used'],
                "cost": chatbot_result['cost'],
                "latency_ms": chatbot_result['latency_ms'],
                "steps": 1
            })
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test AGENT
        print("\n\n🤖 REACT AGENT (multi-step)\n" + "-"*80)
        try:
            llm = GeminiProvider()
            agent = ReActAgent(llm=llm, max_steps=5)
            agent_result = agent.run(query)
            print(f"Final Answer: {agent_result['response'][:200]}...")
            print(f"Metrics: Step {agent_result['steps']} | "
                  f"{agent_result['tokens_used']} tokens | {agent_result['latency_ms']}ms")
            results["agent"].append({
                "query": query,
                "response": agent_result['response'],
                "tokens": agent_result['tokens_used'],
                "latency_ms": agent_result['latency_ms'],
                "steps": agent_result['steps'],
                "success": agent_result['success']
            })
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # 4. Summary
    print("\n\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    
    total_chatbot_tokens = sum(r["tokens"] for r in results["chatbot"])
    total_agent_tokens = sum(r["tokens"] for r in results["agent"])
    avg_chatbot_latency = sum(r["latency_ms"] for r in results["chatbot"]) / len(results["chatbot"])
    avg_agent_latency = sum(r["latency_ms"] for r in results["agent"]) / len(results["agent"])
    
    print(f"\n{'Metric':<30} {'Chatbot':<25} {'Agent':<25}")
    print("-"*80)
    print(f"{'Total Tokens':<30} {total_chatbot_tokens:<25} {total_agent_tokens:<25}")
    print(f"{'Avg Latency (ms)':<30} {avg_chatbot_latency:<25.0f} {avg_agent_latency:<25.0f}")
    print(f"{'Steps per Query':<30} {1:<25} {'Multi (varies)':<25}")
    print(f"{'Data Source':<30} {'Training data':<25} {'Real APIs':<25}")
    
    # Export results
    with open("comparison_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Results exported to comparison_results.json")


if __name__ == "__main__":
    test_conversation()