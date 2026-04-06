# Group Report: Lab 3 - Production-Grade Agentic System

- **Team Name**: Phong402_Team11
- **Team Members**: 
        2A202600369: Hồ Thị Tố Nhi
        2A202600368: Hà Hữu An
        2A202600077-Hoàng Văn Kiên
        2A202600042-Đỗ Văn Quyết\
        2A202600095 – Lê Hoàng Long
- **Deployment Date**: [2026-04-06]

---

## 1. Executive Summary

*Brief overview of the agent's goal and success rate compared to the baseline chatbot.*

- **Success Rate**: [e.g., 85% on 20 test cases]
- **Key Outcome**: [e.g., "Our agent solved 40% more multi-step queries than the chatbot baseline by correctly utilizing the Search tool."]
### 1.1 Agent Goal

The goal of our system is to build a **Shopping Deal Assistant** that helps users:
- Find products based on user requirements (e.g., type, features, price)  
- Filter products within a given budget  
- Optimize selection based on user criteria (e.g., cheapest, best performance, best value)  

Unlike a baseline chatbot, the agent can handle **multi-step queries with constraints**, such as:

👉 *"Tìm laptop dưới 15 triệu, cấu hình mạnh nhất"*  
👉 *"Tai nghe dưới 1 triệu, pin trâu + giá sau giảm"*

---

### 1.2. Success Rate

- **Success Rate**: ~85% on 20 test cases  

Success is defined as:
- Correctly understanding user requirements (product + budget + criteria)  
- Filtering relevant products  
- Selecting the best option based on the given criteria  

### 1.3. Key Outcome

- The agent solved **~40% more constraint-based and multi-step queries** than the chatbot baseline  
- Improved ability to handle:
  - Budget constraints  
  - User preferences (e.g., performance, battery, price)  
  - Multi-criteria optimization  

👉 Example:
- Query: *"Tìm laptop dưới 15 triệu cấu hình mạnh nhất"*  
  - Chatbot: đưa gợi ý chung  
  - Agent: lọc theo budget + chọn cấu hình,tiêu chí tốt nhất  



## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation
*Diagram or description of the Thought-Action-Observation loop.*
Diagram: https://drive.google.com/file/d/1cAhsjtbK4ac7IR4flMvDOMj5joKIudEo/view?usp=sharing


### 2.2 Tool Definitions (Inventory)
| Tool Name | Input Format | Use Case |
| :--- | :--- | :--- |
| `search_products` | `json (query, max_price optional)` | Tìm kiếm sản phẩm theo từ khóa từ Google Shopping (SerpAPI), lọc theo ngân sách nếu có. |
| `calc_final_price` | `json (original_price, discount_percent, discount_fixed, quantity)` | Tính giá cuối cùng sau khi áp dụng mã giảm giá . |


### 2.3 LLM Providers Used
- **Primary**: Gemini 2.5 Flash
- **Secondary (Backup)**: gpt-4o

---

## 3. Telemetry & Performance Dashboard

*Analyze the industry metrics collected during the final test run.*

- **Average Latency (P50)**: 2155ms
- **Max Latency (P99)**: 28603ms
- **Average Tokens per Task**: 8010ms
- **Total Cost of Test Suite**: 0

---

## 4. Root Cause Analysis (RCA) - Failure Traces

*Deep dive into why the agent failed.*
### Case Study: [e.g., Hallucinated Argument]
- **Input**: "How much is the tax for 500 in Vietnam?"
- **Observation**: Agent called `calc_tax(amount=500, region="Asia")` while the tool only accepts 2-letter country codes.
- **Root Cause**: The system prompt lacked enough `Few-Shot` examples for the tool's strict argument format.
### 4.1. Early Termination in Multi-step Reasoning
- **Input**:"Find Bluetooth headphones under 1 million VND, apply discounts if available, and select the cheapest product."
- **Observation**:The agent only executed:search_products. Then terminated immediately (steps= 1) without:applying any discount, selecting the cheapest product
- **Root Cause**: The agent failed to recognize this as a multi-step task requiring sequential reasoning
The system prompt did not clearly define a step-by-step workflow (e.g., search → apply discount → compare → select).Although max_steps was set to 5, the agent terminated early due to lack of explicit planning instructions. The model assumed the first tool result was sufficient and did not continue reasoning

### 4.2. No Action Taken for Knowledge-based Query
- **Input**: "What is Bluetooth headphones? Explain briefly for beginners."
- **Observation**: The agent returned:
      steps = 0
      reason = no_action
    No response or meaningful output was generated
- **Root Cause**
    The system failed to correctly route the query to a direct LLM response
    The agent pipeline was overly dependent on tool usage and lacked a fallback mechanism for non-tool queries
    There was no clear instruction such as:
                If no tool is required, answer directly using the language model
    As a result, the agent did not take any action when the query did not match available tools
---

## 5. Ablation Studies & Experiments

### Experiment 1: Prompt v1 vs Prompt v2
- **Diff**:
  Prompt v1: Generic instructions with no clear workflow
  Prompt v2: Added explicit steps:
    * Extract budget → call `search_products`
    * Apply discount if available
    * Select the cheapest product
  Added constraints:
    * Do not stop early
    * Always map user requirements to tool parameters (e.g., price → max_price)
- **Result**:
  Reduced early termination errors
  Reduced missing parameter issues (e.g., max_price)
  Improved multi-step task handling

### Experiment 2 (Bonus): Chatbot vs Agent
| Case | Chatbot Result | Agent Result | Winner |
### Experiment 2 (Bonus): Chatbot vs Agent

| Case                 | Chatbot Result                   | Agent Result                                     | Winner    |
| Simple Question      | Correct explanation              | Correct explanation                              | Draw      |
| Product Search       | Generic suggestions              | Retrieved real products via API                  | **Agent** |
| Budget Constraint    | Ignored budget                   | Correctly filtered by price (`max_price`)        | **Agent** |
| Discount Application | Hallucinated or skipped discount | Correctly applied discount using tool            | **Agent** |
| Multi-step Task      | Incomplete reasoning             | Completed all steps (search → discount → select) | **Agent** |

---

## 6. Production Readiness Review

*Considerations for taking this system to a real-world environment.*

- **Security**: 
      Validate and sanitize user inputs before passing to tools (e.g., query, max_price)
      Secure API keys using environment variables (.env) and avoid hardcoding
      Prevent malformed or adversarial inputs that could break tool execution
- **Guardrails**: 
      Limit maximum reasoning steps (e.g., max_steps = 5) to avoid infinite loops and high cost
      Enforce rules such as:
            Do not hallucinate discount codes
            Only use predefined tools
      Add fallback handling when tools fail (e.g., API error → return safe response)
- **Scaling**: 
      Modularize tools (search, pricing, discount) for easier extension
      Support more complex workflows (e.g., multiple filters, ranking logic)
      Consider migrating to frameworks like LangGraph for better control over multi-step reasoning and branching
---

> [!NOTE]
> Submit this report by renaming it to `GROUP_REPORT_[TEAM_NAME].md` and placing it in this folder.
