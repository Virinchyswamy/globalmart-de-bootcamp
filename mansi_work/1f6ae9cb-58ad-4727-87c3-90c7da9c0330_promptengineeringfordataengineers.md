# Prompt Engineering for Data Engineers
## Content Type
Masterclass

## Overview
In this masterclass, you will use the Databricks Foundation Model API to build three practical productivity tools grounded in your GlobalMart DE work. You will build a SQL explainer that translates complex queries into plain English, a few-shot SQL optimizer that learns your team's conventions, and a natural-language-to-SQL translator. You will then enhance real PySpark functions with AI-generated docstrings and defensive error handling using chain-of-thought prompting. Finally, you will build a DQ failure reporter that translates error codes into business-ready stakeholder communication and a structured data dictionary generator. 

## Learning Objectives
- Use zero-shot prompting to explain complex GlobalMart SQL queries in plain English with a structured 3-part output
- Use few-shot prompting to teach an LLM your team's SQL conventions and apply them to new queries
- Build a natural-language-to-SQL translator grounded in the GlobalMart schema that avoids hallucinating table names
- Generate professional Google-style docstrings for PySpark transformation functions without changing function logic
- Add defensive error handling to DE code using chain-of-thought prompting to identify failure modes first
- Build a DQ failure explainer that translates error codes like REGISTERED_UNDER_18 into plain-English business reports
- Generate a structured JSON data dictionary from a table schema using structured output prompting

## Prerequisites
- SQL — JOINs, CTEs, window functions
- Python basics — functions, f-strings, print statements
- PySpark — DataFrames, withColumn, when/otherwise
- Databricks notebook environment running on Free Edition

## Duration of Completion
null minutes

## Level
Intermediate

## Industries


## Tags


## Scenarios
### AI-Augmented SQL 
#### Overview
In this scenario you will use the Databricks Foundation Model API to build three practical SQL tools: a zero-shot explainer that translates complex GlobalMart queries into plain English, a few-shot optimizer that learns your team's coding conventions from examples, and a natural-language-to-SQL translator. By the end you will have a reusable prompt toolkit that makes any SQL task faster — whether you are reviewing a colleague's query, writing one from scratch, or explaining it to a business stakeholder.

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
- databricks (tool)
- sql (tool)
- gen-ai (tool)
- python (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

### From Genie to Full Control
<br>

Yesterday you typed questions into Genie and it converted them to SQL automatically. You were using prompts without writing them — Genie wrote the prompt for you behind the scenes.

Today you take control of that prompt layer yourself.

![Image](https://cdn.enqurious.com/images/6719ae24-aa30-46f4-8204-64f2fa87a696_Screenshot-2026-07-23-at-11.webp)

<br>

**Three tools you will build in this scenario:**

| Tool | What it does | When you use it |
|------|-------------|-----------------|
| SQL Explainer | Translates complex SQL to plain English | Reviewing a colleague's query, explaining joins to a stakeholder |
| SQL Optimizer | Suggests performance improvements using team conventions | Before pushing a slow query to production |
| NL-to-SQL | Converts a business question to a runnable query | When the business team asks ad-hoc questions |
<br>

**The Foundation Model API pattern you will use throughout:**

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()

response = w.serving_endpoints.predict(
    endpoint="databricks-meta-llama-3-1-70b-instruct",
    inputs={
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": USER_MESSAGE}
        ],
        "temperature": 0.0,
        "max_tokens": 600
    }
)
answer = response["choices"][0]["message"]["content"]
print(answer)
```

> **Free Edition note:** `databricks-meta-llama-3-1-70b-instruct` is available at zero cost on Databricks Free Edition. No API keys, no billing — it runs on Databricks infrastructure.



**Tags**


##### Input 2
**Type:** Text

### Zero-Shot SQL Explainer — Concept
<br>

**Zero-shot** means you describe the task in the prompt without giving the LLM any examples. You rely entirely on the model's pre-trained knowledge.

For SQL explanation this works well because:
- Llama 70B was trained on millions of SQL snippets
- The task is deterministic — there is one correct explanation of what a query does
- You do not need to teach the model your data model, just give it the query

**The key design decision: the system prompt.**

A bad system prompt produces vague, generic output:
```
"You are a helpful assistant."
```

A good system prompt produces structured, actionable output:
```
"You are a senior SQL reviewer for GlobalMart, a retail analytics company.
When given a SQL query:
1. Explain in plain English what the query returns (1-2 sentences)
2. Identify the tables joined and why
3. Flag any performance concern (e.g., missing partition filter, cartesian join risk)
Keep your response under 150 words. No code in your response."
```

**Why system prompt framing matters more than anything else:**
- It sets the persona (SQL reviewer vs generic assistant)
- It defines the output structure (3-part answer vs free text)
- It constrains length (150 words vs unlimited rambling)
- It excludes noise (no code in response — you want explanation, not more SQL)



**Tags**


##### Input 3
**Type:** Code

**Question:** Task 1 — Build the SQL Explainer.
The `explain_sql()` function below has three blanks. Fill them in:

**Language:** python

**Snippet:** from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
ENDPOINT = "databricks-meta-llama-3-1-70b-instruct"

def explain_sql(query: str) -> str:
    """
    Explains a SQL query in plain English using the Foundation Model API.
    Returns a structured 3-part explanation.
    """
    SYSTEM_PROMPT = """________"""   # TODO: write the SQL reviewer system prompt

    USER_MESSAGE = f"""________"""   # TODO: pass the query to the model (hint: use an f-string)

    response = w.serving_endpoints.predict(
        endpoint=ENDPOINT,
        inputs={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": USER_MESSAGE}
            ],
            "temperature": 0.0,
            "max_tokens": 400
        }
    )
    return response["choices"][0]["message"]["________"]   # TODO: correct key


# Test query — GlobalMart customer revenue analysis
TEST_QUERY = """
WITH customer_revenue AS (
    SELECT
        c.customer_id,
        c.full_name,
        c.customer_tenure_days,
        CASE
            WHEN c.customer_tenure_days < 90  THEN 'New'
            WHEN c.customer_tenure_days < 365 THEN 'Regular'
            ELSE 'Loyal'
        END AS tenure_tier,
        SUM(f.revenue) AS total_revenue
    FROM gbmart.silver.customers c
    JOIN gbmart.gold.fact_sales f ON c.customer_sk = f.customer_sk
    GROUP BY c.customer_id, c.full_name, c.customer_tenure_days
)
SELECT customer_id, full_name, tenure_tier, total_revenue
FROM customer_revenue
ORDER BY total_revenue DESC
LIMIT 10
"""

explanation = explain_sql(TEST_QUERY)
print(explanation)

**Solution:** 
```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
ENDPOINT = "databricks-meta-llama-3-1-70b-instruct"

def explain_sql(query: str) -> str:
    SYSTEM_PROMPT = """You are a senior SQL reviewer for GlobalMart, a retail analytics company 
whose data lives in Unity Catalog (gbmart.bronze / gbmart.silver / gbmart.gold).

When given a SQL query:
1. Explain in plain English what the query returns (1-2 sentences)
2. Identify the main tables joined and the reason for each join
3. Flag any performance concern (e.g., missing partition filter, no index hint, large cartesian join risk)

Keep your response under 150 words. Do not include any SQL code in your response."""

    USER_MESSAGE = f"""Explain the following GlobalMart SQL query:

{query}"""

    response = w.serving_endpoints.predict(
        endpoint=ENDPOINT,
        inputs={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": USER_MESSAGE}
            ],
            "temperature": 0.0,
            "max_tokens": 400
        }
    )
    return response["choices"][0]["message"]["content"]

