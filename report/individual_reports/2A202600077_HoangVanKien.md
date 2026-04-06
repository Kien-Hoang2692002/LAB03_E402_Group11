# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Hoàng Văn Kiên
- **Student ID**: 2A202600077
- **Date**: 2026-04-06

## I. Technical Contribution (15 Points)

Trong bài lab này, tôi tập trung vào việc xây dựng và cải tiến **ReAct Agent** cho bài toán shopping chatbot.

**Modules Implemented:**
- `src/agent/react_agent.py`
- `src/tools/shopping_tools.py`

**Các tính năng chính đã tích hợp:**
- Tích hợp `LLMProvider` và hệ thống logging
- Xây dựng đầy đủ ReAct Loop
- Tool Execution Engine hỗ trợ gọi dynamic các tool
- Caching mechanism để tối ưu hiệu suất
- Flexible Action Parsing hỗ trợ nhiều format output của LLM

**Code Highlights:**

```python
# ReAct Loop Implementation
while steps < self.max_steps:
    response = self.llm.generate(
        prompt=current_prompt,
        system_prompt=self.get_system_prompt()
    )
    # Thought → Action → Observation → Final Answer
Luồng hoạt động của agent: Nhận input từ user Gửi vào LLM với REACT_SYSTEM_PROMPT LLM sinh ra: Thought Action Agent parse Action → gọi tool Nhận Observation → append vào prompt Lặp lại cho đến khi có Final Answer
```

## II. Debugging Case Study (10 Points)

**Problem Description:**  
Agent không parse được action khi LLM trả về format khác dự kiến (ví dụ: dùng `Action Input` thay vì `Action: tool(...)`).

**Log Source:**  
`AGENT_END: reason=no_action`

**Diagnosis:**  
Nguyên nhân: Regex ban đầu chỉ hỗ trợ format `Action: tool(arg1, arg2)`.  
Tuy nhiên, LLM đôi khi trả về theo format khác:
→ Dẫn đến agent không nhận diện được action và kết thúc sớm.

**Solution:**  
Thêm fallback parsing để tăng tính robust:

```python
action_name_match = re.search(r"Action:\s*(\w+)", content)
action_input_match = re.search(r"Action Input:\s*(\{.*?\})", content, re.DOTALL)
```
## III. Personal Insights: Chatbot vs ReAct (10 Points)

### 1. Reasoning
ReAct Agent tốt hơn chatbot ở:
- Có bước **Thought** → suy nghĩ trước khi hành động
- Không trả lời “đoán mò” dựa trên kiến thức cũ

**Ví dụ:**
- Chatbot: trả lời giá iPhone theo kiến thức cũ
- ReAct Agent: gọi `search_products` → lấy dữ liệu real-time

### 2. Reliability
Agent đôi khi kém hơn chatbot khi:
- LLM sinh sai format → parse fail
- Tool trả lỗi → agent không recover tốt
- Vòng lặp vượt `max_steps`

→ Trong những trường hợp này, chatbot đơn giản lại ổn định và đáng tin cậy hơn.

### 3. Observation
Observation đóng vai trò rất quan trọng:
- Là feedback thực tế từ môi trường (tool output)
- Giúp agent cập nhật context và điều chỉnh hành vi ở các bước tiếp theo

**Ví dụ:**  
Observation trả về danh sách sản phẩm → Agent dùng thông tin đó để chọn sản phẩm phù hợp và tính giá tiếp theo.

---

## IV. Future Improvements (5 Points)

- **Scalability**: 
  - Sử dụng async queue (Celery / Kafka) cho tool calls
  - Tách agent thành microservices

- **Safety**: 
  - Thêm Supervisor LLM kiểm tra action
  - Validate input trước khi gọi tool

- **Performance**: 
  - Dùng Vector DB để chọn tool phù hợp khi có nhiều tool
  - Improve cache (sử dụng Redis thay vì file JSON)
  - Giảm token usage bằng prompt optimization

