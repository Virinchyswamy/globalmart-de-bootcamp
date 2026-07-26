# Agent Use Cases for Data Engineers
## Content Type
Masterclass

## Overview
In this masterclass, you will learn when to use an AI agent instead of a single prompt, then build two real GlobalMart agents using LangChain on Databricks Free Edition. Starting with a 3-question decision framework to distinguish agent tasks from fixed scripts, you will understand the ReAct loop — the Thought → Action → Observation cycle that drives all agents in this track. You will build a SQL Review Agent with three tools (syntax checker, explainer, optimizer) and read the verbose trace to see how the LLM reasons between tool calls. You will then build a Pipeline Monitor Agent that checks table freshness and DQ failure counts for GlobalMart Silver tables and generates a standup-ready morning report — replacing 20–30 minutes of manual morning work with a single command. All runs are captured in MLflow for full observability.

## Learning Objectives
- Apply a 3-question decision framework to determine whether a task needs an agent or a fixed Python script
- Explain the ReAct loop (Thought → Action → Observation → repeat → Final Answer) using a GlobalMart DE example
- Write @tool functions with routing-quality docstrings that guide the LLM's tool selection decisions
- Build a SQL Review Agent using LangChain's ZERO_SHOT_REACT_DESCRIPTION pattern with three GlobalMart tools
- Interpret a verbose ReAct trace to understand the agent's reasoning and identify improvements to tool design
- Build a Pipeline Monitor Agent with check_table_freshness, count_dq_failures, and generate_status_report tools
- Enable MLflow autologging to capture a complete agent trace for debugging and production audit

## Prerequisites
- Completed Foundation Model API call pattern
- Python — functions, decorators, try/except
- Databricks notebook environment with LangChain installed (pip install langchain langchain-community)
- Familiarity with GlobalMart Silver layer tables

## Duration of Completion
null minutes

## Level
Intermediate

## Industries


## Tags