TEST_QUERY = """
WITH customer_revenue AS (
    SELECT
        c.customer_id,
        c.full_name,
        c.customer_tenure_days,
        CASE
            WHEN c.customer_tenure_days < 90  THEN 'New'
            WHEN c.customer_tenure_days < 365 THEN 'Regular'
            ELSE 'Loyal'
        END AS tenure_tier,
        SUM(f.revenue) AS total_revenue
    FROM gbmart.silver.customers c
    JOIN gbmart.gold.fact_sales f ON c.customer_sk = f.customer_sk
    GROUP BY c.customer_id, c.full_name, c.customer_tenure_days
)
SELECT customer_id, full_name, tenure_tier, total_revenue
FROM customer_revenue
ORDER BY total_revenue DESC
LIMIT 10
"""

print(explain_sql(TEST_QUERY))
# Expected output (approximate):
# 1. This query finds the top 10 GlobalMart customers by total revenue,
#    classifying each by tenure (New/Regular/Loyal) based on how long they have been registered.
# 2. Tables: silver.customers (customer profile + tenure), gold.fact_sales (revenue per transaction),
#    joined on customer_sk (the SCD2 surrogate key set in Silver).
# 3. Performance note: No partition filter on fact_sales — on large datasets, adding a date range
#    filter on sale_date before the GROUP BY will significantly reduce shuffle.
```

**Tags**
- generative-ai / agentic-ai / prompt-engineering (skill)

##### Input 4
**Type:** Text

### Few-Shot SQL Optimizer — Teach the LLM Your Team's Conventions
<br>

Zero-shot relies on the model's general knowledge. **Few-shot** gives the model 2–3 examples of input → output, so it learns the specific style and conventions you want.

**When few-shot beats zero-shot for SQL:**
- You have team-specific conventions the model doesn't know (e.g., "always use CTEs, never subqueries")
- You want consistent output format (e.g., "always add a comment explaining the change")
- The optimization rule is GlobalMart-specific (e.g., "always partition filter on `_ingested_at`")

**Few-shot structure for SQL optimization:**

```
SYSTEM: You are GlobalMart's SQL optimizer. Follow the conventions shown in the examples.

USER:
Example 1:
BEFORE: SELECT * FROM gbmart.silver.customers WHERE email LIKE '%gmail%'
AFTER:  SELECT customer_id, email FROM gbmart.silver.customers WHERE email LIKE '%gmail%'
-- Change: Removed SELECT *, selected only needed columns to reduce shuffle.

Example 2:
BEFORE: SELECT o.order_id, c.full_name FROM gbmart.silver.orders o,
        gbmart.silver.customers c WHERE o.customer_id = c.customer_id
AFTER:  SELECT o.order_id, c.full_name FROM gbmart.silver.orders o
        JOIN gbmart.silver.customers c ON o.customer_id = c.customer_id
-- Change: Replaced implicit comma join with explicit JOIN for clarity and optimizer hint.

Now optimize this query:
BEFORE: [learner's query]
```

The LLM sees the pattern — avoid SELECT *, use explicit JOINs, explain the change — and applies it to the new query.



**Tags**


##### Input 5
**Type:** Code

**Question:** Task 2 — Build the Few-Shot SQL Optimizer.
The `optimize_sql()` function has two blanks. Fill in:

**Language:** python

**Snippet:** def optimize_sql(query: str) -> str:
    """
    Suggests a performance-optimized version of a GlobalMart SQL query.
    Uses few-shot examples to teach GlobalMart-specific conventions.
    """
    FEW_SHOT_EXAMPLES = """________"""   # TODO: paste the two few-shot examples from Input 4

    SYSTEM_PROMPT = """You are GlobalMart's SQL optimizer. Apply the same conventions shown 
in the examples below. Always output:
BEFORE: [original query]
AFTER:  [optimized query]
-- Change: [one sentence explaining the specific change and why]"""

    USER_MESSAGE = f"""{FEW_SHOT_EXAMPLES}

Now optimize this query:
________"""   # TODO: append the query variable

    response = w.serving_endpoints.predict(
        endpoint=ENDPOINT,
        inputs={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": USER_MESSAGE}
            ],
            "temperature": 0.0,
            "max_tokens": 500
        }
    )
    return response["choices"][0]["message"]["content"]


SLOW_QUERY = """
SELECT * FROM gbmart.silver.customers c,
              gbmart.silver.orders o
WHERE c.customer_id = o.customer_id
AND   c.customer_tenure_days > 365
"""

print(optimize_sql(SLOW_QUERY))

**Solution:** 
```python
def optimize_sql(query: str) -> str:
    FEW_SHOT_EXAMPLES = """Example 1:
BEFORE: SELECT * FROM gbmart.silver.customers WHERE email LIKE '%gmail%'
AFTER:  SELECT customer_id, email FROM gbmart.silver.customers WHERE email LIKE '%gmail%'
-- Change: Removed SELECT *, selected only needed columns to reduce shuffle.

Example 2:
BEFORE: SELECT o.order_id, c.full_name FROM gbmart.silver.orders o,
        gbmart.silver.customers c WHERE o.customer_id = c.customer_id
AFTER:  SELECT o.order_id, c.full_name FROM gbmart.silver.orders o
        JOIN gbmart.silver.customers c ON o.customer_id = c.customer_id
-- Change: Replaced implicit comma join with explicit JOIN for clarity and query optimizer hint."""

    SYSTEM_PROMPT = """You are GlobalMart's SQL optimizer. Apply the same conventions shown 
in the examples below. Always output:
BEFORE: [original query]
AFTER:  [optimized query]
-- Change: [one sentence explaining the specific change and why]"""

    USER_MESSAGE = f"""{FEW_SHOT_EXAMPLES}

Now optimize this query:
BEFORE: {query}"""

    response = w.serving_endpoints.predict(
        endpoint=ENDPOINT,
        inputs={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": USER_MESSAGE}
            ],
            "temperature": 0.0,
            "max_tokens": 500
        }
    )
    return response["choices"][0]["message"]["content"]

