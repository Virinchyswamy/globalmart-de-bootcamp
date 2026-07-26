# Prompt Engineering SQL Productivity with LLMs
## Content Type
Scenario

## Overview
A 90-minute hands-on lab where you apply the prompt engineering patterns from the morning ILT to real GlobalMart SQL scenarios. You will build a SQL classifier that decides whether a query needs optimization, extend the NL-to-SQL translator to handle ambiguous questions, and write a prompt that generates a complete set of DQ constraint SQL statements from a table schema. Each task is self-contained and graded independently.

## Learning Objectives
- Build a zero-shot SQL complexity classifier using the Foundation Model API
- Handle ambiguous business questions in the NL-to-SQL translator using clarification prompts
- Generate SQL DQ constraints from a table schema using few-shot examples
- Evaluate LLM output quality using pass/fail criteria on known test cases

## Prerequisites
- Foundation Model API pattern working in your Databricks notebook

## Duration of Completion
90 minutes

## Level
Intermediate

## Industries
- retail-and-cpg

## Tags
- databricks (tool)
- sql (tool)
- gen-ai (tool)
- python (tool)
- ml-modelling (skill)
- ai-modelling (skill)
- generative-ai (skill)
- mlops (skill)
- llm-integration (skill)
- ai-engineering (skill)
- machine-learning (skill)
- approach (skill)
- data-understanding (skill)
- problem-understanding (skill)

#### Overview
A 90-minute hands-on lab where you apply the prompt engineering patterns from the morning ILT to real GlobalMart SQL scenarios. You will build a SQL classifier that decides whether a query needs optimization, extend the NL-to-SQL translator to handle ambiguous questions, and write a prompt that generates a complete set of DQ constraint SQL statements from a table schema. Each task is self-contained and graded independently.

#### Level
intermediate

#### Industries
- retail-and-cpg

#### Tags
- databricks (tool)
- sql (tool)
- gen-ai (tool)
- python (tool)
- ml-modelling (skill)
- ai-modelling (skill)
- generative-ai (skill)
- mlops (skill)
- llm-integration (skill)
- ai-engineering (skill)
- machine-learning (skill)
- approach (skill)
- data-understanding (skill)
- problem-understanding (skill)

#### Scenario Inputs
##### Input 1
**Type:** Text

### Lab Overview
<br>

This is a self-directed lab. You have 90 minutes. Each task builds on the patterns from the morning — you are not copying code, you are applying the patterns to new problems.

**Setup — run this cell first:**

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
ENDPOINT = "databricks-meta-llama-3-1-70b-instruct"

def call_llm(system_prompt: str, user_message: str, temperature: float = 0.0, max_tokens: int = 500) -> str:
    """Utility wrapper — use this throughout the lab to avoid repeating boilerplate."""
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

