# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Hồ Thị Tố Nhi
- **Student ID**: 2A202600369
- **Date**: 2026-04-06

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase (e.g., implemented a specific tool, fixed the parser, etc.).*

- **Modules Implementated**: src/tools/shopping_tool.py
- **Code Highlights**: research and design of the shopping tool without direct code implementation. Defined detailed input/output schemas, and realistic use cases based on user needs (e.g., budget, product specs). These specifications enabled the engineering team to implement a reliable tool that integrates effectively with the ReAct reasoning loop, reducing ambiguity and improving tool-call accuracy.
- **Documentation**: The shopping tool is integrated into the ReAct (Reasoning + Acting) loop to support dynamic product retrieval. The agent first performs reasoning to extract key user requirements such as budget, category, and specifications. Based on this, it decides whether to invoke the shopping tool. During the action step, the agent calls the tool with structured arguments (e.g., price_max, category, specs). The tool returns relevant product results, which are fed back into the observation step. The agent then uses this information to refine its reasoning or generate a final, grounded response. This interaction helps reduce hallucination and ensures responses are based on real data.

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**:  
The agent failed to respond when the Gemini API quota was exceeded, causing the system to crash and return an error to the user.

- **Log Source**:  
[logs/2026-04-06.log]
Error: 429 Quota exceeded  
Agent stopped execution  

- **Diagnosis**:  
The system relied solely on a single LLM provider (Gemini) without any fallback mechanism. When the API limit was reached, the agent could not recover or continue execution.

- **Solution**:  
Implemented a `FallbackProvider` that automatically switches from Gemini to OpenAI when an error occurs. This ensures continuous operation and improves system robustness under API constraints.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: 
        The Thought block enables the agent to break down tasks into structured steps (e.g., extract budget → call tool → apply discount → select cheapest), instead of giving a direct response like a chatbot. This significantly improves performance on multi-step queries and reduces missed requirements.
2.  **Reliability**: 
        The agent may perform worse than the chatbot in certain cases:
                When tools return incorrect data (e.g., price parsing errors)
                When external APIs fail (e.g., invalid API key, timeout)
                When simple queries trigger unnecessary tool usage
                In contrast, chatbots are generally more stable for straightforward knowledge-based questions.
3.  **Observation**: 
        Observations (tool outputs) play a critical role in guiding the next steps. For example, after retrieving products from search_products, the agent uses this data to apply discounts and compare prices. If the observation is inaccurate, it can negatively affect the entire reasoning process.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: 
        Introduce asynchronous processing for tool calls to improve responsiveness
        Deploy the system as microservices (search, pricing, discount) for better scalability
        Add caching for frequent queries (e.g., popular products) to reduce API calls
- **Safety**: 
        Implement a “Supervisor” layer to validate tool calls and prevent invalid or hallucinated actions
        Add stricter input validation and output verification (e.g., price range, discount logic)
        Enforce rules to ensure the agent only uses trusted tools and predefined discount codes
- **Performance**: 
        Optimize tool usage by reducing unnecessary calls (e.g., skip tools for simple queries)
        Use a vector database to retrieve relevant tools or past queries in more complex systems
        Improve prompt efficiency to reduce token usage and latency

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