# Expected output (approximate):
# BEFORE: SELECT * FROM gbmart.silver.customers c, gbmart.silver.orders o
#         WHERE c.customer_id = o.customer_id AND c.customer_tenure_days > 365
# AFTER:  SELECT c.customer_id, c.full_name, c.customer_tenure_days,
#                o.order_id, o.total_amount
#         FROM gbmart.silver.customers c
#         JOIN gbmart.silver.orders o ON c.customer_id = o.customer_id
#         WHERE c.customer_tenure_days > 365
# -- Change: Removed SELECT *, replaced implicit comma join with explicit JOIN,
#    selected only business-relevant columns.
```

**Tags**
- llm-integration / few-shot-learning (skill)

##### Input 6
**Type:** Choice

**Question:** You are building a SQL optimization tool for the GlobalMart team. The LLM should always produce the same optimized version for the same input query — no randomness, no variation. Which temperature setting should you use?

**Options:** 
- `temperature: 1.0` — maximum creativity for novel optimization ideas

- `temperature: 0.7` — balanced between creativity and consistency

- `temperature: 0.0` — fully deterministic, same output every run

- `temperature: 0.3` — slight variation to catch different edge cases

**Correct Options:** 
- `temperature: 0.0` — fully deterministic, same output every run

**Solution:** 
`temperature: 0.0` is correct for all deterministic tasks — SQL explanation, optimization, and code review. There is one correct answer for "what does this query do" and you want the LLM to give it consistently every time. Use higher temperature only when you want creative variation: brainstorming column names, generating synthetic test data, or exploring multiple refactoring approaches.

**Tags**
- llm-integration / temperature (skill)

##### Input 7
**Type:** Code

**Question:** Task 3 — NL-to-SQL Translator.
Build a function that takes a plain English business question and returns a runnable GlobalMart SQL query. The schema context is provided for you. Fill in the system prompt that grounds the LLM in the GlobalMart schema and instructs it to return only a SQL query (no markdown, no explanation).

**Language:** python

**Snippet:** GLOBALMART_SCHEMA = """
GlobalMart Unity Catalog — available tables:

gbmart.silver.customers   — customer_id, full_name, email, customer_tenure_days, age, registration_date, is_current
gbmart.silver.orders      — order_id, customer_id, order_date, total_amount, status
gbmart.silver.order_items — order_item_id, order_id, product_id, quantity, unit_price
gbmart.silver.products    — product_id, product_name, category, unit_cost
gbmart.silver.returns     — return_id, order_id, customer_id, return_date, reason
gbmart.gold.fact_sales    — order_sk, customer_sk, product_sk, sale_date, revenue, quantity_sold
gbmart.gold.dim_customers — customer_sk, customer_id, full_name, tenure_tier (New/Regular/Loyal)
"""

def nl_to_sql(business_question: str) -> str:
    """
    Converts a plain English business question to a runnable GlobalMart SQL query.
    Returns only the SQL — no markdown, no explanation.
    """
    SYSTEM_PROMPT = """________"""   # TODO: ground the LLM in the GlobalMart schema and return SQL only

    response = w.serving_endpoints.predict(
        endpoint=ENDPOINT,
        inputs={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": business_question}
            ],
            "temperature": 0.0,
            "max_tokens": 400
        }
    )
    return response["choices"][0]["message"]["content"]


# Test: business question → SQL
questions = [
    "Which product category had the highest return rate last month?",
    "List all loyal customers who have not placed an order in the last 90 days.",
    "What is the average order value by tenure tier?"
]

for q in questions:
    print(f"Q: {q}")
    print(f"SQL:\n{nl_to_sql(q)}\n{'─'*60}\n")

**Solution:** 
```python
GLOBALMART_SCHEMA = """
GlobalMart Unity Catalog — available tables:

gbmart.silver.customers   — customer_id, full_name, email, customer_tenure_days, age, registration_date, is_current
gbmart.silver.orders      — order_id, customer_id, order_date, total_amount, status
gbmart.silver.order_items — order_item_id, order_id, product_id, quantity, unit_price
gbmart.silver.products    — product_id, product_name, category, unit_cost
gbmart.silver.returns     — return_id, order_id, customer_id, return_date, reason
gbmart.gold.fact_sales    — order_sk, customer_sk, product_sk, sale_date, revenue, quantity_sold
gbmart.gold.dim_customers — customer_sk, customer_id, full_name, tenure_tier (New/Regular/Loyal)
"""

def nl_to_sql(business_question: str) -> str:
    SYSTEM_PROMPT = f"""You are a SQL generator for GlobalMart, a retail analytics company.
Use ONLY the tables and columns from the schema below. Do not invent tables or columns.

SCHEMA:
{GLOBALMART_SCHEMA}

Rules:
- Return ONLY the SQL query, no markdown, no explanation, no backticks
- Use fully qualified table names (gbmart.silver.xxx or gbmart.gold.xxx)
- Prefer gbmart.gold tables when available (they are pre-aggregated)
- Add a comment on the first line: -- Question: [the original question]"""

    response = w.serving_endpoints.predict(
        endpoint=ENDPOINT,
        inputs={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": business_question}
            ],
            "temperature": 0.0,
            "max_tokens": 400
        }
    )
    return response["choices"][0]["message"]["content"]
