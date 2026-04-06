import os
import re
import json
import time
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
from src.agent.prompts import REACT_SYSTEM_PROMPT
from src.tools.shopping_tools import search_products, get_discount, calc_final_price

load_dotenv()


class ReActAgent:
    """ReAct Agent with Thought-Action-Observation loop."""
    
    def __init__(self, llm: LLMProvider, max_steps: int = 5):
        self.llm = llm
        self.max_steps = max_steps

    def get_system_prompt(self) -> str:
        return REACT_SYSTEM_PROMPT

    def run(self, user_input: str) -> Dict[str, Any]:
        """ReAct loop với better error handling."""
        
        logger.log_event("AGENT_START", {
            "input": user_input,
            "model": self.llm.model_name
        })
        
        start_time = time.time()
        current_prompt = user_input
        steps = 0
        total_tokens = 0
        
        while steps < self.max_steps:
            response = self.llm.generate(
                prompt=current_prompt,
                system_prompt=self.get_system_prompt()
            )
            
            content = response["content"]
            total_tokens += response.get("usage", {}).get("total_tokens", 0)
            
            print(f"\n[Step {steps}] LLM:\n{content}\n")
            
            # Check Final Answer FIRST
            if "Final Answer:" in content:
                final_answer = content.split("Final Answer:")[-1].strip()
                latency_ms = int((time.time() - start_time) * 1000)
                
                logger.log_event("AGENT_END", {
                    "steps": steps,
                    "reason": "final_answer",
                    "latency_ms": latency_ms
                })
                
                return {
                    "response": final_answer,
                    "steps": steps,
                    "tokens_used": total_tokens,
                    "latency_ms": latency_ms,
                    "success": True
                }
            
            # Parse Action - IMPROVED REGEX
            action_match = re.search(
                r"Action:\s*(\w+)\s*\(\s*(.*?)\s*\)",
                content,
                re.DOTALL | re.IGNORECASE  # ← Case insensitive + multiline
            )
            
            if not action_match:
                print(f"⚠️ Không tìm action. Content:\n{content}")
                
                # Try to extract keyword và suggest
                if "search" in content.lower():
                    observation = "Gợi ý: Hãy gọi search_products(query, max_price)"
                elif "discount" in content.lower():
                    observation = "Gợi ý: Hãy gọi get_discount(code)"
                elif "final" in content.lower() or "answer" in content.lower():
                    observation = "Bạn có đủ thông tin rồi, hãy trả lời Final Answer"
                else:
                    observation = f"Lỗi parse. Hãy viết chính xác: Action: tool_name(args)"
                
                current_prompt += f"\n{content}\nObservation: {observation}\n\nHãy thử lại."
                steps += 1
                continue
            
            # Execute tool
            tool_name = action_match.group(1).strip()
            args_str = action_match.group(2).strip()
            
            observation = self._execute_tool(tool_name, args_str)
            
            print(f"[Tool] {tool_name}({args_str})\n[Observation] {observation}\n")
            
            logger.log_event("TOOL_EXECUTED", {
                "step": steps,
                "tool": tool_name,
                "observation": observation
            })
            
            current_prompt += f"\n{content}\nObservation: {observation}"
            steps += 1
        
        latency_ms = int((time.time() - start_time) * 1000)
        logger.log_event("AGENT_END", {
            "steps": steps,
            "reason": "max_steps_exceeded"
        })
        
        return {
            "response": "❌ Vượt quá số bước tối đa",
            "steps": steps,
            "tokens_used": total_tokens,
            "latency_ms": latency_ms,
            "success": False
        }

    def _execute_tool(self, tool_name: str, args_str: str) -> str:
        """Execute tool dynamically."""
        try:
            args = [arg.strip().strip("'\"") for arg in args_str.split(",")]
            
            if tool_name == "search_products":
                query = args[0] if len(args) > 0 else ""
                max_price = int(args[1]) if len(args) > 1 and args[1] else None
                result = search_products(query, max_price)
                
            elif tool_name == "get_discount":
                code = args[0] if len(args) > 0 else ""
                result = get_discount(code)
                
            elif tool_name == "calc_final_price":
                price = float(args[0]) if len(args) > 0 else 0
                discount_percent = float(args[1]) if len(args) > 1 and args[1] else 0
                discount_fixed = float(args[2]) if len(args) > 2 and args[2] else 0
                quantity = int(args[3]) if len(args) > 3 and args[3] else 1
                result = calc_final_price(price, discount_percent, discount_fixed, quantity)
                
            else:
                return json.dumps({"error": f"Tool không biết: {tool_name}"}, ensure_ascii=False)
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.log_event("TOOL_ERROR", {"tool": tool_name, "error": str(e)})
            return json.dumps({"error": str(e)}, ensure_ascii=False)