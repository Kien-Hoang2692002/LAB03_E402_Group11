# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Đỗ Văn Quyết
- **Student ID**: 2A202600042
- **Date**: 2026-04-06

---

## I. Technical Contribution (15 Points)

Trong bài lab này, tôi tập trung vào việc xây dựng và cải tiến chatbot, làm ReAct Agents, giao diện demo.

- **Modules Implementated**: src/tools/shopping_tools.py, streamlit_app.py,chatbot_baseline.py
- **Code Highlights**: 
try:
    result = run_gemini()
    return result, "Gemini"
except Exception as gemini_error:
    logger.log_event("FALLBACK_TRIGGERED", {"provider": "gemini", "error": str(gemini_error)})
    try:
        result = run_openai()
        return result, "OpenAI (fallback)"
    except Exception as openai_error:
        # Xử lý khi cả 2 đều lỗi...
- **Documentation**: Đây là một tính năng rất quan trọng trong môi trường Production. Nếu Gemini gặp lỗi (hết quota, lỗi server), hệ thống sẽ tự động chuyển sang OpenAI để đảm bảo trải nghiệm người dùng không bị gián đoạn.

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: Sửa lỗi hiển thị URL có dấu cách ở Agent
- **Log Source**: https://www.google.com.vn/search?ibp=oshop&q=tai nghe Bluetooth&prds=catalogid:3333131619137253218
- **Diagnosis**: vấn đề nằm ở chỗ dữ liệu trả về từ SerpAPI thường chứa các ký tự đặc biệt hoặc khoảng trắng (đặc biệt là trong tham số q hoặc các redirect link), khiến Markdown hoặc UI của Agent không nhận diện được đó là một đường dẫn hợp lệ.
- **Solution**: Thêm thư viện 
from urllib.parse import urlparse, urlunparse, quote
raw_link = item.get("product_link", "#")
            if raw_link != "#":
                parsed = urlparse(raw_link)
                safe_query = quote(parsed.query, safe='=&?')
                # Ghép URL lại
            else:
                safe_link = "#"
"product_link": safe_link

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: 
Chatbot: Trả lời trực tiếp dựa trên dữ liệu đã học.
ReAct Agent: Dùng Thought để chia nhỏ vấn đề thành các bước logic, giúp kiểm soát quá trình giải quyết nhiệm vụ phức tạp thay vì đoán mò.
2.  **Reliability**: 
Agent tệ hơn Chatbot khi:
Bị kẹt trong vòng lặp vô tận (lặp lại một hành động mà không ra kết quả).
Gặp câu hỏi quá đơn giản (làm phức tạp hóa vấn đề, gây tốn thời gian và chi phí).
Công cụ hỗ trợ (Tools) trả về dữ liệu sai.
3.  **Observation**: 
Là "nguyên liệu" để Agent đánh giá thực tế.
Giúp Agent biết mình đã tìm đủ thông tin chưa hoặc cần phải thay đổi hướng tiếp cận nếu bước trước đó thất bại.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Sử dụng hàng đợi bất đồng bộ (asynchronous queue) để xử lý các lệnh gọi tool song song, giúp agent mở rộng quy mô khi có nhiều yêu cầu hoặc nhiều công cụ.
- **Safety**: Tích hợp một LLM "Supervisor" để kiểm tra, đánh giá và phê duyệt các hành động của agent trước khi thực thi, nhằm giảm thiểu rủi ro về hành vi không mong muốn hoặc lỗi logic.
- **Performance**: Sử dụng Vector Database (VD) để lưu trữ và truy xuất mô tả công cụ, giúp agent lựa chọn công cụ phù hợp nhanh hơn trong hệ thống có nhiều tool, đồng thời tối ưu hóa tốc độ phản hồi

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