```

**Tags**
- databricks / databricks-genie (tool)

##### Input 8
**Type:** Short Answer

**Question:** You have built three SQL tools: zero-shot explainer, few-shot optimizer, and NL-to-SQL translator. A junior data engineer on your team asks: "Should I always use few-shot? More examples must mean better output, right?"

**Template:** null

**Solution:** 
Zero-shot is the better choice when the task is well-defined and the model already has strong relevant knowledge — SQL explanation is a good example because Llama 70B has seen millions of SQL queries and can explain them accurately without examples. Adding few-shot examples when they are not needed increases prompt size (and therefore latency and token cost), introduces a new risk of example quality issues (a bad example teaches the wrong pattern), and can actually constrain the model unnecessarily — if your example only shows one optimization pattern, the model may apply it even when a different optimization would be better. Use few-shot when you have GlobalMart-specific conventions or output formats the model cannot infer from the task description alone; use zero-shot when the task is universal and the model's pre-training knowledge is sufficient.

**Tags**
- llm-integration / few-shot-learning (skill)

### AI-Augmented Data Engineering 
#### Overview
In this scenario you will use LLMs for three tasks that data engineers spend hours on manually: explaining a DQ failure scan output to the business team, generating a complete data dictionary from a table schema, and translating a technical pipeline change into a plain-English stakeholder summary. All three examples use real GlobalMart artifacts from the Silver layer you built

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
- gen-ai (tool)
- python (tool)
- sql (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

### The Three DE Communication Problems LLMs Solve
<br>

Data engineers spend significant time translating technical output into language the business can act on. Three specific pain points:

**Problem 1 — DQ failure reports that only engineers understand**

Your Silver layer DQ scan produces this:
```
_dq_issue                COUNT
NULL_EMAIL               12
INVALID_EMAIL_FORMAT     3
REGISTERED_UNDER_18      77
```

The business team receives this table and asks: "What does INVALID_EMAIL_FORMAT mean? What are you doing about the 77 rows?" You spend 30 minutes writing an explanation email.

**Problem 2 — Data dictionaries written at the last minute**

Every Gold table you produce needs a data dictionary for the BI team, governance, and compliance. Writing descriptions for 20+ columns from scratch takes 2 hours per table.

**Problem 3 — Technical pipeline changes explained to stakeholders**

"We moved 77 customer records to quarantine" needs to be explained to the Customer Success team, the Data Governance team, and the Product team — all in different levels of technical detail.

**Today you build a prompt for each of these.** None of them require any new code patterns — just precise system prompts applied to real GlobalMart artifacts.



**Tags**


##### Input 2
**Type:** Code

**Question:** Task 1 — DQ Failure Explainer.
Build a `explain_dq_results()` function that takes a DQ scan summary (as a dict of error code → count) and returns a plain-English explanation for the business team. The system prompt must:

**Language:** python

**Snippet:** from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
ENDPOINT = "databricks-meta-llama-3-1-70b-instruct"

def explain_dq_results(dq_summary: dict, table_name: str) -> str:
    """
    Converts DQ scan output into a plain-English business report.

    Args:
        dq_summary: dict mapping DQ issue code to count of affected records
        table_name: name of the table that was scanned
    """
    issues_text = "\n".join([f"- {code}: {count} records" for code, count in dq_summary.items()])

    SYSTEM_PROMPT = """________"""   # TODO: DQ explainer system prompt

    USER_MESSAGE = f"""The following data quality issues were found during the latest scan of {table_name}:

{issues_text}

Please write the business explanation and recommended actions."""

    response = w.serving_endpoints.predict(
        endpoint=ENDPOINT,
        inputs={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": USER_MESSAGE}
            ],
            "temperature": 0.0,
            "max_tokens": 600
        }
    )
    return response["choices"][0]["message"]["content"]


# Real DQ scan output from GlobalMart Silver customers
DQ_RESULTS = {
    "INVALID_EMAIL_FORMAT": 3,
    "REGISTERED_UNDER_18": 77,
    "NULL_FIRST_NAME": 4
}

report = explain_dq_results(DQ_RESULTS, "gbmart.silver.customers")
print(report)

**Solution:** 
```python
def explain_dq_results(dq_summary: dict, table_name: str) -> str:
    issues_text = "\n".join([f"- {code}: {count} records" for code, count in dq_summary.items()])

    SYSTEM_PROMPT = """You are a GlobalMart Data Quality Analyst writing a report for the Business Operations team.
When given a list of data quality issues and their record counts:
1. Translate each issue code into plain English (e.g., REGISTERED_UNDER_18 = "Customer registered before reaching the minimum age of 18")
2. State the count and business impact (e.g., "77 customer accounts may not meet our legal Terms of Service requirements")
3. For each issue, state the recommended action: Fix (data can be corrected automatically), Quarantine (record held pending review), or Investigate (business team input needed)
4. End with a one-paragraph overall summary

Write in a professional tone. No technical jargon, no code. The audience is business stakeholders, not engineers."""

    response = w.serving_endpoints.predict(
        endpoint=ENDPOINT,
        inputs={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"The following data quality issues were found during the latest scan of {table_name}:\n\n{issues_text}\n\nPlease write the business explanation and recommended actions."}
            ],
            "temperature": 0.0,
            "max_tokens": 600
        }
    )
    return response["choices"][0]["message"]["content"]