print("Ready. call_llm() is available.")
```

**Three tasks:**
<br>

| Task | Topic | Time | Credit |
|------|-------|------|--------|
| Task 1 | SQL Complexity Classifier | 25 min | 6 pts |
| Task 2 | Ambiguous NL-to-SQL | 30 min | 8 pts |
| Task 3 | DQ Constraint Generator | 35 min | 6 pts |



**Tags**


##### Input 2
**Type:** Text

### Task 1 — SQL Complexity Classifier (25 min)
<br>

A senior DE on your team wants a tool that reads a SQL query and classifies it as:
- `SIMPLE` — single table, no joins, no CTEs
- `MODERATE` — 1-2 joins or a CTE, no subqueries
- `COMPLEX` — 3+ joins, nested subqueries, window functions, or recursive CTEs

**Why this is useful:** Routes simple queries to junior reviewers and complex queries to seniors automatically.

**Your task:** Build `classify_sql_complexity()` using zero-shot prompting. The function must return exactly one of: `SIMPLE`, `MODERATE`, `COMPLEX` — no explanation, no JSON, just the label.

Test it on the four queries provided. Your classifier must get at least 3/4 correct.



**Tags**


##### Input 3
**Type:** Code

**Question:** Task 1 — Build the SQL Complexity Classifier.
Write the `classify_sql_complexity()` function. Design the system prompt so the output is exactly one word: SIMPLE, MODERATE, or COMPLEX. Then run the four test cases and report your accuracy.

**Language:** python

**Snippet:** def classify_sql_complexity(query: str) -> str:
    """Returns SIMPLE, MODERATE, or COMPLEX for a given SQL query."""
    system_prompt = """________"""   # TODO: write the classifier system prompt
    result = call_llm(system_prompt, query, temperature=0.0, max_tokens=10)
    return result.strip().upper()


# Test cases with expected labels
test_cases = [
    ("""SELECT customer_id, email FROM gbmart.silver.customers WHERE age > 25""",
     "SIMPLE"),

    ("""SELECT c.customer_id, c.full_name, COUNT(o.order_id) AS order_count
        FROM gbmart.silver.customers c
        JOIN gbmart.silver.orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id, c.full_name""",
     "MODERATE"),

    ("""WITH ranked AS (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS rn
            FROM gbmart.silver.orders
        )
        SELECT customer_id, order_id, total_amount
        FROM ranked WHERE rn = 1""",
     "MODERATE"),

    ("""WITH revenue AS (
            SELECT c.customer_id, SUM(f.revenue) AS total_rev
            FROM gbmart.silver.customers c
            JOIN gbmart.gold.fact_sales f ON c.customer_sk = f.customer_sk
            GROUP BY c.customer_id
        ),
        returns AS (
            SELECT customer_id, COUNT(*) AS return_count
            FROM gbmart.silver.returns
            GROUP BY customer_id
        )
        SELECT r.customer_id, r.total_rev,
               COALESCE(ret.return_count, 0) AS returns,
               r.total_rev / NULLIF(COALESCE(ret.return_count, 0), 0) AS rev_per_return
        FROM revenue r LEFT JOIN returns ret ON r.customer_id = ret.customer_id
        ORDER BY rev_per_return DESC""",
     "COMPLEX")
]

print("Testing SQL Complexity Classifier\n" + "="*40)
correct = 0
for query, expected in test_cases:
    predicted = classify_sql_complexity(query)
    match = "✓" if predicted == expected else "✗"
    print(f"{match}  Expected: {expected} | Got: {predicted}")
    if predicted == expected:
        correct += 1

print(f"\nAccuracy: {correct}/{len(test_cases)}")

**Solution:** 
```python
def classify_sql_complexity(query: str) -> str:
    system_prompt = """Classify the complexity of a SQL query as exactly one of: SIMPLE, MODERATE, or COMPLEX.

SIMPLE = single table, no joins, no CTEs, no subqueries, no window functions
MODERATE = 1-2 explicit JOINs, or a single CTE, or a simple subquery — no nesting
COMPLEX = 3+ JOINs, multiple CTEs, nested subqueries, window functions (ROW_NUMBER, RANK, LAG), or recursive CTEs

Respond with exactly one word: SIMPLE, MODERATE, or COMPLEX.
No explanation, no punctuation, no additional text."""

    result = call_llm(system_prompt, query, temperature=0.0, max_tokens=10)
    return result.strip().upper()