## Scenarios
### Pipeline Monitor Agent 
#### Overview
In this scenario you will build a Pipeline Monitor Agent that a data engineer would run each morning instead of manually checking each Silver table. The agent has three tools: check_table_freshness (reads Delta table history), count_dq_failures (counts quarantine records from today's run), and generate_status_report (calls the LLM to write a plain-English pipeline health summary). The agent decides which tables need alerts vs simple OK status, and produces a morning standup-ready report.

#### Level
intermediate

#### Industries
- general

#### Tags
- gen-ai (tool)
- python (tool)
- sql (tool)
- approach (skill)
- data-understanding (skill)
- problem-understanding (skill)
- ml-modelling (skill)
- ai-modelling (skill)
- generative-ai (skill)
- mlops (skill)
- llm-integration (skill)
- ai-engineering (skill)
- machine-learning (skill)
- databricks (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

### What the Pipeline Monitor Agent Replaces
<br>

Every morning a data engineer on the GlobalMart team checks:

```
1. When did gbmart.silver.customers last update?  → DESCRIBE HISTORY
2. When did gbmart.silver.orders last update?     → DESCRIBE HISTORY
3. How many records were quarantined today?        → SELECT COUNT(*) FROM quarantine WHERE DATE = today
4. Is anything stale or broken?                   → judgement call based on all the above
5. Write the morning Slack update                  → "Silver layer looks good. Customers: 3 mins ago..."
```

This is 20-30 minutes of manual work — reading Delta history, counting records, writing a summary.

**The Pipeline Monitor Agent does all of this in one command:**

```python
result = monitor_agent.run(
    "Run a morning health check on gbmart.silver.customers and gbmart.silver.orders. "
    "Flag any tables that are stale (>2 hours) or have high quarantine counts (>50 today). "
    "Produce a standup-ready status report."
)
print(result)
```

**Three tools you will build:**
<br>

| Tool | Reads from | Returns |
|------|-----------|---------|
| `check_table_freshness` | `DESCRIBE HISTORY <table>` | Age in hours + FRESH/STALE/UNKNOWN |
| `count_dq_failures` | `gbmart.silver.*_quarantine` WHERE date = today | Count + severity (OK/WARN/ALERT) |
| `generate_status_report` | Calls Foundation Model API | Plain-English pipeline health summary |


**Tags**


##### Input 2
**Type:** Code

**Question:** Task 1 — Build the Three Monitor Tools.
Fill in the docstrings for all three tools (the LLM reads these to decide when to call each tool) and fill in the missing logic in `count_dq_failures` to query today's quarantine records.

**Language:** python

**Snippet:** import mlflow
from langchain.tools import tool
from langchain.agents import AgentType, initialize_agent
from langchain_community.chat_models import ChatDatabricks
from databricks.sdk import WorkspaceClient
from datetime import datetime, timezone

w = WorkspaceClient()
ENDPOINT = "databricks-meta-llama-3-1-70b-instruct"


@tool
def check_table_freshness(table_name: str) -> str:
    """________"""   # TODO: describe when to call this and what it returns
    try:
        history_df = spark.sql(f"DESCRIBE HISTORY {table_name} LIMIT 1")
        last_update = history_df.collect()[0]["timestamp"]
        now = datetime.now(timezone.utc)
        if last_update.tzinfo is None:
            last_update = last_update.replace(tzinfo=timezone.utc)
        age_hours = (now - last_update).total_seconds() / 3600
        status = "FRESH" if age_hours < 2 else ("STALE" if age_hours < 24 else "VERY_STALE")
        return (f"Table: {table_name}\n"
                f"Last updated: {last_update.strftime('%Y-%m-%d %H:%M UTC')}\n"
                f"Age: {age_hours:.1f} hours\n"
                f"Status: {status}")
    except Exception as e:
        return f"UNKNOWN — could not read history for {table_name}: {str(e)[:200]}"


@tool
def count_dq_failures(table_name: str) -> str:
    """________"""   # TODO: describe when to call this and what it returns
    quarantine_table = table_name.replace(".silver.", ".silver.") + "_quarantine"
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        count_df = spark.sql(f"""
            ________
        """)   # TODO: count today's quarantine records. Hint: WHERE DATE(_quarantine_ts) = '{today}'
        count = count_df.collect()[0][0]
        severity = "OK" if count == 0 else ("WARN" if count <= 50 else "ALERT")
        return (f"Quarantine table: {quarantine_table}\n"
                f"Date: {today}\n"
                f"Records quarantined today: {count}\n"
                f"Severity: {severity}")
    except Exception as e:
        return f"Could not count quarantine records for {table_name}: {str(e)[:200]}"


@tool
def generate_status_report(pipeline_observations: str) -> str:
    """________"""   # TODO: describe when to call this — should be called LAST after collecting all observations
    SYSTEM_PROMPT = """You are a senior data engineer writing a morning pipeline health report for the GlobalMart team.
Given a set of pipeline observations (freshness checks, DQ failure counts):
1. Start with an overall status: ALL GOOD / ATTENTION NEEDED / ALERT
2. Summarize each table's status in one bullet point
3. List any recommended actions for STALE or ALERT severity items
4. Keep the total report under 150 words
5. Write for a standup meeting — technical but concise, no raw SQL or table paths"""

    response = w.serving_endpoints.predict(
        endpoint=ENDPOINT,
        inputs={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Write a morning pipeline health report based on these observations:\n\n{pipeline_observations}"}
            ],
            "temperature": 0.0,
            "max_tokens": 400
        }
    )
    return response["choices"][0]["message"]["content"]

**Solution:** 
```python
@tool
def check_table_freshness(table_name: str) -> str:
    """Check how recently a GlobalMart Delta table was last updated. Call this tool for each
    table you need to monitor. Input is the fully qualified table name (e.g., gbmart.silver.customers).
    Returns: last update timestamp, age in hours, and status (FRESH if <2h, STALE if 2-24h,
    VERY_STALE if >24h). Call this before count_dq_failures for each table."""
    try:
        history_df = spark.sql(f"DESCRIBE HISTORY {table_name} LIMIT 1")
        last_update = history_df.collect()[0]["timestamp"]
        now = datetime.now(timezone.utc)
        if last_update.tzinfo is None:
            last_update = last_update.replace(tzinfo=timezone.utc)
        age_hours = (now - last_update).total_seconds() / 3600
        status = "FRESH" if age_hours < 2 else ("STALE" if age_hours < 24 else "VERY_STALE")
        return (f"Table: {table_name}\n"
                f"Last updated: {last_update.strftime('%Y-%m-%d %H:%M UTC')}\n"
                f"Age: {age_hours:.1f} hours\n"
                f"Status: {status}")
    except Exception as e:
        return f"UNKNOWN — could not read history for {table_name}: {str(e)[:200]}"


@tool
def count_dq_failures(table_name: str) -> str:
    """Count how many records were quarantined today for a GlobalMart Silver table. Call this
    after check_table_freshness confirms the table was updated recently. Input is the fully qualified
    Silver table name (e.g., gbmart.silver.customers — the tool will find the corresponding quarantine
    table automatically). Returns: quarantine count for today and severity (OK=0, WARN=1-50, ALERT=>50)."""
    quarantine_table = table_name.replace(".silver.", ".silver.") + "_quarantine"
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        count_df = spark.sql(f"""
            SELECT COUNT(*) FROM {quarantine_table}
            WHERE DATE(_quarantine_ts) = '{today}'
        """)
        count = count_df.collect()[0][0]
        severity = "OK" if count == 0 else ("WARN" if count <= 50 else "ALERT")
        return (f"Quarantine table: {quarantine_table}\n"
                f"Date: {today}\n"
                f"Records quarantined today: {count}\n"
                f"Severity: {severity}")
    except Exception as e:
        return f"Could not count quarantine records for {table_name}: {str(e)[:200]}"


@tool
def generate_status_report(pipeline_observations: str) -> str:
    """Generate a plain-English morning pipeline health report. Call this LAST, after you have
    collected freshness and DQ failure information for all tables. Input is a text summary of all
    observations gathered from check_table_freshness and count_dq_failures. Returns a standup-ready
    pipeline health report with overall status, per-table bullets, and recommended actions."""
    SYSTEM_PROMPT = """You are a senior data engineer writing a morning pipeline health report for the GlobalMart team.
Given a set of pipeline observations (freshness checks, DQ failure counts):
1. Start with an overall status: ALL GOOD / ATTENTION NEEDED / ALERT
2. Summarize each table's status in one bullet point
3. List any recommended actions for STALE or ALERT severity items
4. Keep the total report under 150 words
5. Write for a standup meeting — technical but concise, no raw SQL or table paths"""

    response = w.serving_endpoints.predict(
        endpoint=ENDPOINT,
        inputs={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Write a morning pipeline health report based on these observations:\n\n{pipeline_observations}"}
            ],
            "temperature": 0.0,
            "max_tokens": 400
        }
    )
    return response["choices"][0]["message"]["content"]
```

**Tags**
- generative-ai / agentic-ai / tool-calling (skill)

##### Input 3
**Type:** Code

**Question:** Task 2 — Initialize Agent with MLflow Autologging.
Fill in the two blanks to (a) enable MLflow autologging for LangChain agents and (b) start the MLflow run that captures the agent trace. Then run the monitor on both GlobalMart Silver tables.
MLflow autologging for LangChain captures every Thought → Action → Observation step automatically — you can view it under Experiments → your run → Traces tab in the Databricks UI.

**Language:** python

**Snippet:** # Enable MLflow autologging for LangChain
________   # TODO: enable langchain autologging in mlflow

tools = [check_table_freshness, count_dq_failures, generate_status_report]

llm = ChatDatabricks(
    endpoint="databricks-meta-llama-3-1-70b-instruct",
    temperature=0.0
)

monitor_agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    max_iterations=10,
    handle_parsing_errors=True
)