# Expected output (approximate):
# ## Data Quality Report — gbmart.silver.customers
#
# **Issue 1: Invalid Email Address Format (3 records)**
# Three customer accounts have email addresses that do not meet our standard format requirements...
# Recommended Action: FIX — These emails can be corrected automatically...
#
# **Issue 2: Customer Registered Under Age 18 (77 records)**
# 77 customer accounts show a registration date before the customer turned 18...
# Recommended Action: QUARANTINE — These records have been placed in a review queue...
#
# **Issue 3: Missing First Name (4 records)**
# Four customer records are missing the first name field...
# Recommended Action: INVESTIGATE — Please review with the source system team...
#
# **Summary:** ... [professional summary]
```

**Tags**
- generative-ai / agentic-ai / prompt-engineering (skill)
- llm-integration / system-prompt (skill)

##### Input 3
**Type:** Text

### Data Dictionary Generation — Structured Output Prompting
<br>

A data dictionary maps each column to: description, data type, possible values, and business meaning. Writing this manually for a 15-column Silver table takes 60–90 minutes.

**The key prompt technique: structured output via JSON schema in the prompt.**

Instead of asking the LLM to write free text, you tell it the exact JSON structure you want:

```python
SYSTEM_PROMPT = """You are a data documentation specialist.
When given a table schema, generate a data dictionary in this exact JSON format:
{
  "table": "fully_qualified_table_name",
  "description": "one sentence describing what this table contains",
  "columns": [
    {
      "name": "column_name",
      "type": "data_type",
      "description": "plain English description",
      "example_values": ["value1", "value2"],
      "business_rule": "any constraint or business rule that applies"
    }
  ]
}
Return only the JSON. No markdown fences, no explanation."""
```

This produces output you can parse programmatically — save it to a file, render it as a table in Confluence, or load it into a data catalog.



**Tags**


##### Input 4
**Type:** Code

**Question:** Task 2 — Data Dictionary Generator.
Build a `generate_data_dictionary()` function that takes a table name and its schema (as a list of column definitions), and returns a structured JSON data dictionary. Fill in the system prompt using the JSON format from Input 3.

**Language:** python

**Snippet:** import json

def generate_data_dictionary(table_name: str, schema_text: str) -> dict:
    """
    Generates a structured data dictionary for a GlobalMart table.
    Returns a parsed dict with table description and column-level documentation.
    """
    SYSTEM_PROMPT = """________"""   # TODO: structured JSON output system prompt

    USER_MESSAGE = f"""Generate a data dictionary for the following table:

Table: {table_name}

Schema:
{schema_text}"""

    response = w.serving_endpoints.predict(
        endpoint=ENDPOINT,
        inputs={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": USER_MESSAGE}
            ],
            "temperature": 0.0,
            "max_tokens": 1000
        }
    )
    raw_output = response["choices"][0]["message"]["content"]

    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        print("Warning: LLM did not return valid JSON. Raw output:")
        print(raw_output)
        return {}


# GlobalMart silver.customers schema
CUSTOMERS_SCHEMA = """
customer_sk              STRING    -- SCD2 surrogate key (SHA256 hash)
customer_id              STRING    -- Natural key from source system (CUST-XXXXX format)
first_name               STRING    -- Customer first name
last_name                STRING    -- Customer last name
full_name                STRING    -- Derived: first_name + last_name
email                    STRING    -- Email address (cleaned, lowercase)
phone_number             STRING    -- Formatted as +91-XXXXXXXXXX
date_of_birth            DATE      -- Customer date of birth
age                      INT       -- Derived: age in years as of today
registration_date        DATE      -- Date customer registered on GlobalMart
customer_tenure_days     INT       -- Derived: days since registration
is_current               BOOLEAN   -- SCD2 flag: true = active record
effective_start_date     DATE      -- SCD2: when this version became active
effective_end_date       DATE      -- SCD2: when this version was superseded (null if active)
"""

data_dict = generate_data_dictionary("gbmart.silver.customers", CUSTOMERS_SCHEMA)

# Pretty print
if data_dict:
    print(f"Table: {data_dict.get('table')}")
    print(f"Description: {data_dict.get('description')}\n")
    for col in data_dict.get("columns", []):
        print(f"  {col['name']} ({col['type']}): {col['description']}")
        if col.get("business_rule"):
            print(f"    Rule: {col['business_rule']}")

**Solution:** 
```python
def generate_data_dictionary(table_name: str, schema_text: str) -> dict:
    SYSTEM_PROMPT = """You are a data documentation specialist for GlobalMart, a retail analytics company.
When given a table schema:
Generate a data dictionary in this exact JSON format (no markdown fences, no explanation):
{
  "table": "fully_qualified_table_name",
  "description": "one sentence describing what this table contains and its role in the data model",
  "columns": [
    {
      "name": "column_name",
      "type": "data_type",
      "description": "plain English description of what this column contains",
      "example_values": ["realistic_example_1", "realistic_example_2"],
      "business_rule": "constraint, derivation formula, or business rule — empty string if none"
    }
  ]
}

For derived columns (age, full_name, customer_tenure_days), the business_rule field must state the derivation formula.
For SCD2 columns, the description must explain the SCD2 purpose.
Return only valid JSON."""

    response = w.serving_endpoints.predict(
        endpoint=ENDPOINT,
        inputs={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Generate a data dictionary for:\nTable: {table_name}\nSchema:\n{schema_text}"}
            ],
            "temperature": 0.0,
            "max_tokens": 1000
        }
    )
    raw = response["choices"][0]["message"]["content"]
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("Warning: LLM did not return valid JSON. Raw output:")
        print(raw)
        return {}
```

**Tags**
- generative-ai / agentic-ai / prompt-engineering (skill)
- llm-integration / system-prompt (skill)

##### Input 5
**Type:** Choice

**Question:** Your `generate_data_dictionary()` function returns an empty dict `{}` and prints "Warning: LLM did not return valid JSON." What is the most likely cause, and what is the first thing to check?

**Options:** 
- The LLM model is down — check Databricks workspace status

- The LLM wrapped its JSON output in markdown fences (```json ... ```) — add a strip step or tighten the system prompt

- The `json.loads()` function has a bug — replace with `eval()`

- The schema was too long — reduce column count to 5

**Correct Options:** 
- The LLM wrapped its JSON output in markdown fences (```json ... ```) — add a strip step or tighten the system prompt

**Solution:** 
This is the most common failure mode when asking LLMs for JSON output. Despite the system prompt saying "no markdown fences," some models (especially smaller ones) still wrap the output in `\`\`\`json ... \`\`\``. Fix by either: (a) adding a post-processing step `raw = raw.strip().removeprefix("```json").removesuffix("```").strip()`, or (b) adding a stronger constraint to the system prompt: "Your response must start with `{` and end with `}`. Do not include any text before or after the JSON."

**Tags**
- generative-ai / agentic-ai / context-management (skill)
- llm-integration / hallucination (skill)
- llm-integration / system-prompt (skill)

##### Input 6
**Type:** Code

**Question:** Task 3 — Stakeholder Summary Generator.
Build a `generate_stakeholder_summary()` function that takes a pipeline change description and a target audience, and generates an appropriate communication. Test it on the GlobalMart quarantine decision with three audiences: Business Operations, Legal/Compliance, and Product team. Fill in the system prompt that adapts tone and depth to the audience.

**Language:** python

**Snippet:** def generate_stakeholder_summary(
    technical_change: str,
    audience: str,
    context: str = ""
) -> str:
    """
    Generates a stakeholder-appropriate communication for a pipeline change.

    Args:
        technical_change: What happened in the pipeline (technical description)
        audience: Target audience (Business Operations / Legal-Compliance / Product)
        context: Optional additional context (table name, impact size, etc.)
    """
    SYSTEM_PROMPT = """________"""   # TODO: audience-adaptive communication system prompt

    USER_MESSAGE = f"""Technical change: {technical_change}
Target audience: {audience}
{f"Additional context: {context}" if context else ""}

Write the stakeholder communication."""

    response = w.serving_endpoints.predict(
        endpoint=ENDPOINT,
        inputs={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": USER_MESSAGE}
            ],
            "temperature": 0.1,
            "max_tokens": 400
        }
    )
    return response["choices"][0]["message"]["content"]


CHANGE = """During today's Silver layer processing, 77 customer records were moved to 
gbmart.silver.customers_quarantine with DQ issue code REGISTERED_UNDER_18. 
These customers have a RegistrationDate that is less than 18 years after their DateOfBirth.
They are excluded from gbmart.silver.customers (the clean table) and will not appear 
in any Gold layer reports until the business team resolves their status."""

CONTEXT = "GlobalMart customers table, 77 records out of ~20,000 total (0.4%)"

audiences = ["Business Operations", "Legal-Compliance", "Product Team"]

for audience in audiences:
    print(f"\n{'='*60}")
    print(f"AUDIENCE: {audience}")
    print('='*60)
    print(generate_stakeholder_summary(CHANGE, audience, CONTEXT))

