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
- Find products based on user requirements (e.g., type, features, performance)  
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
  - Agent: lọc theo budget + chọn cấu hình tốt nhất  



## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation
*Diagram or description of the Thought-Action-Observation loop.*
Diagram: https://drive.google.com/file/d/1cAhsjtbK4ac7IR4flMvDOMj5joKIudEo/view?usp=sharing


### 2.2 Tool Definitions (Inventory)
| Tool Name | Input Format | Use Case |
| :--- | :--- | :--- |
| `calc_tax` | `json` | Calculate VAT based on country code. |
| `search_api` | `string` | Retrieve real-time information from Google Search. |


### 2.3 LLM Providers Used
- **Primary**: Gemini 2.5 Flash
- **Secondary (Backup)**: 

---

## 3. Telemetry & Performance Dashboard

*Analyze the industry metrics collected during the final test run.*

- **Average Latency (P50)**: [e.g., 1200ms]
- **Max Latency (P99)**: [e.g., 4500ms]
- **Average Tokens per Task**: [e.g., 350 tokens]
- **Total Cost of Test Suite**: [e.g., $0.05]

---

## 4. Root Cause Analysis (RCA) - Failure Traces

*Deep dive into why the agent failed.*

### Case Study: [e.g., Hallucinated Argument]
- **Input**: "How much is the tax for 500 in Vietnam?"
- **Observation**: Agent called `calc_tax(amount=500, region="Asia")` while the tool only accepts 2-letter country codes.
- **Root Cause**: The system prompt lacked enough `Few-Shot` examples for the tool's strict argument format.

---

## 5. Ablation Studies & Experiments

### Experiment 1: Prompt v1 vs Prompt v2
- **Diff**: [e.g., Adding "Always double check the tool arguments before calling".]
- **Result**: Reduced invalid tool call errors by [e.g., 30%].

### Experiment 2 (Bonus): Chatbot vs Agent
| Case | Chatbot Result | Agent Result | Winner |
| :--- | :--- | :--- | :--- |
| Simple Q | Correct | Correct | Draw |
| Multi-step | Hallucinated | Correct | **Agent** |

---

## 6. Production Readiness Review

*Considerations for taking this system to a real-world environment.*

- **Security**: [e.g., Input sanitization for tool arguments.]
- **Guardrails**: [e.g., Max 5 loops to prevent infinite billing cost.]
- **Scaling**: [e.g., Transition to LangGraph for more complex branching.]

---

> [!NOTE]
> Submit this report by renaming it to `GROUP_REPORT_[TEAM_NAME].md` and placing it in this folder.