# Run with MLflow tracking
with ________("GlobalMart-Pipeline-Monitor"):   # TODO: start mlflow run
    result = monitor_agent.run(
        "Run a morning health check on the following GlobalMart Silver tables: "
        "gbmart.silver.customers and gbmart.silver.orders. "
        "For each table: check freshness, then count today's DQ failures. "
        "After checking both tables, generate a standup-ready pipeline status report. "
        "Flag any table that is STALE or has ALERT-level DQ failures."
    )

print("\n" + "="*60)
print("MORNING PIPELINE REPORT:")
print("="*60)
print(result)
print("\n[Check Experiments → Traces tab for the full agent trace]")

**Solution:** 
```python
import mlflow

mlflow.langchain.autolog()

tools = [check_table_freshness, count_dq_failures, generate_status_report]

llm = ChatDatabricks(
    endpoint="databricks-meta-llama-3-1-70b-instruct",
    temperature=0.0
)

monitor_agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    max_iterations=10,
    handle_parsing_errors=True
)

with mlflow.start_run(run_name="GlobalMart-Pipeline-Monitor"):
    result = monitor_agent.run(
        "Run a morning health check on the following GlobalMart Silver tables: "
        "gbmart.silver.customers and gbmart.silver.orders. "
        "For each table: check freshness, then count today's DQ failures. "
        "After checking both tables, generate a standup-ready pipeline status report. "
        "Flag any table that is STALE or has ALERT-level DQ failures."
    )

print(result)

# Expected agent trace (from verbose output):
# Thought: "I need to check both tables. Start with customers freshness."
# Action: check_table_freshness | Input: gbmart.silver.customers
# Observation: "Last updated: 2026-07-23 04:30 UTC | Age: 1.2h | Status: FRESH"
#
# Thought: "Customers is fresh. Check DQ failures for customers."
# Action: count_dq_failures | Input: gbmart.silver.customers
# Observation: "Records quarantined today: 77 | Severity: ALERT"
#
# Thought: "Customers has ALERT-level DQ failures. Now check orders freshness."
# Action: check_table_freshness | Input: gbmart.silver.orders
# Observation: "Last updated: 2026-07-23 04:35 UTC | Age: 1.1h | Status: FRESH"
#
# Thought: "Orders is fresh. Check DQ failures for orders."
# Action: count_dq_failures | Input: gbmart.silver.orders
# Observation: "Records quarantined today: 12 | Severity: WARN"
#
# Thought: "I have both tables' status. Customers is ALERT. Generate report."
# Action: generate_status_report | Input: [all observations combined]
# Final Answer: [standup-ready report]
```

**Tags**
- generative-ai / agentic-ai / agent-initialization (skill)

##### Input 4
**Type:** Choice

