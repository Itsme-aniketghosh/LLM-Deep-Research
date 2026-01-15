"""
Planner - Dynamic search count (3-7)
"""

import json
import random
from dataclasses import dataclass
from typing import List
from llm_client import get_llm
import logger


@dataclass
class WebSearchItem:
    query: str
    reason: str


@dataclass 
class WebSearchPlan:
    searches: List[WebSearchItem]


async def plan_searches(query: str) -> WebSearchPlan:
    # Random 3-7 searches
    count = random.randint(3, 7)
    
    llm = get_llm()
    logger.step("Plan", f"{count} searches")
    
    prompt = f"""Create exactly {count} search queries for: {query}

Output JSON: {{"searches": [{{"query": "term", "reason": "why"}}]}}

Make them specific and diverse. JSON only:"""
    
    response = await llm.generate(prompt, json_mode=True)
    
    try:
        data = llm.parse_json_response(response)
        searches = [
            WebSearchItem(query=s["query"], reason=s.get("reason", ""))
            for s in data.get("searches", [])[:count]
        ]
        if len(searches) >= 2:
            logger.success("Plan", f"{len(searches)} queries ready")
            return WebSearchPlan(searches=searches)
    except:
        pass
    
    # Fallback
    pool = [
        f"{query} statistics 2024",
        f"{query} benefits advantages",
        f"{query} problems issues",
        f"{query} examples",
        f"{query} expert analysis",
        f"{query} latest developments",
        f"{query} comparison",
    ]
    picks = random.sample(pool, min(count, len(pool)))
    return WebSearchPlan(searches=[WebSearchItem(q, "") for q in picks])
