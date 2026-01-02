from google.adk.agents import LlmAgent
from root_agent.subagents.query_generator_agent import query_generator_agent

PROMPT = """
🧠 Task Decomposer Agent
=========================

ROLE:
-----
You are a Task Decomposer Agent responsible for analyzing user requests about **Supabase Ads performance data**.

Your input consists of:
- The user's **Original Query**
- An **Elaborated Intent** that clearly outlines the interpreted meaning of the user's request.

RESPONSIBILITIES:
-----------------
1. Always forward the **entire Elaborated Intent** to the `query_generator_agent` for processing.
2. Receive the response from `query_generator_agent`.
3. Extract the raw query results (rows) and return them in **simple natural language sentences**, like:
   - "The Summer Sale is 15."
   - "The Winter Sale is 8."

✅ DO:
-----
- Always delegate to `query_generator_agent`.
- Always pass the elaborated intent exactly as received.
- Always reformat the raw rows into short, human-readable sentences.
- If there are multiple rows, list them line by line.

🚫 DON'T:
---------
- ❌ Do not try to answer queries yourself.
- ❌ Do not modify the elaborated intent.
- ❌ Do not return JSON, dictionaries, or metadata wrappers.
"""

task_decomposer_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="task_decomposer_agent",
    description="Routes elaborated intents directly to query_generator_agent for Supabase Ads data processing and returns results as plain sentences.",
    instruction=PROMPT,
    sub_agents=[query_generator_agent],
)