**Question:** After running the agent with MLflow autologging, you open the Traces tab in Databricks Experiments. You see the agent called tools in this order: `check_table_freshness(customers)` → `count_dq_failures(customers)` → `check_table_freshness(orders)` → `count_dq_failures(orders)` → `generate_status_report`. Why did the agent call `check_table_freshness` BEFORE `count_dq_failures` for each table, rather than checking freshness for all tables first?

**Options:** 
- The tool descriptions forced this order — check_table_freshness mentions "call before count_dq_failures"

- The agent followed a fixed pipeline defined in its system prompt

- The agent reasoned that DQ failure counts are only meaningful if the table ran recently — so it validated freshness per-table before checking failures, treating each table as an independent investigation

- LangChain always calls tools in the order they are listed in the tools array

**Correct Options:** 
- The agent reasoned that DQ failure counts are only meaningful if the table ran recently — so it validated freshness per-table before checking failures, treating each table as an independent investigation

**Solution:** 
This is emergent reasoning from the ReAct loop — the agent was not explicitly instructed to check freshness before DQ failures per table. It inferred that a DQ failure count is meaningless if the pipeline didn't run recently (no run = no new quarantine records, so count of 0 is misleading). The tool descriptions helped by saying "Call this after check_table_freshness confirms the table was updated recently" — that phrasing guided the agent's reasoning without hard-coding a sequence. This is the key benefit of well-written tool docstrings: they shape agent reasoning without removing its flexibility.

**Tags**
- mlops / model-retraining / monitoring-drift / drift-metrics-logging (skill)

##### Input 5
**Type:** File Upload

**Question:** Run the Pipeline Monitor Agent on `gbmart.silver.customers` and at least one other Silver table. Take a screenshot showing:
1. The verbose output in your Databricks notebook (showing at least 3 Thought → Action → Observation cycles)
2. The final printed report
Upload the screenshot here.

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**
- approach / concept-clarity (skill)

##### Input 6
**Type:** Short Answer

**Question:** Your Pipeline Monitor Agent currently runs on demand (you call `agent.run()` manually). A colleague suggests: "We should schedule this as a Databricks Workflow job that runs at 6:00 AM every day and sends the report to our team Slack channel." In 3–4 sentences, describe what you would add to the agent architecture to make this production-ready — what new tool, what scheduling mechanism, and what failure handling.

**Template:** null

**Solution:** 
To make the agent production-ready, add a fourth tool `send_slack_alert(report: str, channel: str)` that calls the Slack API with the generated report — the agent already knows when to alert vs report OK, so it can decide which Slack channel to use (alert channel vs daily digest). Schedule it as a Databricks Workflow with a cron trigger at 06:00 IST using a Python task type running this notebook; set the job to retry once on failure with a 5-minute delay. For failure handling, wrap the `monitor_agent.run()` call in a try/except — if the agent itself fails (e.g., max_iterations exceeded), send a fallback Slack message directly (not via agent) saying "Pipeline Monitor Agent failed to run — manual check required" so the team is never silently left without a morning status.

**Tags**
- generative-ai / agentic-ai / tool-calling (skill)
- approach / concept-clarity (skill)

### SQL Review Agent 
#### Overview
In this scenario you will build a SQL Review Agent using LangChain on Databricks. The agent has three tools: check_syntax (validates the query can be parsed), explain_query (calls the LLM to explain what the query does), and suggest_optimization (calls the LLM with the few-shot optimizer from MC-PE-01). Given a SQL query, the agent decides which tools to call and in what order, then produces a structured review report. You will see the ReAct trace — the agent's step-by-step reasoning — in the output.

#### Level
intermediate

#### Industries
- general

