"""
Research Manager - Detailed live tracking
"""

import asyncio
from typing import AsyncGenerator
from planner_agent import plan_searches
from search_agent import search_and_summarize_with_raw
from writer_agent import write_report
import logger


class ResearchManager:
    
    async def run(self, query: str) -> AsyncGenerator[str, None]:
        logger.info("Research", f"Topic: {query}")
        
        # ===== PLANNING =====
        yield self._status("🧠 PLANNING", "Analyzing your topic...", [
            f"📌 Topic: **{query}**",
            "🔄 Generating search strategy..."
        ])
        
        try:
            plan = await plan_searches(query)
            num = len(plan.searches)
            queries = [item.query for item in plan.searches]
        except Exception as e:
            yield self._status("❌ ERROR", str(e), [])
            return
        
        yield self._status("✅ STRATEGY READY", f"{num} searches planned", [
            f"**{i}.** {q}" for i, q in enumerate(queries, 1)
        ])
        await asyncio.sleep(0.8)
        
        # ===== PARALLEL SEARCH =====
        completed = 0
        succeeded = 0
        results = {}
        current_queries = {i: "⏳ Waiting..." for i in range(1, num + 1)}
        
        async def do_search(idx: int, item):
            nonlocal completed, succeeded
            current_queries[idx] = "🔍 Searching..."
            try:
                raw, summary = await search_and_summarize_with_raw(item.query, item.reason, idx)
                if raw and summary:
                    results[idx] = (item.query, raw, summary)
                    current_queries[idx] = f"✅ {len(raw)} sources"
                    succeeded += 1
                else:
                    current_queries[idx] = "⚠️ No results"
            except Exception as e:
                current_queries[idx] = "❌ Failed"
                logger.error(f"S{idx}", str(e))
            completed += 1
        
        # Launch all
        tasks = [do_search(i, item) for i, item in enumerate(plan.searches, 1)]
        all_tasks = asyncio.gather(*tasks)
        
        # Live progress
        while completed < num:
            lines = []
            for i, q in enumerate(queries, 1):
                status = current_queries[i]
                lines.append(f"**{i}.** {q[:35]}... {status}")
            
            pct = int(completed / num * 100)
            bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
            
            yield self._status(
                f"🔍 SEARCHING [{completed}/{num}]",
                f"`[{bar}]` {pct}%",
                lines
            )
            await asyncio.sleep(0.4)
        
        await all_tasks
        
        # Collect summaries
        summaries = []
        summary_preview = []
        for idx in sorted(results.keys()):
            q, raw, summary = results[idx]
            summaries.append(summary)
            # Show first 80 chars of each summary
            preview = summary[:80].replace('\n', ' ') + "..."
            summary_preview.append(f"**{idx}.** {preview}")
        
        yield self._status(
            "✅ SEARCH COMPLETE",
            f"{succeeded}/{num} successful",
            summary_preview[:5]  # Show top 5 previews
        )
        await asyncio.sleep(0.5)
        
        if not summaries:
            yield self._status("❌ NO DATA", "Try a different topic", [])
            return
        
        # ===== WRITING =====
        yield self._status(
            "✍️ WRITING REPORT",
            f"Synthesizing {len(summaries)} sources...",
            [
                f"📊 Total research: {sum(len(s) for s in summaries):,} chars",
                "🤖 AI crafting your 3-paragraph report...",
                "⏱️ ~15-30 seconds..."
            ]
        )
        
        try:
            report = await write_report(query, summaries)
            logger.success("Research", "Done!")
            
            yield self._status("✅ DONE!", "Report ready 👇", [
                f"📝 {len(report):,} characters",
                f"📚 Based on {len(summaries)} sources"
            ]) + "\n<!--REPORT-->\n" + report
            
        except Exception as e:
            yield self._status("❌ WRITE ERROR", str(e)[:100], [])
    
    def _status(self, title: str, subtitle: str, details: list) -> str:
        out = f"## {title}\n\n"
        if subtitle:
            out += f"{subtitle}\n\n"
        if details:
            out += "---\n\n"
            for d in details:
                out += f"{d}\n\n"
        return out