**Solution:** 
```python
def generate_stakeholder_summary(technical_change: str, audience: str, context: str = "") -> str:
    SYSTEM_PROMPT = """You are a data engineering lead at GlobalMart communicating pipeline changes to stakeholders.
Adapt your communication to the target audience:

Business Operations: Focus on business impact — which reports are affected, what actions are needed, when normal data will resume.

Legal-Compliance: Focus on regulatory implications — which data protection or age-verification rules are relevant, what the quarantine process ensures, and what documentation exists.

Product Team: Focus on user experience impact — which features or customer-facing data may be affected, whether the impacted customers will see anything different, and what the engineering team is doing.

Rules for all audiences:
- Write in 3-4 sentences maximum
- No technical jargon (no "DQ scan", no "Delta table", no "Unity Catalog")
- Be factual and calm — do not alarm unnecessarily
- State the next step clearly"""

    USER_MESSAGE = f"""Technical change: {technical_change}
Target audience: {audience}
{f"Additional context: {context}" if context else ""}

Write the stakeholder communication."""

    response = w.serving_endpoints.predict(
        endpoint=ENDPOINT,
        inputs={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": USER_MESSAGE}
            ],
            "temperature": 0.1,
            "max_tokens": 400
        }
    )
    return response["choices"][0]["message"]["content"]

# Expected outputs vary by audience:
# Business Operations: "During today's data refresh, 77 customer accounts (0.4% of total) were
#   flagged for age verification review and are currently excluded from reports..."
# Legal-Compliance: "In compliance with our Terms of Service age requirement, 77 customer
#   records have been placed in a controlled review queue pending verification..."
# Product Team: "A small set of 77 customer accounts (less than 1% of users) are temporarily
#   excluded from personalization features while their account details are verified..."
```

**Tags**
- generative-ai / agentic-ai / prompt-engineering (skill)
- llm-integration / system-prompt (skill)

##### Input 7
**Type:** Short Answer

**Question:** You have built a DQ explainer, a data dictionary generator, and a stakeholder summary tool. A colleague argues: "This is just glorified mail-merge — you're templating. What makes this better than writing a Python f-string that fills in the error counts?"

**Template:** null

**Solution:** 
A Python f-string can fill in `{count}` for error counts, but it cannot translate `REGISTERED_UNDER_18` into "Customer registered before reaching the minimum age of 18" — that translation requires understanding what the term means and knowing what action the business should take, which comes from the LLM's pre-trained knowledge of data governance patterns. More importantly, the LLM adapts its explanation to context: it knows that REGISTERED_UNDER_18 is a Quarantine case (not a Fix case) without being told, because it has seen compliance literature about age-gated services during training. The stakeholder summary tool goes further — it rewrites the same technical change in three entirely different registers (operational, legal, product) from a single input, which would require three separate f-string templates and manual writing of all content. The LLM's value here is semantic understanding and register adaptation, not text substitution.

**Tags**
- generative-ai / agentic-ai / context-management (skill)

### AI-Augmented Python
#### Overview
In this scenario you will use the Foundation Model API to enhance real GlobalMart data engineering Python code. You will build three tools: a docstring generator that takes a raw PySpark function and produces professional documentation, a defensive-code enhancer that adds try/except blocks and input validation, and a refactoring assistant that suggests cleaner implementations. All examples come from the actual GlobalMart Silver layer notebooks you built in Weeks 2–5.

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
- gen-ai (tool)
- python (tool)
- sql (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

### Why Enhance Code You Already Wrote?
<br>

You have already written working DE code — the Silver layer notebooks, the DQ checks, the SCD2 logic. The code runs. But it has gaps that slow down the team:

| Gap | Problem |
|-----|---------|
| No docstrings | A new team member reads `remediate_emails(df)` and has no idea what it expects or returns |
| No error handling | `dq_scan_df` crashes silently when a Bronze table is empty — no useful error message |
| Verbose logic | A 20-line `withColumn` chain could be replaced by a helper function |
<br>

**LLMs are excellent at code enhancement because:**
- They have seen millions of docstrings, error handlers, and refactoring patterns
- The task is additive — you show them working code and ask them to add structure
- They can explain WHY they made each change (chain-of-thought prompting)

**The pattern today:**

```
You (engineer) ──► working GlobalMart function
     ──► LLM ──► same function with: docstring + error handling + explanation
     ──► You ──► review, accept/reject changes, paste into notebook
```

> **Key point:** You are not asking the LLM to write your code. You are asking it to make your existing code production-grade. The logic stays yours; the documentation and defensive wrappers get added by the LLM.



**Tags**


##### Input 2
**Type:** Text

### Docstring Generation — Concept
<br>

Python docstrings in DE code serve three people:
1. **Future you** — reading this notebook in 3 months
2. **Your team** — the senior DE reviewing your PR
3. **The platform** — tools like `help()`, IDEs, and automated doc generators

A good docstring for a PySpark function includes:
- What the function does (1 sentence)
- Args: name, type, description for each parameter
- Returns: type and description
- Raises: any exceptions intentionally raised
- Example: one call showing the expected usage

**The prompt pattern for docstring generation:**

```python
SYSTEM_PROMPT = """You are a Python documentation expert specializing in PySpark and Delta Lake.
When given a Python function:
1. Add a Google-style docstring
2. Include: description, Args, Returns, Raises (if applicable), Example
3. Do not change the function logic — only add the docstring
4. Return the complete function with docstring included"""
```

The key constraint: **do not change the function logic.** Without it, the LLM will sometimes "improve" your code while adding the docstring — changing behavior you did not ask it to change.



**Tags**


##### Input 3
**Type:** Code

**Question:** Task 1 — Generate a Docstring. 
The `add_docstring()` function has two blanks. Fill in:

**Language:** python

**Snippet:** from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
ENDPOINT = "databricks-meta-llama-3-1-70b-instruct"

def add_docstring(function_code: str) -> str:
    """Adds a Google-style docstring to a Python function without changing its logic."""

    SYSTEM_PROMPT = """________"""   # TODO: docstring generator system prompt

    response = w.serving_endpoints.predict(
        endpoint=ENDPOINT,
        inputs={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"________"}   # TODO: pass the function code
            ],
            "temperature": 0.0,
            "max_tokens": 700
        }
    )
    return response["choices"][0]["message"]["content"]