#### Tags
- approach (skill)
- data-understanding (skill)
- problem-understanding (skill)
- ml-modelling (skill)
- ai-modelling (skill)
- generative-ai (skill)
- mlops (skill)
- llm-integration (skill)
- ai-engineering (skill)
- machine-learning (skill)
- databricks (tool)
- sql (tool)
- gen-ai (tool)
- python (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

### What the SQL Review Agent Does
<br>

The SQL Review Agent is a tool a senior data engineer would use to sanity-check queries before they hit production. Today you build it — tomorrow it saves you 15 minutes per query review.

**Agent flow:**

```
User: "Review this GlobalMart query: SELECT * FROM gbmart.silver.customers,
       gbmart.silver.orders WHERE customers.customer_id = orders.customer_id"

Agent:
  Thought: "First I should check if this SQL is syntactically valid."
  Action: check_syntax
  Input: "SELECT * FROM gbmart.silver.customers, ..."
  Observation: "VALID — query parses successfully"

  Thought: "Query is valid. Now I should explain what it does."
  Action: explain_query
  Input: "SELECT * FROM gbmart.silver.customers, ..."
  Observation: "This query joins the Silver customers and orders tables using
                an implicit comma JOIN, returning all columns for all matching records."

  Thought: "Implicit comma JOIN is a performance concern. I should check for optimizations."
  Action: suggest_optimization
  Input: "SELECT * FROM gbmart.silver.customers, ..."
  Observation: "BEFORE: ... AFTER: ... -- Change: Replace implicit JOIN with explicit JOIN"

  Final Answer: "Query Review Report:
  ✓ Syntax: Valid
  ℹ Explanation: Joins customers to orders, returns all matching rows.
  ⚠ Optimization: Replace implicit comma JOIN with explicit JOIN; remove SELECT *."
```

**Three tools you will build:**
1. `check_syntax` — runs a Spark `EXPLAIN` to validate the query without executing it
2. `explain_query` — calls the Foundation Model API with the explainer system prompt from MC-PE-01
3. `suggest_optimization` — calls the Foundation Model API with the few-shot optimizer from MC-PE-01



**Tags**


##### Input 2
**Type:** Code

**Question:** Task 1 — Define the Three Tools.
Fill in the three `@tool` functions. Each tool has a critical docstring — the LLM reads this description to decide when to call the tool, so it must be clear about what the tool does and when to use it.

**Language:** python

**Snippet:** # Install if needed: pip install langchain langchain-community
from langchain.agents import AgentType, initialize_agent
from langchain.tools import tool
from langchain_community.chat_models import ChatDatabricks
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
ENDPOINT = "databricks-meta-llama-3-1-70b-instruct"


@tool
def check_syntax(query: str) -> str:
    """________"""   # TODO: clear description — when should the agent call this?
    try:
        spark.sql(f"EXPLAIN {query}")
        return "VALID — query parses successfully and can be executed"
    except Exception as e:
        return f"INVALID — syntax error: {str(e)[:300]}"


@tool
def explain_query(query: str) -> str:
    """________"""   # TODO: clear description — when should the agent call this?
    SYSTEM_PROMPT = """You are a senior SQL reviewer for GlobalMart (retail analytics, Unity Catalog).
When given a SQL query:
1. Explain in plain English what the query returns (1-2 sentences)
2. Identify the main tables joined and the reason for each join
3. Note any performance concern (missing partition filter, SELECT *, implicit JOIN)
Keep response under 120 words. No code."""

    response = w.serving_endpoints.predict(
        endpoint=ENDPOINT,
        inputs={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Explain this GlobalMart SQL query:\n\n{query}"}
            ],
            "temperature": 0.0,
            "max_tokens": 300
        }
    )
    return response["choices"][0]["message"]["content"]


@tool
def suggest_optimization(query: str) -> str:
    """________"""   # TODO: clear description — when should the agent call this?
    FEW_SHOT = """Example 1:
BEFORE: SELECT * FROM gbmart.silver.customers WHERE email LIKE '%gmail%'
AFTER:  SELECT customer_id, email FROM gbmart.silver.customers WHERE email LIKE '%gmail%'
-- Change: Removed SELECT *, selected only needed columns to reduce shuffle.

Example 2:
BEFORE: SELECT o.order_id, c.full_name FROM gbmart.silver.orders o,
        gbmart.silver.customers c WHERE o.customer_id = c.customer_id
AFTER:  SELECT o.order_id, c.full_name FROM gbmart.silver.orders o
        JOIN gbmart.silver.customers c ON o.customer_id = c.customer_id
-- Change: Replaced implicit comma join with explicit JOIN."""

    SYSTEM_PROMPT = f"""You are GlobalMart's SQL optimizer. Apply the conventions shown below.
Always output:
BEFORE: [original query]
AFTER:  [optimized query]
-- Change: [one sentence explaining the change]

{FEW_SHOT}"""

    response = w.serving_endpoints.predict(
        endpoint=ENDPOINT,
        inputs={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Optimize this query:\nBEFORE: {query}"}
            ],
            "temperature": 0.0,
            "max_tokens": 400
        }
    )
    return response["choices"][0]["message"]["content"]

