"""
Web Search - DuckDuckGo
"""

from ddgs import DDGS
from typing import List, Dict
import asyncio
import logger


async def web_search(query: str, max_results: int = 10, search_num: int = 0) -> List[Dict[str, str]]:
    tag = f"S{search_num}" if search_num else "DDG"
    
    def _search():
        try:
            results = list(DDGS().text(query, max_results=max_results))
            logger.success(tag, f"{len(results)} hits")
            return results
        except Exception as e:
            logger.error(tag, str(e))
            return []
    
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(None, _search)
    
    return [{
        "title": r.get("title", ""),
        "url": r.get("href", ""),
        "snippet": r.get("body", "")
    } for r in results]
