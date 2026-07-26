# Prompt Engineering DE Documentation Generator
## Content Type
Scenario

## Overview
A 75-minute self-directed lab where you build a DE Documentation Generator — a tool that takes GlobalMart pipeline artifacts (quarantine tables, Silver schemas, error logs) and produces ready-to-publish documentation. You will generate a DQ runbook from a quarantine summary, produce a data lineage description from a transformation notebook, and write a pipeline incident report from an error log. These are real outputs a data engineer produces weekly; you will build the LLM tools that generate them in minutes.

## Learning Objectives
- Build a DQ runbook generator from a quarantine table summary
- Generate a data lineage description from a transformation chain
- Write a pipeline incident report using chain-of-thought prompting from an error log

## Prerequisites
- Foundation Model API pattern working in your Databricks notebook

## Duration of Completion
75 minutes

## Level
Intermediate

## Industries
- retail-and-cpg

## Tags
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

#### Overview
A 75-minute self-directed lab where you build a DE Documentation Generator — a tool that takes GlobalMart pipeline artifacts (quarantine tables, Silver schemas, error logs) and produces ready-to-publish documentation. You will generate a DQ runbook from a quarantine summary, produce a data lineage description from a transformation notebook, and write a pipeline incident report from an error log. These are real outputs a data engineer produces weekly; you will build the LLM tools that generate them in minutes.

#### Level
intermediate

#### Industries
- retail-and-cpg

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

### Lab Overview — What You Are Building
<br>

A **DE Documentation Generator** is a collection of LLM-powered tools that produce documentation artifacts automatically. Data engineers spend 2–3 hours per week writing these — after this lab you will have tools that generate them in under 2 minutes.

**Three documentation tasks:**

| Task | Input | Output | Time |
|------|-------|--------|------|
| Task 1: DQ Runbook | Quarantine summary (issue → count → action) | Runbook for ops team | 20 min |
| Task 2: Data Lineage | Transformation notebook description | Lineage paragraph for data catalog | 25 min |
| Task 3: Incident Report | Error log + downstream impact | Structured incident report | 30 min |

**Setup:**

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
ENDPOINT = "databricks-meta-llama-3-1-70b-instruct"