# The MODERATE classification for the ROW_NUMBER CTE query is debatable:
# some prompt designs classify window functions as COMPLEX.
# If your classifier returns COMPLEX for test case 3, update the expected to COMPLEX
# and note this in your short answer (Input 9).
```

**Tags**
- llm-integration / prompt-engineering (skill)
- llm-integration / system-prompt (skill)

##### Input 4
**Type:** Text

### Task 2 — Ambiguous NL-to-SQL (30 min)
<br>

In the morning you built a NL-to-SQL translator. But business questions are often ambiguous:

- "Show me top customers" — top by what? Revenue? Order count? Tenure?
- "Which products are slow-moving?" — what's the threshold? Last 30 days? Last quarter?
- "Find high-value orders" — what's the high-value cutoff?

A naive NL-to-SQL tool makes assumptions and returns a query that may answer the wrong question. A better approach: detect ambiguity and ask one clarifying question before writing SQL.

**Your task:** Build an `ambiguous_nl_to_sql()` function that:
1. First checks if the question is ambiguous (missing key parameter)
2. If ambiguous, returns a clarifying question instead of SQL
3. If clear, returns the SQL directly



**Tags**


##### Input 5
**Type:** Code

**Question:** Task 2 — Build the Ambiguous NL-to-SQL Handler. 
The function should take a question and return either SQL (if clear) or a clarifying question (if ambiguous). Design your system prompt to detect the ambiguity and respond in a structured way that your code can parse. Test on the four questions provided.

**Language:** python

**Snippet:** GLOBALMART_SCHEMA = """
gbmart.silver.customers  — customer_id, full_name, email, customer_tenure_days, age, registration_date, is_current
gbmart.silver.orders     — order_id, customer_id, order_date, total_amount, status
gbmart.silver.order_items— order_item_id, order_id, product_id, quantity, unit_price
gbmart.silver.products   — product_id, product_name, category, unit_cost
gbmart.silver.returns    — return_id, order_id, customer_id, return_date, reason
gbmart.gold.fact_sales   — order_sk, customer_sk, product_sk, sale_date, revenue, quantity_sold
gbmart.gold.dim_customers— customer_sk, customer_id, full_name, tenure_tier (New/Regular/Loyal)
"""

def ambiguous_nl_to_sql(question: str) -> dict:
    """
    Returns a dict: {"type": "sql", "content": "SELECT..."} if the question is clear,
    or {"type": "clarification", "content": "Which metric should I use..."} if ambiguous.
    """
    system_prompt = f"""________"""   # TODO: system prompt that returns structured output you can parse

    raw = call_llm(system_prompt, question, temperature=0.0, max_tokens=400)

    # TODO: parse the LLM output into {"type": "sql"/"clarification", "content": "..."}
    # Hint: design your system prompt to start the response with "SQL:" or "CLARIFY:"
    ________

    return result


test_questions = [
    "Show me the top 10 customers by total revenue in the last 30 days",   # CLEAR — should return SQL
    "Find our slow-moving products",                                         # AMBIGUOUS — needs threshold
    "Which customers are at risk of churning?",                             # AMBIGUOUS — no churn definition
    "List all orders from July 2026 with status = 'RETURNED'"               # CLEAR — should return SQL
]

for q in test_questions:
    result = ambiguous_nl_to_sql(q)
    print(f"Q: {q}")
    print(f"Type: {result['type']}")
    print(f"Response: {result['content'][:200]}")
    print()

**Solution:** 
```python
def ambiguous_nl_to_sql(question: str) -> dict:
    system_prompt = f"""You are a SQL generator for GlobalMart. Use ONLY the tables below.

SCHEMA:
{GLOBALMART_SCHEMA}

Rules:
1. If the question has a missing key parameter (metric, threshold, time range, or definition),
   respond with: CLARIFY: [one specific clarifying question]
2. If the question is clear enough to write accurate SQL, respond with: SQL: [the query]
3. Use fully qualified table names. No markdown. One line starting with SQL: or CLARIFY:"""

    raw = call_llm(system_prompt, question, temperature=0.0, max_tokens=400)
    raw = raw.strip()

    if raw.startswith("SQL:"):
        return {"type": "sql", "content": raw[4:].strip()}
    elif raw.startswith("CLARIFY:"):
        return {"type": "clarification", "content": raw[8:].strip()}
    else:
        # fallback — if the LLM didn't follow format, treat as SQL
        return {"type": "sql", "content": raw}