**Solution:** 
```python
@tool
def check_syntax(query: str) -> str:
    """Use this tool FIRST on any SQL query to check if it is syntactically valid before
    running explanation or optimization. Input is a SQL query string. Returns 'VALID' if the
    query can be parsed by Spark, or 'INVALID: [error]' if there is a syntax error."""
    try:
        spark.sql(f"EXPLAIN {query}")
        return "VALID — query parses successfully and can be executed"
    except Exception as e:
        return f"INVALID — syntax error: {str(e)[:300]}"


@tool
def explain_query(query: str) -> str:
    """Use this tool to explain what a SQL query does in plain English. Call this AFTER
    check_syntax confirms the query is valid. Input is a SQL query string. Returns a
    plain-English explanation including: what data is returned, which tables are joined, and
    any performance concerns flagged."""
    SYSTEM_PROMPT = """You are a senior SQL reviewer for GlobalMart (retail analytics, Unity Catalog).
When given a SQL query:
1. Explain in plain English what the query returns (1-2 sentences)
2. Identify the main tables joined and the reason for each join
3. Note any performance concern (missing partition filter, SELECT *, implicit JOIN)
Keep response under 120 words. No code."""

    response = w.serving_endpoints.predict(
        endpoint=ENDPOINT,
        inputs={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Explain this GlobalMart SQL query:\n\n{query}"}
            ],
            "temperature": 0.0,
            "max_tokens": 300
        }
    )
    return response["choices"][0]["message"]["content"]


@tool
def suggest_optimization(query: str) -> str:
    """Use this tool to suggest performance optimizations for a GlobalMart SQL query.
    Call this when explain_query identifies a performance concern (SELECT *, implicit JOIN,
    missing filter). Input is a SQL query string. Returns BEFORE/AFTER SQL with a one-line
    explanation of the change."""
    FEW_SHOT = """Example 1:
BEFORE: SELECT * FROM gbmart.silver.customers WHERE email LIKE '%gmail%'
AFTER:  SELECT customer_id, email FROM gbmart.silver.customers WHERE email LIKE '%gmail%'
-- Change: Removed SELECT *, selected only needed columns to reduce shuffle.

Example 2:
BEFORE: SELECT o.order_id, c.full_name FROM gbmart.silver.orders o,
        gbmart.silver.customers c WHERE o.customer_id = c.customer_id
AFTER:  SELECT o.order_id, c.full_name FROM gbmart.silver.orders o
        JOIN gbmart.silver.customers c ON o.customer_id = c.customer_id
-- Change: Replaced implicit comma join with explicit JOIN."""

    SYSTEM_PROMPT = f"""You are GlobalMart's SQL optimizer. Apply the conventions shown below.
Always output:
BEFORE: [original query]
AFTER:  [optimized query]
-- Change: [one sentence explaining the change]

{FEW_SHOT}"""

    response = w.serving_endpoints.predict(
        endpoint=ENDPOINT,
        inputs={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Optimize this query:\nBEFORE: {query}"}
            ],
            "temperature": 0.0,
            "max_tokens": 400
        }
    )
    return response["choices"][0]["message"]["content"]
```

**Tags**
- generative-ai / agentic-ai / tool-calling (skill)

##### Input 3
**Type:** Code

**Question:** Task 2 — Initialize and Run the Agent.
Fill in the two blanks to initialize the SQL Review Agent and run it on the test query. After running, read the verbose trace and identify: (a) the order in which the agent called the tools, and (b) whether it called all three tools or stopped early.

**Language:** python

**Snippet:** tools = [check_syntax, explain_query, suggest_optimization]

llm = ChatDatabricks(
    endpoint="databricks-meta-llama-3-1-70b-instruct",
    temperature=0.0
)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    max_iterations=________,       # TODO: set a safe limit (hint: 3 tools × 2 = safe ceiling)
    handle_parsing_errors=________  # TODO: should be True for production agents
)


TEST_QUERY = """
SELECT * FROM gbmart.silver.customers c,
              gbmart.silver.orders o,
              gbmart.silver.order_items oi
WHERE c.customer_id = o.customer_id
AND   o.order_id    = oi.order_id
"""

print("Running SQL Review Agent...\n")
result = agent.run(f"Please review this GlobalMart SQL query and provide a complete review report:\n{TEST_QUERY}")
print("\n" + "="*60)
print("FINAL REVIEW REPORT:")
print("="*60)
print(result)

**Solution:** 
```python
tools = [check_syntax, explain_query, suggest_optimization]

llm = ChatDatabricks(
    endpoint="databricks-meta-llama-3-1-70b-instruct",
    temperature=0.0
)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    max_iterations=8,         # 3 tools × ~2 calls each, plus reasoning steps
    handle_parsing_errors=True
)

TEST_QUERY = """
SELECT * FROM gbmart.silver.customers c,
              gbmart.silver.orders o,
              gbmart.silver.order_items oi
WHERE c.customer_id = o.customer_id
AND   o.order_id    = oi.order_id
"""

result = agent.run(f"Please review this GlobalMart SQL query and provide a complete review report:\n{TEST_QUERY}")
print(result)

# Expected trace order:
# 1. check_syntax → VALID
# 2. explain_query → "This query returns all columns from customers, orders, and order_items..."
# 3. suggest_optimization → "BEFORE: SELECT * ... AFTER: SELECT specific columns ... JOIN explicitly"
# Final Answer: structured review report summarizing all three tool outputs
```

**Tags**
- generative-ai / agentic-ai / agent-initialization (skill)

##### Input 4
**Type:** Choice

**Question:** After running the agent, you see in the verbose output:

**Options:** 
- No — the agent should have called `suggest_optimization` first, then explained the result

- Yes — the agent correctly reasoned from Observation to next tool, checking syntax before explanation, and triggering optimization based on the explain output flagging SELECT *

- No — an agent should never call the same category of tool (LLM-based) twice in one run

