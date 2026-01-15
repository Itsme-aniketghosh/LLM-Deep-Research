"""
Deep Research - Live refreshing status
"""

import gradio as gr
from research_manager import ResearchManager


async def run_research(query: str):
    """Status panel refreshes each step, report appears at end"""
    if not query.strip():
        yield "**Enter a topic above**", ""
        return
    
    status = ""
    report = ""
    
    async for chunk in ResearchManager().run(query):
        if "<!--REPORT-->" in chunk:
            parts = chunk.split("<!--REPORT-->")
            status = parts[0].strip()
            report = parts[1].strip() if len(parts) > 1 else ""
        else:
            status = chunk  # Replace, don't append
        
        yield status, report


with gr.Blocks(title="Deep Research") as demo:
    gr.Markdown("# 🔬 Deep Research AI")
    
    with gr.Row():
        query = gr.Textbox(
            placeholder="Enter any topic...",
            label="Topic",
            scale=5
        )
        btn = gr.Button("🚀 Research", variant="primary", scale=1)
    
    with gr.Row():
        with gr.Column(scale=1):
            status = gr.Markdown("*Waiting...*", label="Status")
        with gr.Column(scale=2):
            report = gr.Markdown("*Report appears here*", label="Report")
    
    btn.click(run_research, query, [status, report])
    query.submit(run_research, query, [status, report])

if __name__ == "__main__":
    demo.launch()