# GlobalMart DQ scan function from Silver layer — no docstring yet
GLOBALMART_FUNCTION = '''
def run_dq_scan(df, email_regex=r"^[a-zA-Z0-9._%+\\-]+@[a-zA-Z0-9.\\-]+\\.[a-zA-Z]{2,}$"):
    from pyspark.sql.functions import col, when, lit, to_date, floor, datediff, trim
    dob_temp   = to_date(col("DateOfBirth"),      "yyyy-MM-dd")
    reg_temp   = to_date(col("RegistrationDate"), "yyyy-MM-dd")
    age_at_reg = floor(datediff(reg_temp, dob_temp) / 365.25)
    return df \\
        .withColumn("_dob_temp",    dob_temp) \\
        .withColumn("_reg_temp",    reg_temp) \\
        .withColumn("_age_at_reg",  age_at_reg) \\
        .withColumn("_dq_issue",
            when(col("CustomerID").isNull(),               lit("NULL_CUSTOMER_ID"))
            .when(col("FirstName").isNull() | (trim(col("FirstName")) == ""), lit("NULL_FIRST_NAME"))
            .when(col("Email").isNull(),                   lit("NULL_EMAIL"))
            .when(~col("Email").rlike(email_regex),        lit("INVALID_EMAIL_FORMAT"))
            .when(col("DateOfBirth").isNull(),             lit("NULL_DATE_OF_BIRTH"))
            .when(col("_age_at_reg") < 18,                 lit("REGISTERED_UNDER_18"))
            .otherwise(lit(None))
        )
'''

result = add_docstring(GLOBALMART_FUNCTION)
print(result)

**Solution:** 
```python
def add_docstring(function_code: str) -> str:
    SYSTEM_PROMPT = """You are a Python documentation expert specializing in PySpark and Delta Lake.
When given a Python function:
1. Add a Google-style docstring directly after the def line
2. Include these sections: description (1 sentence), Args (name, type, description), Returns (type + description), Raises (if applicable), Example (one realistic call)
3. Do not change the function logic in any way — only add the docstring
4. Return the complete function with docstring included, no markdown fences"""

    response = w.serving_endpoints.predict(
        endpoint=ENDPOINT,
        inputs={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Add a docstring to this function:\n\n{function_code}"}
            ],
            "temperature": 0.0,
            "max_tokens": 700
        }
    )
    return response["choices"][0]["message"]["content"]

# Expected output includes:
# def run_dq_scan(df, email_regex=...):
#     """Scans a customer Bronze DataFrame for data quality issues and tags each row with its first failing rule.
#
#     Args:
#         df (pyspark.sql.DataFrame): Raw customer DataFrame from gbmart.bronze.customers.
#         email_regex (str): Regex pattern for valid email format.
#                           Defaults to standard RFC-5322-compatible pattern.
#
#     Returns:
#         pyspark.sql.DataFrame: Original DataFrame with three added columns:
#             - _dob_temp (DateType): Parsed DateOfBirth
#             - _reg_temp (DateType): Parsed RegistrationDate
#             - _age_at_reg (float): Customer age in years at registration
#             - _dq_issue (str): First failing DQ rule code, or None if clean
#
#     Example:
#         scanned_df = run_dq_scan(bronze_df)
#         scanned_df.filter(col("_dq_issue").isNotNull()).groupBy("_dq_issue").count().show()
#     """
#     ... [original logic unchanged]
```

**Tags**
- generative-ai / agentic-ai / prompt-engineering (skill)
- llm-integration / system-prompt (skill)

##### Input 4
**Type:** Text

### Defensive Code Enhancement — Chain-of-Thought Prompting
<br>

Without error handling, a DE pipeline fails in the least helpful way:

```
AnalysisException: Table or view not found: gbmart.bronze.customers
```

That error message is from Spark — not from your code. The data engineer on call at 2am has no idea:
- Which step failed?
- Was the table dropped or never created?
- Should they rerun the full pipeline or just this step?

**Chain-of-thought (CoT) prompting** asks the LLM to reason step by step before producing its answer. For code enhancement this is useful because:
- It forces the LLM to identify failure modes before writing handlers
- The reasoning appears in the output, so you can verify the LLM understood your code correctly
- It produces more thorough error handling (catches edge cases, not just the obvious `try/except`)

**The CoT prompt pattern:**

```python
SYSTEM_PROMPT = """You are a senior data engineer performing a code safety review.
When given a Python/PySpark function:
Step 1: List the 3 most likely failure modes (empty table, schema mismatch, null column, etc.)
Step 2: For each failure mode, write the specific exception it raises in Spark/Python
Step 3: Add defensive code to catch and re-raise each with a clear, actionable error message
Step 4: Return the hardened function — the original logic must remain unchanged

Format your response as:
## Failure Modes
[your analysis]

## Hardened Function
[complete Python code]"""
```


**Tags**


##### Input 5
**Type:** Code

**Question:** Task 2 — Add Defensive Error Handling.
The `add_error_handling()` function has one blank: the chain-of-thought system prompt. Fill it in following the pattern from Input 4.

**Language:** python

**Snippet:** def add_error_handling(function_code: str) -> str:
    """Adds defensive error handling to a PySpark function using chain-of-thought prompting."""

    SYSTEM_PROMPT = """________"""   # TODO: the CoT system prompt from Input 4

    response = w.serving_endpoints.predict(
        endpoint=ENDPOINT,
        inputs={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Add defensive error handling to this function:\n\n{function_code}"}
            ],
            "temperature": 0.0,
            "max_tokens": 900
        }
    )
    return response["choices"][0]["message"]["content"]


WRITE_FUNCTION = '''
def write_to_silver(clean_df, quarantine_df, silver_table, quarantine_table):
    clean_df.write.format("delta").mode("append").saveAsTable(silver_table)
    quarantine_df.write.format("delta").mode("append").option("overwriteSchema", "true").saveAsTable(quarantine_table)
    print(f"Written to {silver_table}: {spark.table(silver_table).count()} rows")
    print(f"Quarantine: {spark.table(quarantine_table).count()} rows")
'''

result = add_error_handling(WRITE_FUNCTION)
print(result)

