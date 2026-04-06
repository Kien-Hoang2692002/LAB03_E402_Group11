import os
import time
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from src.core.gemini_provider import GeminiProvider
from src.core.openai_provider import OpenAIProvider
from src.telemetry.logger import logger

load_dotenv()


class BaseChatbot:
    """
    Baseline Chatbot - Multi-provider support (Gemini or OpenAI).
    Uses only 1 LLM call per query.
    """
    
    def __init__(self, provider: str = "gemini"):
        """
        Args:
            provider: "gemini" or "openai"
        """
        self.provider_name = provider
        self.conversation_history = []
        
        if provider == "gemini":
            self.llm = GeminiProvider()
        elif provider == "openai":
            self.llm = OpenAIProvider(model_name="gpt-4o")
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        print(f"✅ Chatbot initialized with {provider.upper()}")
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate API cost based on provider."""
        if self.provider_name == "gemini":
            # Gemini 2.0 Flash pricing
            input_cost = (input_tokens / 1_000_000) * 0.075
            output_cost = (output_tokens / 1_000_000) * 0.3
            return input_cost + output_cost
        
        elif self.provider_name == "openai":
            # GPT-4o pricing (as of 2024)
            input_cost = (input_tokens / 1_000_000) * 5.0  # $5 per 1M input tokens
            output_cost = (output_tokens / 1_000_000) * 15.0  # $15 per 1M output tokens
            return input_cost + output_cost
    
    def get_system_prompt(self) -> str:
        """Shopping assistant prompt - NO TOOLS."""
        return """Bạn là một trợ lý mua sắm thông minh.

HƯỚNG DẪN:
1. Lắng nghe yêu cầu của khách hàng (budget, loại sản phẩm, đặc điểm mong muốn)
2. Dựa trên KIẾN THỨC HUẤN LUYỆN, gợi ý sản phẩm phù hợp
3. Ước lượng giá dựa trên kinh nghiệm (KHÔNG TÌM KIẾM THỰC TẾ)
4. Đề xuất mã giảm giá phổ biến (nếu có)
5. Ước tính giá cuối cùng
6. Trả lời ngắn gọn, rõ ràng

⚠️ HẠNCHẾ: 
- Không có truy cập vào dữ liệu sản phẩm thực tế
- Không biết giá cả thực tế hiện tại
- Không thể áp dụng mã giảm giá chính xác
- Chỉ dựa vào suy đoán và kiến thức cũ"""
    
    def chat(self, user_input: str) -> Dict[str, Any]:
        """Single LLM call - ONE STEP ONLY."""
        logger.log_event("CHATBOT_START", {
            "input": user_input,
            "provider": self.provider_name
        })
        
        start_time = time.time()
        
        try:
            result = self.llm.generate(
                prompt=user_input,
                system_prompt=self.get_system_prompt()
            )
            
            response_text = result["content"]
            latency_ms = result.get("latency_ms", int((time.time() - start_time) * 1000))
            tokens_used = result.get("usage", {}).get("total_tokens", 0)
            
            # Calculate cost
            cost = self._calculate_cost(
                input_tokens=result.get("usage", {}).get("prompt_tokens", 0),
                output_tokens=result.get("usage", {}).get("completion_tokens", 0)
            )
            
            # Store in history
            self.conversation_history.append({
                "user": user_input,
                "bot": response_text,
                "latency_ms": latency_ms,
                "tokens": tokens_used,
                "cost": cost
            })
            
            logger.log_event("CHATBOT_RESPONSE", {
                "latency_ms": latency_ms,
                "tokens": tokens_used,
                "cost": cost,
                "provider": self.provider_name
            })
            
            return {
                "response": response_text,
                "latency_ms": latency_ms,
                "tokens_used": tokens_used,
                "cost": cost,
                "step_count": 1
            }
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            logger.log_event("CHATBOT_ERROR", {
                "error": str(e),
                "provider": self.provider_name
            })
            return {
                "response": error_msg,
                "latency_ms": int((time.time() - start_time) * 1000),
                "tokens_used": 0,
                "cost": 0,
                "step_count": 0
            }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get cumulative metrics."""
        if not self.conversation_history:
            return {"message": "No conversation history"}
        
        total_latency = sum(h["latency_ms"] for h in self.conversation_history)
        total_tokens = sum(h["tokens"] for h in self.conversation_history)
        total_cost = sum(h["cost"] for h in self.conversation_history)
        
        return {
            "provider": self.provider_name,
            "total_queries": len(self.conversation_history),
            "total_latency_ms": total_latency,
            "avg_latency_ms": total_latency / len(self.conversation_history),
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 6)
        }