# Expected results:
# Q1 "top 10 customers by total revenue" → SQL: SELECT ... (clear enough)
# Q2 "slow-moving products" → CLARIFY: "What threshold defines slow-moving? (e.g., <10 units sold in last 30 days?)"
# Q3 "customers at risk of churning" → CLARIFY: "What is your churn definition? (e.g., no order in last 90 days?)"
# Q4 "orders from July 2026 with status RETURNED" → SQL: SELECT ...
```

**Tags**
- llm-integration / system-prompt (skill)
- llm-integration / prompt-engineering (skill)

##### Input 6
**Type:** Text

### Task 3 — DQ Constraint Generator (35 min)
<br>

Writing `WHERE` clauses for DQ checks is repetitive. Given a table schema with column types and known business rules, an LLM can generate the full `withColumn("_dq_issue", when(...))` chain — the same pattern you saw in the Silver layer notebooks.

**Your task:** Build a `generate_dq_constraints()` function that:
1. Takes a table schema (column names, types, and business rules)
2. Produces a complete PySpark DQ scan block with `withColumn("_dq_issue", when(...))` logic
3. Uses few-shot examples to teach the LLM GlobalMart's DQ pattern



**Tags**


##### Input 7
**Type:** Code

**Question:** Task 3 — Build the DQ Constraint Generator. 
Write the `generate_dq_constraints()` function using few-shot prompting. The few-shot examples show the pattern from the Silver layer. Test on the `gbmart.silver.order_items` schema provided.

**Language:** python

**Snippet:** ORDER_ITEMS_SCHEMA = """
Table: gbmart.silver.order_items
Columns:
- order_item_id  STRING   NOT NULL   Business rule: must match pattern OI-XXXXX
- order_id       STRING   NOT NULL   Business rule: must exist in gbmart.silver.orders
- product_id     STRING   NOT NULL   Business rule: must exist in gbmart.silver.products
- quantity       INT      NOT NULL   Business rule: must be >= 1
- unit_price     DECIMAL  NOT NULL   Business rule: must be > 0.0
"""

def generate_dq_constraints(schema_text: str) -> str:
    """
    Generates a PySpark DQ scan withColumn block for the given table schema.
    Uses few-shot examples to match GlobalMart's Silver layer DQ pattern.
    """
    FEW_SHOT = """Example — customers table:
Schema:
- CustomerID   STRING   NOT NULL
- Email        STRING   NOT NULL  Business rule: must match email regex
- DateOfBirth  STRING   NOT NULL  Business rule: customer must be 18+ at registration

Generated DQ block:
dq_df = bronze_df \\
    .withColumn("_dob_temp", to_date(col("DateOfBirth"), "yyyy-MM-dd")) \\
    .withColumn("_reg_temp", to_date(col("RegistrationDate"), "yyyy-MM-dd")) \\
    .withColumn("_age_at_reg", floor(datediff(col("_reg_temp"), col("_dob_temp")) / 365.25)) \\
    .withColumn("_dq_issue",
        when(col("CustomerID").isNull(),                         lit("NULL_CUSTOMER_ID"))
        .when(col("Email").isNull(),                             lit("NULL_EMAIL"))
        .when(~col("Email").rlike(EMAIL_REGEX),                  lit("INVALID_EMAIL_FORMAT"))
        .when(col("_age_at_reg") < 18,                           lit("REGISTERED_UNDER_18"))
        .otherwise(lit(None))
    )"""

    system_prompt = f"""________"""   # TODO: few-shot system prompt

    return call_llm(system_prompt, f"Generate DQ constraints for:\n{schema_text}", temperature=0.0, max_tokens=600)


print(generate_dq_constraints(ORDER_ITEMS_SCHEMA))

**Solution:** 
```python
def generate_dq_constraints(schema_text: str) -> str:
    FEW_SHOT = """Example — customers table:
Schema:
- CustomerID   STRING   NOT NULL
- Email        STRING   NOT NULL  Business rule: must match email regex
- DateOfBirth  STRING   NOT NULL  Business rule: customer must be 18+ at registration

Generated DQ block:
dq_df = bronze_df \\
    .withColumn("_dob_temp", to_date(col("DateOfBirth"), "yyyy-MM-dd")) \\
    .withColumn("_reg_temp", to_date(col("RegistrationDate"), "yyyy-MM-dd")) \\
    .withColumn("_age_at_reg", floor(datediff(col("_reg_temp"), col("_dob_temp")) / 365.25)) \\
    .withColumn("_dq_issue",
        when(col("CustomerID").isNull(),                         lit("NULL_CUSTOMER_ID"))
        .when(col("Email").isNull(),                             lit("NULL_EMAIL"))
        .when(~col("Email").rlike(EMAIL_REGEX),                  lit("INVALID_EMAIL_FORMAT"))
        .when(col("_age_at_reg") < 18,                           lit("REGISTERED_UNDER_18"))
        .otherwise(lit(None))
    )"""

    system_prompt = f"""You are a GlobalMart PySpark expert generating DQ constraint code.
Use the example below to understand the pattern. Generate a complete PySpark DQ scan block
following exactly the same withColumn + when/otherwise pattern.

Rules:
- NULL checks: when(col("X").isNull(), lit("NULL_X"))
- Format checks: when(~col("X").rlike(pattern), lit("INVALID_X_FORMAT"))
- Range checks: when(col("X") < min_val, lit("INVALID_X_RANGE"))
- Use descriptive issue codes in SCREAMING_SNAKE_CASE
- End every chain with .otherwise(lit(None))
- No markdown fences, return only Python code

{FEW_SHOT}"""

    return call_llm(system_prompt, f"Generate DQ constraints for:\n{schema_text}", temperature=0.0, max_tokens=600)