def call_llm(system_prompt: str, user_message: str, temperature: float = 0.0, max_tokens: int = 600) -> str:
    response = w.serving_endpoints.predict(
        endpoint=ENDPOINT,
        inputs={
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
    )
    return response["choices"][0]["message"]["content"]

print("Ready.")
```



**Tags**


##### Input 2
**Type:** Text

### Task 1 — DQ Runbook Generator (20 min)
<br>

A DQ runbook tells the operations team exactly what to do when a data quality issue occurs. It is not the same as the stakeholder summary from MC-PE-01 Scenario 3 — a runbook is technical and step-by-step, for the person who will fix the problem.

**Runbook structure:**
```
## Issue: REGISTERED_UNDER_18

**Severity:** HIGH — legal compliance risk
**Table:** gbmart.silver.customers_quarantine
**Trigger:** count > 0 of REGISTERED_UNDER_18 records today

**Investigation Steps:**
1. Run: SELECT * FROM gbmart.silver.customers_quarantine WHERE _dq_issue = 'REGISTERED_UNDER_18' AND DATE(_quarantine_ts) = current_date()
2. Check date_of_birth vs registration_date for each flagged record
3. ...

**Resolution Options:**
A. If DOB is incorrect: [manual correction process]
B. If customer was genuinely under 18: [legal escalation process]

**Escalation:** If count > 100: immediately notify [responsible team]
```

Your task: build a `generate_dq_runbook()` function that produces a runbook like this from a quarantine summary.



**Tags**


##### Input 3
**Type:** Code

**Question:** Task 1 — DQ Runbook Generator.
Build `generate_dq_runbook()`. The function takes a list of DQ issues (issue_code, count, table_name) and produces a structured runbook with investigation steps and resolution options for each issue. Design your system prompt to produce the structured format shown in Input 2.

**Language:** python

**Snippet:** def generate_dq_runbook(issues: list, silver_table: str) -> str:
    """
    Generates a DQ operations runbook for the data engineering team.

    Args:
        issues: list of dicts with keys: issue_code (str), count (int), severity (str)
        silver_table: the Silver table that was scanned (e.g., gbmart.silver.customers)
    """
    quarantine_table = silver_table + "_quarantine"

    issues_summary = "\n".join([
        f"- {i['issue_code']}: {i['count']} records today | Severity: {i['severity']}"
        for i in issues
    ])

    SYSTEM_PROMPT = """________"""   # TODO: technical runbook generator system prompt
    # Hint: persona = senior DE writing for the on-call engineer
    # Output format: one runbook section per issue with: severity, investigation SQL, resolution options, escalation trigger

    USER_MESSAGE = f"""Generate a DQ runbook for the following issues found in {silver_table}:
Quarantine table: {quarantine_table}

Issues found today:
{issues_summary}"""

    return call_llm(SYSTEM_PROMPT, USER_MESSAGE, temperature=0.0, max_tokens=900)


# Real GlobalMart quarantine data from today's run
TODAY_ISSUES = [
    {"issue_code": "REGISTERED_UNDER_18", "count": 77,  "severity": "HIGH"},
    {"issue_code": "INVALID_EMAIL_FORMAT", "count": 3,   "severity": "MEDIUM"},
    {"issue_code": "NULL_FIRST_NAME",      "count": 4,   "severity": "LOW"}
]

runbook = generate_dq_runbook(TODAY_ISSUES, "gbmart.silver.customers")
print(runbook)

**Solution:** 
```python
def generate_dq_runbook(issues: list, silver_table: str) -> str:
    quarantine_table = silver_table + "_quarantine"
    issues_summary = "\n".join([
        f"- {i['issue_code']}: {i['count']} records today | Severity: {i['severity']}"
        for i in issues
    ])

    SYSTEM_PROMPT = f"""You are a senior data engineer writing a DQ operations runbook for GlobalMart.
The audience is the on-call data engineer who will respond to this alert.

For each DQ issue, produce a runbook section with this structure:

## Issue: [ISSUE_CODE]

**Tags**
- llm-integration / system-prompt (skill)
- llm-integration / prompt-engineering (skill)

##### Input 4
**Type:** Text

### Task 2 — Data Lineage Description Generator (25 min)
<br>

A data lineage description explains where data came from, what transformations were applied, and where it goes next. It lives in the data catalog (Databricks Unity Catalog lineage view, or Confluence). Writing one per table takes 30–45 minutes.

**Target format:**

```
## Data Lineage: gbmart.silver.customers

**Source:** gbmart.bronze.customers (append-only, loaded by Autoloader from GCS)

**Transformations applied:**
- Email cleaning: removed spaces, stripped d' apostrophe prefix; 3 records fixed
- Phone reformatting: converted 12-digit raw format (91XXXXXXXXXX) to +91-XXXXXXXXXX
- Age validation: 77 records with age < 18 at registration moved to quarantine
- Deduplication: latest record per CustomerID retained using _ingested_at window

**Derived columns added:**
- full_name = concat(first_name, last_name)
- age = floor(datediff(today, date_of_birth) / 365.25)
- customer_tenure_days = datediff(today, registration_date)
- customer_sk = sha2(customer_id || effective_start_date, 256)

**Downstream consumers:**
- gbmart.gold.dim_customers (daily refresh)
- gbmart.gold.fact_sales (joins via customer_sk)
- Genie NLQ (customer segmentation queries)
```

Your task: build a `generate_lineage_description()` function that produces this from a transformation notebook description.



**Tags**


##### Input 5
**Type:** Code

**Question:** Task 2 — Data Lineage Generator.
Build `generate_lineage_description()`. The function takes: the source table, a list of transformations applied (as text), derived columns added, and downstream consumers. It produces a lineage description in the format shown in Input 4.

**Language:** python

**Snippet:** def generate_lineage_description(
    table_name: str,
    source_table: str,
    transformations: list,
    derived_columns: list,
    downstream_consumers: list
) -> str:
    """Generates a data catalog lineage description for a GlobalMart Silver table."""

    SYSTEM_PROMPT = """________"""   # TODO: data lineage documentation system prompt

    USER_MESSAGE = f"""Generate a data lineage description for {table_name}.

Source: {source_table}

Transformations applied:
{chr(10).join(f'- {t}' for t in transformations)}

Derived columns added:
{chr(10).join(f'- {d}' for d in derived_columns)}

Downstream consumers:
{chr(10).join(f'- {c}' for c in downstream_consumers)}"""

    return call_llm(SYSTEM_PROMPT, USER_MESSAGE, temperature=0.0, max_tokens=700)


# From the actual GlobalMart Silver customers notebook
lineage = generate_lineage_description(
    table_name="gbmart.silver.customers",
    source_table="gbmart.bronze.customers (append-only, Autoloader from GCS)",
    transformations=[
        "Email cleaning: removed spaces and d' apostrophe prefix — 3 records fixed",
        "Phone reformatting: converted 12-digit raw BIGINT (91XXXXXXXXXX) to +91-XXXXXXXXXX string format",
        "Age validation: 77 records with age_at_registration < 18 moved to customers_quarantine",
        "Deduplication: latest record per CustomerID retained using row_number over _ingested_at",
        "Column renaming: all columns renamed from PascalCase (CustomerID) to snake_case (customer_id)"
    ],
    derived_columns=[
        "full_name = concat_ws(' ', first_name, last_name)",
        "age = floor(datediff(current_date, date_of_birth) / 365.25)",
        "customer_tenure_days = datediff(current_date, registration_date)",
        "customer_sk = sha2(concat_ws('|', customer_id, effective_start_date), 256)  -- SCD2 surrogate key"
    ],
    downstream_consumers=[
        "gbmart.gold.dim_customers — refreshed daily",
        "gbmart.gold.fact_sales — joins via customer_sk",
        "gbmart.silver.customers_quarantine — receives non-conforming records",
        "Genie NLQ — customer segmentation and tenure analysis"
    ]
)

print(lineage)

**Solution:** 
```python
def generate_lineage_description(table_name, source_table, transformations, derived_columns, downstream_consumers) -> str:
    SYSTEM_PROMPT = """You are a data catalog engineer at GlobalMart writing a data lineage description.
Produce a structured lineage document in Markdown with these sections:

## Data Lineage: [table_name]

**Tags**
- llm-integration / system-prompt (skill)
- llm-integration / prompt-engineering (skill)

##### Input 6
**Type:** Text

### Task 3 — Pipeline Incident Report (30 min)
<br>

When a pipeline fails in production, the on-call engineer must write an incident report. This is time-pressured, stressful work — and the report is often written poorly under pressure.

**Using chain-of-thought prompting** (from MC-PE-01 Scenario 2), you can ask the LLM to reason through the failure before writing the report — which produces more accurate root cause analysis.

**Target incident report format:**

```
## Incident Report — GlobalMart Silver Pipeline
Date: 2026-07-23 | Severity: P2 | Status: RESOLVED

### Timeline
- 04:32 UTC: Pipeline started (scheduled)
- 04:47 UTC: gbmart.silver.orders write failed
- 04:47 UTC: Alert triggered — on-call paged
- 05:15 UTC: Root cause identified
- 05:42 UTC: Fix deployed; pipeline resumed
- 06:01 UTC: gbmart.silver.orders confirmed healthy

### Root Cause
[LLM-generated root cause analysis]

### Impact
[Affected tables, downstream consumers, business impact duration]

### Resolution
[Steps taken to fix]

### Prevention
[What will prevent this from recurring]
```

Your task: build a `generate_incident_report()` function using chain-of-thought prompting.



**Tags**


##### Input 7
**Type:** Code

**Question:** Task 3 — Incident Report Generator.
Build `generate_incident_report()` using chain-of-thought prompting. The system prompt must instruct the LLM to: (a) reason about root cause from the error log BEFORE writing the report, (b) produce the report in the structured format from Input 6. Test on the error log provided.

**Language:** python

**Snippet:** def generate_incident_report(
    error_log: str,
    affected_table: str,
    downstream_impact: str,
    timeline: str
) -> str:
    """
    Generates a pipeline incident report using chain-of-thought reasoning.
    LLM first diagnoses root cause from the error log, then writes the structured report.
    """
    SYSTEM_PROMPT = """________"""   # TODO: chain-of-thought incident report system prompt
    # Must include:
    # Step 1: Analyze error log — identify root cause and contributing factors
    # Step 2: Write the structured incident report

    USER_MESSAGE = f"""
Error log:
{error_log}

Affected table: {affected_table}
Downstream impact: {downstream_impact}
Timeline: {timeline}

Generate the incident report."""

    return call_llm(SYSTEM_PROMPT, USER_MESSAGE, temperature=0.0, max_tokens=800)


ERROR_LOG = """
2026-07-23 04:47:13 ERROR SparkContext: Job 142 failed
  Task 8 in Stage 23 failed 4 times; aborting job
  AnalysisException: Column 'preferred_payment_method_id' not found in schema.
  Current schema: [customer_sk, customer_id, first_name, last_name, full_name,
                   email, phone_number, date_of_birth, age, registration_date,
                   customer_tenure_days, is_current, effective_start_date,
                   effective_end_date, _source_file, _silver_updated_at]
  Pipeline: build_silver_customers
  Write target: gbmart.silver.customers (APPEND mode)
2026-07-23 04:47:14 INFO DeltaLog: Rolling back transaction 891
"""

TIMELINE = """
04:30 UTC: Daily Silver pipeline scheduled start
04:47 UTC: Pipeline failed on gbmart.silver.customers write
04:47 UTC: P2 alert triggered, on-call paged
05:15 UTC: Root cause identified — schema change in Bronze source
05:40 UTC: Column mapping updated in transformation notebook
05:42 UTC: Pipeline restarted
06:01 UTC: gbmart.silver.customers confirmed healthy (count: 21,847)
"""

DOWNSTREAM = """
gbmart.gold.dim_customers refresh delayed by ~2 hours
Genie NLQ customer queries returned stale data during outage window
Marketing report for Jul 23 morning standup was ~90 min late
"""

report = generate_incident_report(ERROR_LOG, "gbmart.silver.customers", DOWNSTREAM, TIMELINE)
print(report)

**Solution:** 
```python
def generate_incident_report(error_log: str, affected_table: str, downstream_impact: str, timeline: str) -> str:
    SYSTEM_PROMPT = """You are a senior data engineer writing a pipeline incident report for GlobalMart.

Step 1 — Root Cause Analysis: Read the error log carefully. Identify:
- The specific error type and what it means
- Which pipeline step failed
- What likely caused the failure (schema change, data issue, config drift, etc.)
- Any contributing factors

Step 2 — Write the structured incident report using this exact format:

## Incident Report — [pipeline name]
Date: [from timeline] | Severity: [P1/P2/P3] | Status: RESOLVED

### Timeline
[bullet list from the provided timeline]

### Root Cause
[2-3 sentences: what failed, why, what triggered it]

### Impact
[bullet list: affected tables, downstream consumers, business impact duration]

### Resolution
[numbered list: exact steps taken to fix]

### Prevention
[2-3 bullet points: changes to prevent recurrence]

Be specific — include table names, error messages, and exact steps."""

    USER_MESSAGE = f"""
Error log:
{error_log}

Affected table: {affected_table}
Downstream impact: {downstream_impact}
Timeline: {timeline}

First diagnose the root cause from the error log, then write the incident report."""

    return call_llm(SYSTEM_PROMPT, USER_MESSAGE, temperature=0.0, max_tokens=800)

# Root cause the LLM should identify:
# AnalysisException: Column 'preferred_payment_method_id' not found
# → The Silver transformation notebook expected this column but the Bronze schema changed
# → Either a source system column was renamed/removed, or a prior transformation notebook
#   that added the column was skipped
# Prevention: add schema validation step before write; use MERGE with explicit column list
#   instead of APPEND with SELECT *; add Bronze schema change alerting
```

**Tags**
- llm-integration / prompt-engineering (skill)

##### Input 8
**Type:** Short Answer

**Question:** In Task 3, you used chain-of-thought prompting to make the LLM reason about the error log before writing the incident report. Compare the root cause section your tool generated with what you would have written if given the same error log without LLM assistance. In 3–4 sentences, describe one thing the LLM identified correctly that you might have missed or spent time looking up, and one thing the LLM got wrong or was vague about that required your domain knowledge to correct.

**Template:** null

**Solution:** 
Sample answer (learner's actual experience will vary):
The LLM correctly identified that `AnalysisException: Column not found` in the context of a Delta APPEND write means the source schema diverged from what the transformation notebook expected — it correctly suggested the root cause was a schema change in the Bronze source rather than a notebook bug, which saved me time I would have spent re-reading the notebook logic. However, the LLM was vague about the prevention step — it suggested "add schema validation" without specifying the actual Spark command to use (`from pyspark.sql import functions as F; F.schema_of_json()`, or Delta constraints, or a `MERGE` with explicit column mapping). That part required my domain knowledge to make the recommendation specific and actionable. This reflects the general pattern: LLMs are strong at pattern recognition and diagnosis but weak at GlobalMart-specific technical prescriptions — the more specific the prevention step needs to be, the more you need to fill in from your own knowledge.

**Tags**
- llm-integration / prompt-engineering (skill)

##### Input 9
**Type:** File Upload

**Question:** Take a screenshot of your Databricks notebook showing outputs from all three tasks:

**Max No. of Files:** 3

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**
- approach / concept-clarity (skill)