- Yes — but only because max_iterations was set to 8

**Correct Options:** 
- Yes — the agent correctly reasoned from Observation to next tool, checking syntax before explanation, and triggering optimization based on the explain output flagging SELECT *

**Solution:** 
This is exactly the ReAct loop working correctly. The agent used the explain_query observation ("SELECT * as a concern") to decide that optimization was warranted — a decision it could not have made without seeing that intermediate result. This is the core value of the agent over a fixed script: it reads the output of each tool before choosing the next one. The max_iterations setting is a safety mechanism, not a decision driver — the agent would have made the same three calls even if max_iterations were 20.

**Tags**
- generative-ai / agentic-ai / agent-state (skill)

##### Input 5
**Type:** Short Answer

**Question:** Your SQL Review Agent worked correctly. Now a colleague asks: "Can we add a fourth tool called `execute_query` that actually runs the SQL on the GlobalMart tables and returns the results?"

**Template:** null

**Solution:** 
Adding `execute_query` means the LLM can run arbitrary SQL on production GlobalMart tables — including destructive operations if the tool is not constrained properly. The risk is that the LLM might, in a reasoning chain, decide to "verify" its explanation by running the query, which could be an expensive full-table scan on `gbmart.silver.orders` (millions of rows) or — in a worst-case prompt injection scenario — a DROP TABLE. Before building it, two safeguards are essential: (1) restrict the tool to read-only SQL by raising an exception if the query contains DDL keywords (DROP, ALTER, INSERT, UPDATE, DELETE), and (2) add a `LIMIT 100` clause automatically before executing so the tool can never run an unbounded scan regardless of what the LLM passes. A third safeguard worth adding: require the agent to call `check_syntax` and log the query before `execute_query` is permitted.

**Tags**
- generative-ai / agentic-ai / tool-calling (skill)

### When to Use an Agent vs a Single Prompt
#### Overview
In this scenario you will learn to distinguish between tasks that need a single LLM call and tasks that need an agent. You will build a decision framework grounded in GlobalMart DE work, walk through three real examples of DE tasks and decide which approach fits each, and understand the ReAct loop pattern that all agents in this program use. This scenario is concept-heavy and sets the foundation 

#### Level
intermediate

#### Industries
- general