# Expected output (approximate):
# dq_df = bronze_df \
#     .withColumn("_dq_issue",
#         when(col("order_item_id").isNull(),                   lit("NULL_ORDER_ITEM_ID"))
#         .when(~col("order_item_id").rlike(r"^OI-\w+$"),       lit("INVALID_ORDER_ITEM_ID_FORMAT"))
#         .when(col("order_id").isNull(),                        lit("NULL_ORDER_ID"))
#         .when(col("product_id").isNull(),                      lit("NULL_PRODUCT_ID"))
#         .when(col("quantity").isNull(),                        lit("NULL_QUANTITY"))
#         .when(col("quantity") < 1,                             lit("INVALID_QUANTITY_RANGE"))
#         .when(col("unit_price").isNull(),                      lit("NULL_UNIT_PRICE"))
#         .when(col("unit_price") <= 0,                          lit("INVALID_UNIT_PRICE_RANGE"))
#         .otherwise(lit(None))
#     )
```

**Tags**
- llm-integration / few-shot-learning (skill)
- llm-integration / prompt-engineering (skill)

##### Input 8
**Type:** Short Answer

**Question:** In Task 2 (ambiguous NL-to-SQL), your system prompt uses a simple `CLARIFY:` / `SQL:` prefix to make the output parseable. A colleague suggests using JSON output instead: `{"type": "clarify", "content": "..."}`. What are the trade-offs between these two approaches for a production NL-to-SQL tool?

**Template:** null

**Solution:** 
The `CLARIFY:` / `SQL:` prefix approach is simpler to implement and more robust with smaller models — the LLM reliably produces a two-token prefix before its content, so parsing is a simple `startswith()` check. JSON output is more flexible and extensible (you can add fields like `"confidence"`, `"tables_used"`, `"clarification_type"`) but is more fragile: the LLM may wrap the JSON in markdown fences, include trailing commas, or produce partially valid JSON when the output is long — all of which break `json.loads()`. For a production tool, JSON is the right long-term choice if you add a post-processing step that strips markdown fences before parsing, includes a fallback for malformed output, and uses `temperature: 0.0` consistently. For a quick internal tool or MVP, the prefix approach is more reliable and takes less debugging.

**Tags**
- llm-integration / structured-output-parsing (skill)
- generative-ai / agentic-ai / prompt-engineering (skill)

##### Input 9
**Type:** File Upload

**Question:** Take a screenshot of your Databricks notebook showing the output of all three tasks:

**Max No. of Files:** 3

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**
- approach / concept-clarity (skill)

