"""
Search Agent - Summaries optimized for report writing
"""

from typing import Tuple, List, Dict
from llm_client import get_llm
from web_search import web_search
import logger


# Optimized for the writer's needs: hook, meat, punch
SYSTEM_PROMPT = """You are a research assistant preparing material for a journalist.

From these search results, extract:

1. **HOOK MATERIAL** - One surprising statistic or bold claim that would grab attention
2. **KEY FACTS** - 2-3 specific facts with numbers, names, or concrete details  
3. **INSIGHT** - One interesting implication or "what this means"

Format your response exactly like this:
HOOK: [the surprising stat or claim]
FACTS: [bullet the key facts]
INSIGHT: [the deeper meaning]

Be specific. Use actual numbers and names from the results."""


async def search_and_summarize_with_raw(query: str, reason: str, num: int = 0) -> Tuple[List[Dict], str]:
    tag = f"S{num}" if num else "Search"
    
    results = await web_search(query, max_results=5, search_num=num)
    
    if not results:
        return [], ""
    
    # Format for LLM
    context = ""
    for r in results[:4]:
        context += f"\n• {r['title']}\n  {r['snippet']}\n"
    
    llm = get_llm()
    
    try:
        prompt = f"Search: '{query}'\n\nResults:{context}\n\nExtract the best material for a report:"
        
        summary = await llm.generate(prompt, system_prompt=SYSTEM_PROMPT)
        
        # Clean up any preamble
        summary = summary.strip()
        for skip in ["Here", "Based on", "I found", "The search"]:
            if summary.startswith(skip):
                lines = summary.split('\n', 1)
                summary = lines[1].strip() if len(lines) > 1 else summary
        
        logger.success(tag, f"{len(results)} sources → {len(summary)} chars")
        return results, summary
        
    except Exception as e:
        logger.error(tag, str(e))
        # Fallback: return raw snippet
        return results, f"FACTS: {results[0]['snippet'][:200]}" if results else ""