#### Tags
- approach (skill)
- data-understanding (skill)
- problem-understanding (skill)
- ml-modelling (skill)
- ai-modelling (skill)
- generative-ai (skill)
- llm-integration (skill)
- ai-engineering (skill)
- machine-learning (skill)
- databricks (tool)
- sql (tool)
- gen-ai (tool)
- python (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

### Single Prompt vs Agent — What's the Difference?
<br>

All three tools you built in MC-PE-01 used a single LLM call. You sent a prompt, got an answer, done.

An **agent** is different: it runs a loop. Each iteration the LLM decides what to do next — call a tool, check the result, then decide again — until it has enough information to give a final answer.

![Image](https://cdn.enqurious.com/images/36ed80e5-76fd-4ca1-90b7-b0d47d1ed293_Screenshot-2026-07-24-at-12.webp)

**The key difference:** In a single prompt, you do the reasoning ("I need to explain this query → write the explainer prompt"). In an agent, the LLM does the reasoning ("I need to check the table freshness first, then check DQ failures, then decide whether to send an alert").



**Tags**


##### Input 2
**Type:** Text

### The 3-Question Decision Framework
<br>
Use this to decide whether to build an agent or stick with a single prompt:

![Image](https://cdn.enqurious.com/images/5557f635-a669-47d1-aaf9-6a7bd0597180_Screenshot-2026-07-24-at-12.webp)

**One more heuristic:** If you can write out all the steps as a fixed numbered list before running, it is probably NOT an agent task — it's a Python script with some LLM calls in it. Agents are for tasks where the LLM must figure out the steps at runtime.



**Tags**


##### Input 3
**Type:** Choice

**Question:** A GlobalMart DE runs this every morning: (1) read the DQ scan output from `gbmart.silver.customers_quarantine`, (2) count the number of new records added today, (3) send a Slack notification with the count. Should this be an agent or a Python script with LLM calls?

**Options:** 
- Agent — it has multiple steps, so it must be an agent

- Python script with LLM calls — the steps are fixed and pre-determined, no tool-choice branching needed

- Agent — because it involves data quality

- Python script — because it does not use the Foundation Model API at all

**Correct Options:** 
- Python script with LLM calls — the steps are fixed and pre-determined, no tool-choice branching needed

**Solution:** 
The three steps are fully determined before runtime — always read quarantine, always count, always send Slack. There is no branching: the pipeline does not need to choose step 3 based on what step 2 returned. This is a fixed sequence of operations, some of which might call an LLM (e.g., to format the Slack message in plain English). Use a Python script with LLM calls for the message generation, not an agent. Agents add overhead (multiple LLM calls per task, harder to debug) — only use them when the LLM must make routing decisions.

**Tags**
- generative-ai / agentic-ai / sequential-chain (skill)

##### Input 4
**Type:** Choice

**Question:** A GlobalMart DE needs a tool that, given any DQ error scenario, decides whether to: (a) auto-fix and write to Silver, (b) quarantine and alert, or (c) escalate to the senior engineer with a detailed brief. The decision depends on reading the quarantine counts, checking whether the issue type is known, and looking up the historical fix success rate. Should this be an agent or a fixed Python script?

**Options:** 
- Fixed Python script — write a series of if/elif statements for each DQ issue type

- Agent — the routing decision depends on runtime data from multiple tools, and can't be pre-determined

- Single LLM call with a very detailed prompt

- Agent — only because it has more than 2 steps

**Correct Options:** 
- Agent — the routing decision depends on runtime data from multiple tools, and can't be pre-determined

**Solution:** 
This is an agent task because Q1 from the framework is YES: which action to take (fix / quarantine / escalate) cannot be decided at design time — it depends on what `check_dq_issue_type()`, `get_quarantine_count()`, and `get_fix_success_rate()` return at runtime. The LLM must observe the results of these tools and reason about which path to take. A fixed if/elif script would work only if the decision rules are exhaustive and static — but DQ issues are varied and new issue types appear regularly. The agent's flexibility in routing to the right tool based on intermediate results is exactly what makes it the right choice here.

**Tags**
- generative-ai / agentic-ai / multi-agent-systems (skill)

##### Input 5
**Type:** Text

### The ReAct Loop — How Agents Reason
<br>

Every agent in this module uses the **ReAct** pattern (Reason + Act). The loop has four steps that repeat until the agent has a final answer:

![Image](https://cdn.enqurious.com/images/02873282-de2a-417b-a247-ba27823a328e_Screenshot-2026-07-24-at-12.webp)

**What you provide when building a ReAct agent:**
1. A set of `@tool` functions the LLM can call
2. A description for each tool (the LLM reads these to decide which to call)
3. An LLM (the "brain" that does the reasoning)
4. A max_iterations limit (prevents infinite loops)

**What LangChain provides:**
- The ReAct loop itself (Thought → Action → Observation → repeat)
- Tool invocation and result injection
- `AgentType.ZERO_SHOT_REACT_DESCRIPTION` — the standard ReAct agent type
- `handle_parsing_errors=True` — graceful recovery from malformed LLM output



**Tags**


##### Input 6
**Type:** Choice

**Question:** You are building a Pipeline Monitor Agent for GlobalMart. It should check whether `gbmart.silver.customers` is fresh, count the DQ failures, and then decide whether to generate an OK report or an alert. What is the minimum set of tools this agent needs?

**Options:** 
- One tool: `run_full_pipeline_check(table_name)` that does all three steps inside one function

- Three tools: `check_freshness()`, `count_dq_failures()`, `generate_report()` — so the agent can call each independently and reason between them

- Two tools: `check_freshness()` and `generate_report()` — the DQ count can be hardcoded

- No tools — the LLM should figure out the table status from its training data

**Correct Options:** 
- Three tools: `check_freshness()`, `count_dq_failures()`, `generate_report()` — so the agent can call each independently and reason between them

**Solution:** 
Agents derive their value from being able to reason BETWEEN tool calls — seeing the freshness result, deciding whether the DQ count is even worth checking, then deciding which type of report to generate. If you collapse everything into one tool (`run_full_pipeline_check`), the LLM becomes a glorified function-caller with no decision-making. Three separate tools with clear descriptions is the correct design — it lets the LLM compose the workflow based on what each step returns.

**Tags**
- generative-ai / agentic-ai / tool-calling (skill)

##### Input 7
**Type:** Short Answer

**Question:** You show a colleague the ReAct loop diagram. They ask: "Why does the LLM get to see the tool's output (the Observation) before deciding the next step? Can't you just chain all the tools together in a fixed order?"

**Template:** null

**Solution:** 
The Observation step is what makes a ReAct agent smarter than a fixed pipeline — the LLM sees what the tool actually returned and can change course based on the result. In a fixed chain, you decide the steps at design time and run them regardless of outcome; with ReAct, the LLM decides what to do next after seeing the evidence. A concrete GlobalMart example: if the Pipeline Monitor Agent calls `check_table_freshness("gbmart.silver.customers")` and gets back "Last updated 2 hours ago — table is FRESH", the agent should skip calling `count_dq_failures()` and go straight to `generate_ok_report()`. If instead it gets "Last updated 26 hours ago — table is STALE", it should call `count_dq_failures()` to understand why the pipeline missed its window before generating an alert. A fixed chain cannot make this branch — it always calls all tools in the same order regardless of the freshness result.

**Tags**
- generative-ai / agentic-ai / sequential-chain (skill)
- generative-ai / agentic-ai / agent-orchestration (skill)

