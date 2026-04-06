# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Lê Hoàng Long
- **Student ID**: 2A202600095
- **Date**: 6-4-2026

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase (e.g., implemented a specific tool, fixed the parser, etc.).*

- **Modules Implementated**: streamlit_app.py
- **Code Highlights**:  llm = LocalProvider(model_path=model_path)
- **Documentation**: Allow the app to use local LLM 

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: None
- **Log Source**: None
- **Diagnosis**:None
- **Solution**: None

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: How did the `Thought` block help the agent compared to a direct Chatbot answer?
    It works better, the information is more reliable 
2.  **Reliability**: There isn't such cases 
3.  **Observation**: It depends much on the context of the  query

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: apply multiple threads strategy
- **Safety**: Set up a limit on the operating right of the agent 
- **Performance**: Replace Phi with Qwen

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
