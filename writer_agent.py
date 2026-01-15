"""
Writer Agent - Uses structured research input
"""

from llm_client import get_llm
import logger


SYSTEM_PROMPT = """You are a brilliant journalist writing for Wired or The Atlantic.

You have research organized into HOOK (surprising facts), KEY FACTS (specifics), and INSIGHTS (meaning).

Write EXACTLY 3 paragraphs:

**PARAGRAPH 1 - THE HOOK (4-5 sentences)**
Open with the most surprising statistic or claim from your research. Make it punchy. Then quickly set up what this topic is about and why it matters right now.

**PARAGRAPH 2 - THE SUBSTANCE (5-6 sentences)**  
The meat. Weave together the best facts from your research. Use specific numbers, real examples, expert names. Show you've done your homework. Make connections.

**PARAGRAPH 3 - THE TAKEAWAY (3-4 sentences)**
Land it. What does this all add up to? Give the reader an insight they can walk away with. End strong.

RULES:
- Exactly 3 paragraphs
- Every sentence must be different - NO repetition
- Use the specific facts from your research
- Write with confidence and style
- Make it something people would share

Write now:"""


async def write_report(query: str, summaries: list[str]) -> str:
    logger.step("Writer", f"Crafting from {len(summaries)} sources")
    
    # Combine all research
    research = "\n\n---\n\n".join([s for s in summaries if len(s) > 30])
    
    if len(research) < 100:
        return f"# {query}\n\nInsufficient research data."
    
    llm = get_llm()
    
    prompt = f"""TOPIC: {query}

YOUR RESEARCH:
{research[]}

Using the HOOKS, FACTS, and INSIGHTS above, write 3 powerful paragraphs."""
    
    report = await llm.generate(prompt, system_prompt=SYSTEM_PROMPT)
    
    # Clean
    report = clean_output(report)
    
    # Add title
    final = f"# {query.title()}\n\n{report}"
    
    logger.success("Writer", f"{len(final)} chars")
    return final


def clean_output(text: str) -> str:
    """Remove any duplicate lines"""
    lines = text.strip().split('\n')
    seen = set()
    clean = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if clean and clean[-1] != '':
                clean.append('')
            continue
        
        # Check first 50 chars for duplicates
        key = stripped.lower()[:50]
        if key not in seen:
            seen.add(key)
            clean.append(line)
    
    return '\n'.join(clean).strip()
