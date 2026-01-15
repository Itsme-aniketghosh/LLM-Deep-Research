"""
LLM Client - Llama 3.2
"""

import os
import json
import re
import asyncio
from huggingface_hub import InferenceClient
import logger


class HuggingFaceLLM:
    def __init__(self):
        self.token = os.environ.get("HF_TOKEN")
        self.model = os.environ.get("HF_MODEL", "meta-llama/Llama-3.2-3B-Instruct")
        self.client = InferenceClient(token=self.token)
        logger.info("LLM", self.model.split("/")[-1])
    
    def _call(self, prompt: str, system: str = "", json_mode: bool = False) -> str:
        msgs = []
        if system:
            msgs.append({"role": "system", "content": system})
        
        content = prompt
        if json_mode:
            content += "\n\nOutput JSON only, nothing else."
        
        msgs.append({"role": "user", "content": content})
        
        resp = self.client.chat_completion(
            model=self.model,
            messages=msgs,
            max_tokens=1200,
            temperature=0.7,
            top_p=0.85,
        )
        return resp.choices[0].message.content
    
    async def generate(self, prompt: str, system_prompt: str = "", json_mode: bool = False) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self._call(prompt, system_prompt, json_mode))
    
    def parse_json_response(self, text: str) -> dict:
        text = re.sub(r'```json?\s*', '', text)
        text = re.sub(r'```', '', text)
        match = re.search(r'\{[\s\S]*\}', text)
        return json.loads(match.group() if match else text)


_llm = None

def get_llm():
    global _llm
    if not _llm:
        _llm = HuggingFaceLLM()
    return _llm
