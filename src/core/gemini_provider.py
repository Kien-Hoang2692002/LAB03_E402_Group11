import os
import time
import google.generativeai as genai
from typing import Dict, Any, Optional, Generator
from src.core.llm_provider import LLMProvider
from dotenv import load_dotenv

load_dotenv()

class GeminiProvider(LLMProvider):
    def __init__(self, model_name: str = "gemini-2.5-flash", api_key: Optional[str] = None):
        if api_key is None:
            api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY not found. Please set it in .env file")

        super().__init__(model_name, api_key)

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        start_time = time.time()

        full_prompt = prompt
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"

        import re
        max_retries = 5
        response = None
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(full_prompt)
                break
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "Quota exceeded" in error_msg:
                    if attempt < max_retries - 1:
                        # Extract exact wait time from API error if possible
                        wait_match = re.search(r"retry in (\d+(?:\.\d+)?)s", error_msg)
                        if wait_match:
                            retry_delay = float(wait_match.group(1)) + 2.0 # Wait exactly what it needs + 2s buffer
                        else:
                            retry_delay = 15.0 * (2 ** attempt) # Fallback exponential: 15s, 30s, 60s
                        
                        print(f"⚠️ API Rate Limit. Chờ {retry_delay:.1f}s trước khi thử lại... (Lần {attempt+1}/{max_retries})")
                        time.sleep(retry_delay)
                    else:
                        raise e
                else:
                    raise e
                    
        if not response:
            raise RuntimeError("Failed to generate content after retries.")

        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        content = response.text if response.text else ""

        usage = {}
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            usage = {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "completion_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count
            }

        return {
            "content": content,
            "usage": usage,
            "latency_ms": latency_ms,
            "provider": "google"
        }

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"

        response = self.model.generate_content(full_prompt, stream=True)

        for chunk in response:
            if chunk.text:
                yield chunk.text