**Solution:** 
```python
def add_error_handling(function_code: str) -> str:
    SYSTEM_PROMPT = """You are a senior data engineer performing a code safety review.
When given a Python/PySpark function:

Step 1: List the 3 most likely failure modes (empty DataFrame, table not found, schema mismatch, permission error, etc.)
Step 2: For each failure mode, identify the specific Python/Spark exception it raises
Step 3: Add try/except blocks that catch each failure and re-raise with a clear message:
  - State WHICH table or step failed
  - State WHAT the likely cause is
  - State WHAT the engineer on call should do next
Step 4: Return the complete hardened function — original logic unchanged

Format:
## Failure Modes
[your analysis]

## Hardened Function
[complete Python code, no markdown fences]"""

    response = w.serving_endpoints.predict(
        endpoint=ENDPOINT,
        inputs={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Add defensive error handling to this function:\n\n{function_code}"}
            ],
            "temperature": 0.0,
            "max_tokens": 900
        }
    )
    return response["choices"][0]["message"]["content"]

# Expected failure modes identified by the LLM:
# 1. AnalysisException — silver/quarantine table does not exist yet (first run)
# 2. AnalysisException — schema mismatch (columns in clean_df don't match existing silver table)
# 3. Empty DataFrame — clean_df or quarantine_df is empty (no rows to write, count() = 0 — is this expected?)
#
# Expected hardened function includes:
# - try/except AnalysisException around each write with message:
#   "Failed to write to {silver_table}. Check: table exists in Unity Catalog, schema matches, write permissions."
# - check if clean_df is empty before writing, warn if so
```

**Tags**
- generative-ai / agentic-ai / prompt-engineering (skill)
- llm-integration / few-shot-learning (skill)

##### Input 6
**Type:** Choice

**Question:** You ask the LLM to add error handling to your `run_dq_scan()` function. The LLM returns the function with the email regex pattern changed from the original. What should you do?

**Options:** 
- Accept the change — the LLM likely found a bug in your regex

- Reject the full output — the LLM broke the constraint and cannot be trusted

- Accept the docstring and error handling but revert the regex to your original

- Re-run with a higher temperature to get a different version

**Correct Options:** 
- Accept the docstring and error handling but revert the regex to your original

**Solution:** 
Always treat LLM output as a starting point you review, not a replacement you blindly accept. The correct approach is to keep what the LLM added correctly (docstring, error handling) and revert any change to the core logic you did not ask for. This is why the system prompt constraint "do not change the function logic" is critical — if the LLM ignores it, your review catches it. LLMs occasionally "improve" code while adding documentation; the engineer's job is to own the diff.

**Tags**


##### Input 7
**Type:** Code

**Question:** Task 3 — Refactoring Assistant.
The GlobalMart Silver layer has a 30-line inline transformation block inside a notebook cell. Build a `suggest_refactor()` function that asks the LLM to propose a cleaner version with helper functions, and explain each change. Fill in the system prompt.

**Language:** python

**Snippet:** def suggest_refactor(code_block: str) -> str:
    """
    Proposes a refactored version of a PySpark code block with helper functions.
    Returns the refactored code + a change log explaining each modification.
    """
    SYSTEM_PROMPT = """________"""   # TODO: refactoring system prompt — ask for helper functions + change log

    response = w.serving_endpoints.predict(
        endpoint=ENDPOINT,
        inputs={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Suggest a refactoring for this PySpark code:\n\n{code_block}"}
            ],
            "temperature": 0.2,
            "max_tokens": 900
        }
    )
    return response["choices"][0]["message"]["content"]


# Inline transformation block from GlobalMart Silver notebook
INLINE_BLOCK = '''
transformed_df = (
    deduped_df
    .withColumn("DateOfBirth",      to_date(col("DateOfBirth"),      "yyyy-MM-dd"))
    .withColumn("RegistrationDate", to_date(col("RegistrationDate"), "yyyy-MM-dd"))
    .withColumn("FirstName",        trim(col("FirstName")))
    .withColumn("LastName",         trim(col("LastName")))
    .withColumn("full_name",            concat_ws(" ", col("FirstName"), col("LastName")))
    .withColumn("age",                  floor(datediff(current_date(), col("DateOfBirth")) / 365.25).cast("int"))
    .withColumn("customer_tenure_days", datediff(current_date(), col("RegistrationDate")).cast("int"))
    .withColumnRenamed("CustomerID",               "customer_id")
    .withColumnRenamed("FirstName",                "first_name")
    .withColumnRenamed("LastName",                 "last_name")
    .withColumnRenamed("Email",                    "email")
    .withColumnRenamed("PhoneNumber",              "phone_number")
    .withColumnRenamed("DateOfBirth",              "date_of_birth")
    .withColumnRenamed("RegistrationDate",         "registration_date")
    .withColumnRenamed("PreferredPaymentMethodID", "preferred_payment_method_id")
)
'''

print(suggest_refactor(INLINE_BLOCK))

**Solution:** 
```python
def suggest_refactor(code_block: str) -> str:
    SYSTEM_PROMPT = """You are a senior PySpark engineer reviewing a GlobalMart Silver layer notebook.
When given a PySpark transformation block:
1. Identify opportunities to extract reusable helper functions (date casting, column renaming, derived metrics)
2. Propose a refactored version using those helper functions
3. Return your response in two sections:

## Refactored Code
[complete refactored Python code — no markdown fences]

## Change Log
[bullet list of each change and the reason: maintainability, testability, or DRY principle]

Keep the transformation logic identical — only improve structure."""

    response = w.serving_endpoints.predict(
        endpoint=ENDPOINT,
        inputs={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Suggest a refactoring for this PySpark code:\n\n{code_block}"}
            ],
            "temperature": 0.2,
            "max_tokens": 900
        }
    )
    return response["choices"][0]["message"]["content"]

# Expected refactored code extracts:
# - cast_dates(df) — handles DateOfBirth + RegistrationDate to DateType
# - derive_metrics(df) — adds full_name, age, customer_tenure_days
# - rename_to_snake_case(df) — column rename mapping
# Main chain becomes: df = cast_dates(df); df = derive_metrics(df); df = rename_to_snake_case(df)
# Change log explains: easier to unit test individual helpers, reusable across other Silver tables
```

**Tags**
- generative-ai / agentic-ai / prompt-engineering (skill)
- llm-integration / system-prompt (skill)

##### Input 8
**Type:** Short Answer

**Question:** Your team lead says: "If the LLM can write docstrings and error handling, why don't we just have it rewrite the entire DQ pipeline from scratch every time we need a change?"

**Template:** null

**Solution:** 
Code enhancement (what we did) is safer for production pipelines because the LLM operates on existing, tested logic — it adds docstrings and wrappers around code that already works correctly. Code generation from scratch asks the LLM to invent logic it has never run on your data, which means it can plausibly generate a DQ scan that misses a specific GlobalMart edge case (like the `d'` apostrophe in email addresses) that your team discovered from real data. The distinction matters because production DE code encodes business decisions — the choice to quarantine REGISTERED_UNDER_18 instead of fixing it was a deliberate call after investigating the data; an LLM generating a pipeline from scratch would have no access to that context. Use LLM generation from scratch for boilerplate and scaffolding; use LLM enhancement for adding quality layers to code that already encodes your domain knowledge.

**Tags**
- llm-integration / llm-basics (skill)

