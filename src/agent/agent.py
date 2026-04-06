import os
import re
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
from src.tools.search import search_products
from src.tools.coupon import apply_coupon
from src.tools.rank import select_cheapest
import json
from src.agent.prompts import (
    PARSE_PROMPT,
    PLANNING_PROMPT,
    FINAL_RESPONSE_PROMPT
)

class ReActAgent:
    """
    SKELETON: A ReAct-style Agent that follows the Thought-Action-Observation loop.
    Students should implement the core loop logic and tool execution.
    """
    
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []

    def get_system_prompt(self) -> str:
        """
        TODO: Implement the system prompt that instructs the agent to follow ReAct.
        Should include:
        1.  Available tools and their descriptions.
        2.  Format instructions: Thought, Action, Observation.
        """
        tool_descriptions = "\n".join([f"- {t['name']}: {t['description']}" for t in self.tools])
        return f"""
        You are an intelligent assistant. You have access to the following tools:
        {tool_descriptions}

        Use the following format:
        Thought: your line of reasoning.
        Action: tool_name(arguments)
        Observation: result of the tool call.
        ... (repeat Thought/Action/Observation if needed)
        Final Answer: your final response.
        """

    def run(self, user_input: str) -> str:
        """
        TODO: Implement the ReAct loop logic.
        1. Generate Thought + Action.
        2. Parse Action and execute Tool.
        3. Append Observation to prompt and repeat until Final Answer.
        """
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})
        
        current_prompt = user_input
        steps = 0

        while steps < self.max_steps:
            # TODO: Generate LLM response
            # result = self.llm.generate(current_prompt, system_prompt=self.get_system_prompt())
            
            # TODO: Parse Thought/Action from result
            
            # TODO: If Action found -> Call tool -> Append Observation
            
            # TODO: If Final Answer found -> Break loop
            
            steps += 1
            
        logger.log_event("AGENT_END", {"steps": steps})
        return "Not implemented. Fill in the TODOs!"

    def _execute_tool(self, tool_name: str, args: str) -> str:
        """
        Helper method to execute tools by name.
        """
        for tool in self.tools:
            if tool['name'] == tool_name:
                # TODO: Implement dynamic function calling or simple if/else
                return f"Result of {tool_name}"
        return f"Tool {tool_name} not found."
    

class ShoppingAgent:
    def __init__(self, llm):
        self.llm = llm

    

    def run(self, query):
        # =========================
        # 1. PARSE USER INPUT 🧠
        # =========================
        parse_prompt = PARSE_PROMPT.format(query=query)
        parse_response = self.llm.generate(parse_prompt)

        def clean_json(text):
            if isinstance(text, dict):
                return text

            # xoá markdown
            text = text.replace("```json", "").replace("```", "").strip()

            # lấy phần JSON đầu tiên
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                text = match.group(0)

            return text

        cleaned = clean_json(parse_response)

        if isinstance(parse_response, dict):
            parsed = cleaned
        else:
            # clean text
            parse_response = cleaned.replace("```json", "").replace("```", "").strip()
            
            try:
                parsed = json.loads(cleaned)
            except:
                parsed = {
                    "product": query,
                    "max_price": None,
                    "other_requirements": ""
                }

        product = parsed.get("product")
        max_price = parsed.get("max_price")

        # =========================
        # 2. PLANNING 🧠
        # =========================
        planning_prompt = PLANNING_PROMPT.format(query=query)
        plan_response = self.llm.generate(planning_prompt)

        if isinstance(plan_response, list):
            plan = plan_response
        elif isinstance(plan_response, dict):
            plan = plan_response.get("plan", ["search_products"])
        else:
            plan_response = plan_response.replace("```json", "").replace("```", "").strip()
            try:
                plan = json.loads(plan_response)
            except:
                plan = ["search_products", "select_cheapest"]

        # =========================
        # 3. EXECUTE TOOLS 🛠
        # =========================
        products = None
        best_product = None
        exchange_result = None # Thêm biến lưu kết quả tỉ giá

        for step in plan:
            # Nếu step liên quan đến tìm kiếm sản phẩm
            if step == "search_products":
                products = search_products(product, max_price)

            # MỚI: Nếu step liên quan đến đổi tỉ giá
            elif step == "get_exchange_rate":
                # Giả sử bạn có hàm get_rate(from_currency, to_currency, amount)
                # Bạn cần trích xuất thông tin này từ 'parsed' ở bước 1
                from_cur = parsed.get("from_currency", "USD")
                to_cur = parsed.get("to_currency", "VND")
                amount = parsed.get("amount", 1)
                # exchange_result = get_realtime_exchange_rate(from_cur, to_cur, amount)

            elif step == "apply_coupon" and products:
                products = [apply_coupon(p) for p in products]

            elif step == "select_cheapest" and products:
                best_product = select_cheapest(products)

        # =========================
        # 4. FINAL RESPONSE 🧾
        # =========================
        # Cập nhật context để LLM biết kết quả của CẢ sản phẩm và tỉ giá
        final_prompt = FINAL_RESPONSE_PROMPT.format(
            query=query,
            product_info=best_product,
            exchange_info=exchange_result # Truyền thêm thông tin tỉ giá vào prompt cuối
        )

        final_answer = self.llm.generate(final_prompt)

        return final_answer