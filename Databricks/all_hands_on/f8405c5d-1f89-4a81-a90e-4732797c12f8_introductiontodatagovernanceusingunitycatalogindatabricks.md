# Introduction to Data Governance using Unity Catalog in Databricks
## Content Type
Masterclass

## Overview
<p style="text-align:justify;">
This module introduces data governance in Databricks, focusing on challenges in managing data access across multiple workspaces. It covers key governance aspects such as access control, user & role management, data lineage, data audit, and data discovery to ensure data security, compliance, and efficiency.

<p style="text-align:justify;">
The module then explores Unity Catalog, Databricks' built-in governance solution that centralizes access control, auditing, and metadata management across workspaces. It explains the benefits of a unified governance framework and the hierarchical structure of Unity Catalog.

<p style="text-align:justify;">
Finally, you will learn how to create a catalog in Unity Catalog, which serves as the top-level container for organizing datasets. The module covers catalog creation using Databricks UI and SQL commands, catalog types, and storage configuration for efficient data management.

## Learning Objectives
- Understand the importance of data governance and the challenges of managing access across multiple workspaces.
- Explain key governance aspects such as access control, user & role management, data lineage, data audit, and data discovery.
- Describe Unity Catalog and its role in centralizing governance, auditing, and metadata management in Databricks.
- Create and manage catalogs in Unity Catalog using both Databricks UI and SQL commands.

## Prerequisites
- Basic understanding of Databricks workspaces and how users access data.
- Familiarity with database concepts, including schemas, tables

## Duration of Completion
80 minutes

## Level
Intermediate

## Industries
- general

## Tags
- batch-etl (skill)
- data-governance (skill)
- access-control-security (skill)
- approach (skill)
- databricks (tool)
- data-storage (skill)
- data-modelling (skill)

## Scenarios
### Need for Data Governance
#### Overview
<p style="text-align:justify;">
This module introduces data governance in Databricks, highlighting challenges in managing data access across multiple workspaces. It covers key governance aspects such as access control, user & role management, data lineage, data audit, and data discovery. Organizations can ensure data security, compliance, and efficiency by implementing a structured governance framework.

#### Level
intermediate

#### Industries
- general

#### Tags
- batch-etl (skill)
- data-governance (skill)
- access-control-security (skill)
- approach (skill)
- databricks (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

John, a junior data engineer at GlobalMart, has noticed growing challenges in managing data access and security across multiple Databricks workspaces. Every time a new analyst or data scientist joins, the senior engineers manually assign permissions, but the process is error-prone and inconsistent.

Recently, below major incidents raised serious concerns:

![Image-image.png](https://cdn.enqurious.com/images/9b0e4764-8d77-4ea3-8573-20f6bb891592_image.webp)

John realizes that without a proper data governance framework, these issues will continue to grow. To understand how to address these challenges, he reaches out to Sharon, a senior data engineer, to explore a better way to secure and manage data in Databricks.

**Tags**


##### Input 2
**Type:** Text

**John:** Sharon, managing data access across multiple teams is turning into a nightmare. Manual permissions are messy, and we’ve already had incidents of unauthorized access and data modifications.

**Sharon:** I get it, John. Without a structured governance model, things can get chaotic. That’s why **data governance** is crucial.

**John:** Governance? You mean just setting up access controls?

**Sharon:** It’s much more than that. Governance ensures:

*   **Access Control:** Only authorized users access specific datasets.
*   **Data Lineage:** Tracks where data comes from and how it's used.
*   **Data Audit:** Logs and tracks **who accessed, modified, or shared data**, ensuring transparency and accountability.
*   **Data Discovery:** Makes finding the right dataset easy while maintaining security.
*   **User & Role Management:** Ensures permissions are assigned centrally and consistently.

**John:** That’s exactly what we need!

**Tags**


##### Input 3
**Type:** Choice

**Question:** Which of the following is NOT a key aspect of data governance?

**Options:** 
- Access Control

- Increasing query performance

- Data Lineage

- Security & Compliance

**Correct Options:** 
- Increasing query performance

**Tags**
- approach / concept-clarity (skill)

##### Input 4
**Type:** Text

**John:** So, when you say access control, you mean restricting who can view or modify data?

**Sharon:** Exactly! Without proper access control, anyone could access sensitive data, leading to security breaches and compliance violations.

**John:** How does governance improve this?

**Sharon:** With a governance framework, we can:  
✅ Define permissions at the table, column, or row level  
✅ Ensure different teams only access relevant data  
✅ Use role-based access control (RBAC) for managing permissions centrally

**John:** So, instead of manually assigning permissions, we set rules centrally and apply them across workspaces?

**Sharon:** Exactly! That way, access is consistent, secure, and scalable.

**Tags**


##### Input 5
**Type:** Choice

**Question:** What is the primary purpose of Access Control in Data Governance?

**Options:** 
- To allow all users to access all datasets

- To restrict unauthorized access to specific datasets

- To improve query performance

- To duplicate datasets for different teams

**Correct Options:** 
- To restrict unauthorized access to specific datasets

**Tags**
- access-control-security / role-based-access-control (skill)

##### Input 6
**Type:** Text

**John:** You also mentioned User & Role Management. How does that differ from access control?

**Sharon:** Access control restricts what data users can access, while User & Role Management defines who gets those permissions.

**John:** So, instead of managing users one by one, we define roles and assign permissions to roles?

**Sharon:** Exactly! A governance model ensures:  
✅ Users are added at the account level, ensuring centralized management.  
✅ Roles define what users can access, instead of assigning permissions individually.  
✅ Access policies apply consistently across all workspaces, reducing manual effort.

**John:** That sounds much better than manually assigning access every time someone joins!

**Tags**


##### Input 7
**Type:** Choice

**Question:** How does User & Role Management improve data governance?

**Options:** 
- It removes the need for access control

- It allows every user to modify permissions

- It assigns permissions centrally instead of manually for each user

- It prevents users from accessing any data

**Correct Options:** 
- It assigns permissions centrally instead of manually for each user

**Tags**
- approach / concept-clarity (skill)

##### Input 8
**Type:** Text

**John:** You also mentioned Data lineage. Why is tracking data movement so important?

**Sharon:** Without it, we don’t know where data came from, how it changed, or who modified it. This creates:

  
❌ Inconsistent reports  
❌ No accountability for errors  
❌ Difficulty in debugging data issues

**John:** How does governance help?

**Sharon:** With governance, we can:  
✅ Track every transformation in the data pipeline  
✅ Identify who made changes and when  
✅ Ensure trust in data by maintaining a full audit trail

**John:** So, if something goes wrong, we can trace it back and fix it quickly?

**Sharon:** Exactly!

**Tags**


##### Input 9
**Type:** Choice

**Question:** Why is Data Lineage important in Data Governance?

**Options:** 
- It speeds up data processing

- It automatically fixes errors in datasets

- It tracks where data comes from and how it's used

- It prevents users from modifying data

**Correct Options:** 
- It tracks where data comes from and how it's used

**Tags**
- access-control-security / role-based-access-control (skill)

##### Input 10
**Type:** Text

**John:** Sharon, we’ve covered Access Control, User Management, and Data Lineage, but what about Data Audit?

**Sharon:** Data Audit tracks who accessed, modified, or shared data, ensuring security and compliance.

**John:** So, it’s like a log of all data activities?

**Sharon:** Exactly! It helps:  
✅ Monitor access and changes  
✅ Detect unauthorized actions  
✅ Ensure compliance with regulations

**John:** So, if someone modifies data incorrectly, we can trace it back?

**Sharon:** Yes! Auditing creates a transparent record, ensuring data integrity and accountability.

**Tags**


##### Input 11
**Type:** Choice

**Question:** Why is Data Audit essential in Data Governance?

**Options:** 
-  It automatically deletes unused datasets

- It removes the need for access control

- It logs and tracks who accessed, modified, or shared data

- It prevents users from seeing data lineage

**Correct Options:** 
- It logs and tracks who accessed, modified, or shared data

**Tags**
- access-control-security / role-based-access-control (skill)

##### Input 12
**Type:** Text

**John:** Lastly, what about data discovery? Why does governance matter there?

**Sharon:** Without governance, analysts struggle to find datasets. They either:  
❌ Waste time searching for the right data  
❌ End up using outdated or duplicate datasets

**John:** How does governance fix that?

**Sharon:** Governance provides:  
✅ A centralized catalog where all datasets are organized and searchable  
✅ Metadata tagging to help users find the most relevant data  
✅ Clear ownership so analysts know who to contact for dataset details

**John:** So, governance makes it easier to find, trust, and use data efficiently?

**Sharon:** Exactly!

**Tags**


##### Input 13
**Type:** Choice

**Question:** What is the main benefit of Data Discovery in a governance model?

**Options:** 
- It allows duplicate datasets to be created

- It makes it easier to find the right datasets while maintaining security

- It restricts access to all datasets

- It automatically generates reports

**Correct Options:** 
- It makes it easier to find the right datasets while maintaining security

**Tags**
- approach / concept-clarity (skill)

##### Input 14
**Type:** Text

**John:** Wow! Governance isn’t just about access—it ensures security, compliance, data integrity, and efficiency.

**Sharon:** That’s right! Organizations risk data leaks, compliance violations, and operational inefficiencies without governance.

**Tags**


### Introduction to Unity Catalog
#### Overview
<p style="text-align:justify;">
This module starts with an introduction to Unity Catalog, Databricks' built-in data governance solution that centralizes access control, auditing, and metadata management across multiple workspaces. 

<p style="text-align:justify;">
It covers the challenges of managing governance in separate workspaces and explains how the Unity Catalog provides a unified governance framework. The module also explores the hierarchical structure of the Unity Catalog and how it ensures fine-grained access control at different levels.

#### Level
intermediate

#### Industries
- general

#### Tags
- batch-etl (skill)
- data-governance (skill)
- access-control-security (skill)
- databricks (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

John, a junior data engineer at GlobalMart, has been learning about data governance and understands its importance in managing data access, security, and compliance. However, he’s unsure how governance can be implemented within Databricks.

While working with different teams, John notices:

*   **Each workspace has separate user management**, leading to inconsistent access control.
*   **Data is duplicated across workspaces**, making it hard to track ownership and usage.
*   **No clear audit trail exists**, making compliance and security monitoring difficult.
*   **Teams struggle to find relevant datasets**, leading to inefficiencies and redundant work.

John wonders, "Is there a way to implement governance directly in Databricks instead of managing everything separately?"

To find out, he reaches out to Sharon, a senior data engineer, to understand how governance can be applied within Databricks effectively.

**Tags**


##### Input 2
**Type:** Text

**John:** Sharon, I understand that governance is important, but how exactly can we implement it in Databricks? Right now, each workspace has its own metastore, user management, and separate policies, which makes everything inconsistent.

**Sharon:** That’s exactly where Unity Catalog comes in! It’s Databricks' built-in governance solution that centralizes access control, auditing, and metadata management across all workspaces.

**John:** So, how does Unity Catalog change governance in Databricks?

**Sharon:** Let me show you a comparison:

📌 **Before Unity Catalog (Without UC)**

*   Each workspace has its own separate metastore.
*   User management is workspace-specific, leading to duplicate efforts and inconsistent permissions.
*   No centralized governance—each workspace follows different security and access policies.

📌 **After Unity Catalog (With UC)**

*   A single, account-level metastore governs all workspaces centrally.
*   User and role management is centralized, eliminating redundancy.
*   Unified access control and security policies ensure consistency across all workspaces.

📌 **Visualizing the Difference**

![Image-image.png](https://cdn.enqurious.com/images/d969c8ff-3ff0-434b-a17e-c571083a00a0_image.webp)

**John:** That makes a lot of sense! So, instead of managing separate meta stores and access policies for each workspace, do we now have a single governance layer at the account level?

**Sharon:** Exactly! With Unity Catalog, governance is scalable, efficient, and secure, ensuring that all workspaces follow the same access control, compliance, and metadata standards.

**Tags**


##### Input 3
**Type:** Choice

**Question:** What is one of the key benefits of Unity Catalog in Databricks?

**Options:** 
- It removes the need for workspaces

- It centralizes access control and metadata management across all workspaces

- It stores all raw data for processing

- It replaces SQL with a new query language

**Correct Options:** 
- It centralizes access control and metadata management across all workspaces

**Tags**
- databricks / unity-catalog / catalog-fully-qualified-name (tool)

##### Input 4
**Type:** Text

>[!NOTE] 
> Unity Catalog is available only in the Premium pricing tier.

**Tags**


##### Input 5
**Type:** Text

**John:** As you mentioned a unified catalog to manage datasets, what does that actually mean? Will we be storing all data in catalogs?

**Sharon:** Yes, but before that, let's discuss the account level. where you manage multiple workspaces, users, and access policies centrally.

**John:** Oh, so the account manages all workspaces centrally?

**Sharon:** Exactly! And within the account, Unity Catalog serves as the metastore, which is responsible for storing metadata (information about tables, schemas, and access policies) and providing governance across all workspaces.

**John:** Instead of setting up governance separately for each workspace, Unity Catalog provides a centralized governance layer.

**Sharon:** Exactly! Unity Catalog follows a structured hierarchy, which you can see in this diagram:

![Image-image.png](https://cdn.enqurious.com/images/fff0c19d-2242-40f7-b979-2836a1709e93_image.webp)

*   **Metastore (Unity Catalog)** → The top-level governance layer that centrally manages metadata for all workspaces.
*   **Catalog** → A logical container that holds multiple schemas (databases).
*   **Schema (Database)** → Organizes datasets by holding tables, views, volumes, and functions.
*   **Tables & Views** → This is where actual data is stored. Fine-grained permissions can be applied at the table, column, or row level to control access.
*   **Volumes & Functions** →Volumes store unstructured data, and functions (including ML models) support advanced data processing.

📌 Here’s how a three-level namespace is used to reference objects in Unity Catalog:  
`catalog.schema.table` → For example, `sales_db.orders.transactions`

**John:** So, Unity Catalog ensures a clear separation between governance layers, making data structured, accessible, and secure?

**Sharon:** Exactly!

**Tags**


##### Input 6
**Type:** Choice

**Question:** What is managed at the account level in Databricks?

**Options:** 
- Only users and permissions

- Only storage resources

- Workspaces, users, and access policies

- Only computational clusters

**Correct Options:** 
- Workspaces, users, and access policies

**Tags**
- databricks / unity-catalog / catalog-securables (tool)

##### Input 7
**Type:** Choice

**Question:** Unity Catalog allows fine-grained access control at which levels?

**Options:** 
- Only at the table level

- Only at the database level

- Table, column, and row levels

- Only at the user level

**Correct Options:** 
- Table, column, and row levels

**Tags**
- databricks / unity-catalog / catalog-securables (tool)

##### Input 8
**Type:** Choice

**Question:** What is the primary role of Unity Catalog as a metastore?

**Options:** 
- To replace data warehouses in Databricks

- To store all datasets instead of using external storage

- To store and manage metadata for all workspaces centrally

- To manage Spark job execution

**Correct Options:** 
- To store and manage metadata for all workspaces centrally

**Tags**
- databricks / unity-catalog / catalog-securables (tool)

##### Input 9
**Type:** Choice

**Question:** What is the correct hierarchical structure of the Unity Catalog?

**Options:** 
- Workspace → Table → Schema

- Schema → Metastore → Table

- Metastore → Catalog → Schema → Table

- Catalog → Table → Database

**Correct Options:** 
- Metastore → Catalog → Schema → Table

**Tags**
- databricks / unity-catalog / catalog-fully-qualified-name (tool)

##### Input 10
**Type:** Choice

**Question:**  How do you reference a table in Unity Catalog’s three-level namespace?

**Options:** 
- workspace.schema.table

- catalog.schema.table

- schema.table.database

- metastore.table.schema

**Correct Options:** 
- catalog.schema.table

**Tags**
- databricks / unity-catalog / catalog-fully-qualified-name (tool)

### Catalog Creation
#### Overview
<p style="text-align:justify;">
This module covers the process of creating a catalog in Unity Catalog, which serves as the top-level container for organizing datasets in Databricks. A catalog allows for centralized data governance, enabling multiple teams to manage and access datasets securely across different workspaces. Learners will explore how to create catalogs using Databricks UI and SQL commands, understand catalog types, and configure storage locations for efficient data management.

#### Level
intermediate

#### Industries
- general

#### Tags
- approach (skill)
- data-storage (skill)
- data-modelling (skill)
- data-governance (skill)
- access-control-security (skill)
- databricks (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

John, a junior data engineer at GlobalMart, has been exploring Unity Catalog and its governance benefits. However, when he tries to organize datasets, he faces challenges:

*   There’s no clear structure for storing different teams' datasets.
*   Data is scattered across workspaces without a unified storage approach.
*   Analysts struggle to find relevant datasets due to inconsistent organization.

John reaches out to Sharon, a senior data engineer, to understand how to properly structure data using Unity Catalog catalogs, schemas, and tables.

**Tags**


##### Input 2
**Type:** Text

**John:** I understand that Unity Catalog helps centralize governance. As far as I know, instead of each workspace managing its own separate governance, all datasets and access controls are managed centrally at the metastore level?

**Sharon:** Hey John! Before we dive into creating catalogs, let’s first understand how the metastore works—it’s the key to enabling collaboration and governance across multiple teams.

Exactly! Let’s take an example:

📌 **Before Unity Catalog (Without a Central Metastore):**

*   The **Marketing** and **Sales** teams operate in **separate workspaces**, each storing their **customer data in its own Hive metastore**, which is **isolated per workspace**.
*   When the **Marketing team** needs **sales transaction data**, they **duplicate it in their workspace**, causing **data inconsistencies**.
*   Additionally, **each team follows different access policies**, making **governance fragmented and difficult to manage**.

📌 **After Unity Catalog (With a Central Metastore):**

*   The **Marketing** and **Sales** teams can access **a shared catalog** from their respective workspaces, as these workspaces are **linked to the same metastore**.
*   This eliminates the need for **data duplication**, allowing datasets to be **securely shared across teams**.
*   **Permissions are enforced at the catalog or schema level**, ensuring **consistent and centralized access control**.

**John:** That’s a big improvement! So, teams still work in their own workspaces, but they access data from one unified governance layer?

**Sharon:** Exactly! Unity Catalog’s metastore ensures a single source of truth, enabling consistent data and seamless collaboration.

**Tags**


##### Input 3
**Type:** Choice

**Question:** John is working with the Marketing and Sales teams, which store their customer data in separate Hive metastores. What problem does this create?

**Options:** 
- Each team follows different access policies, leading to governance complexity.

- Teams have a shared governance model, ensuring data consistency.

- Data is automatically synced between workspaces without duplication.

- Marketing and Sales teams can query data across workspaces without issues.

**Correct Options:** 
- Each team follows different access policies, leading to governance complexity.

**Solution:** 
Without Unity Catalog, each workspace has its own isolated Hive metastore, leading to inconsistent access policies and making governance complex and fragmented.

**Tags**
- databricks / unity-catalog / catalog-privileges-and-permissions (tool)

##### Input 4
**Type:** Text

**John:** Sharon, now that I understand how the metastore works, how do we actually create a catalog in Unity Catalog?

**Sharon:** Great! There are two ways to create a catalog—using the Databricks UI or SQL commands in a notebook or SQL Warehouse. Let’s first see how to create a catalog using the UI.

📌 Method 1: Using Databricks UI
1️⃣ Go to Databricks and open the Catalog (Data Explorer).

- This is where all existing catalogs in your organization are listed.
![Image-image.png](https://cdn.enqurious.com/images/9c3fc238-7618-4dd9-afe6-7855aecc99d7_image.webp)

2️⃣ Click on + then select "Create a catalog".

- This opens the catalog creation window.
![Image-image.png](https://cdn.enqurious.com/images/a3425ed9-daa2-4416-af3e-5943038d3f52_image.webp)

3️⃣ Enter the catalog details.
- **Catalog Name:** Provide a unique name (e.g., sales_db).
- Catalog Type Options in Unity Catalog:
    - **Standard:** Stores tables, views, functions, and other objects in cloud storage.
    - **Foreign:** Mounts and queries external databases like MySQL, PostgreSQL, and SQL Server.
    - **Shared:** Accesses data shared within your organization via Delta Sharing

![Image-image.png](https://cdn.enqurious.com/images/7e1a5d02-b525-46bd-bccc-df70c7b59da7_image.webp)

-  **Storage Location in Unity Catalog:**
    - **Default:** If no location is specified, data is stored in the metastore root location.
    - **External Location:** Allows storing data in cloud storage (ADLS, S3, GCS) for better control and flexibility.

![Image-image.png](https://cdn.enqurious.com/images/b320bb35-1715-4fec-aa38-b8080bf04046_image.webp)


**John:** That looks straightforward! So once I enter these details and click Create, the catalog is ready to use. But if I want to create a catalog using code, is it similar to how we create a schema or database?

**Sharon:** Exactly, John! You just need to run the following command:

```sql
CREATE CATALOG globalmart;
``` 

**Tags**


##### Input 5
**Type:** Choice

**Question:** John needs to create a catalog that will store tables and views directly in Unity Catalog. Which type should he choose?

**Options:** 
- Standard

- Foreign

- Shared

- External

**Correct Options:** 
- Standard

**Tags**
- databricks / unity-catalog / catalog-securables (tool)

##### Input 6
**Type:** Text

**John:** Now that I’ve created a catalog, I guess the next step is to create a schema inside it. I’m familiar with schemas since they are similar to databases, right?

**Sharon:** Exactly, John! A schema (or database) is used to organize tables, views, and other objects within a catalog. Let me show you how to create one.

📌 Creating a Schema Using Databricks UI

- 1️⃣ Open the Catalog (Data Explorer) and select the catalog where you want to create the schema.
- 2️⃣ Click on "+" and choose "Create Schema".
- 3️⃣ Enter a schema name (e.g., globalmart).
- 4️⃣ Click Create, and the schema will be added inside the catalog.

![Image-image.png](https://cdn.enqurious.com/images/33df4c33-0515-439a-9e2c-19a2cc34cadd_image.webp)

![Image-image.png](https://cdn.enqurious.com/images/8136d06e-bbb2-4b1e-87e8-59b2cf4a6969_image.webp)

**John:** That looks simple! I can also use the following command to create a schema:

```sql
CREATE SCHEMA customers;
```

**Sharon:** Yes, but make sure to specify the catalog name before creating the schema. The correct way is:


```sql
CREATE SCHEMA globalmartdb.customers;
```
This ensures the schema is created inside the correct catalog rather than in the default location.

Now that your catalog and schema are set up, you’re ready to store tables within the schema, organizing your datasets efficiently!

          
 
          




**Tags**


##### Input 7
**Type:** Text

John realized that **users from multiple teams can access catalogs across any workspace**, without needing to be **manually added to each workspace** to access the data

**Tags**


##### Input 8
**Type:** Choice

**Question:** John needs to fetch data from the customers table, which is stored inside a catalog in Unity Catalog. Which of the following SQL queries is the correct way to retrieve the data?

**Options:** 
- SELECT * FROM customers;

- SELECT * FROM globalmartdb.customers;

- SELECT * FROM sales.customers;

- SELECT * FROM globalmartdb.sales.customers;

**Correct Options:** 
- SELECT * FROM globalmartdb.sales.customers;

**Tags**
- databricks / unity-catalog / catalog-fully-qualified-name (tool)

### Objects, Roles & Privileges in Unity Catalog
#### Overview
<p style="text-align:justify;">
With Unity Catalog, Databricks introduces a centralized governance model for managing data access, security, and metadata across multiple workspaces. Before Unity Catalog, each workspace had its own Hive Metastore, leading to inconsistent governance, manual user management, and limited cross-workspace data sharing. 

<p style="text-align:justify;">
This module provides a comprehensive understanding of how Unity Catalog simplifies user access, object hierarchy, roles, and privileges, ensuring fine-grained access control at the catalog, schema, and table levels.

#### Level
intermediate

#### Industries
- general

#### Tags
- access-control-security (skill)
- data-governance (skill)
- databricks (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

John has learned that **all catalogs within a metastore can be accessed from any workspace**, ensuring seamless collaboration. However, this raises a **security concern**—

_"If everyone can access every catalog, what prevents unauthorized users from misusing the data? Even though governance is centralized, how do we ensure that only the right users have access to specific datasets?"_

Curious about **how access control works in Unity Catalog**, John reaches out to **Sharon** to understand:

*   **Can access be restricted at the catalog, schema, or table level?**
*   **Are there specific roles that manage access permissions?**

**Tags**


##### Input 2
**Type:** Text

**John:** Sharon, How do we restrict access and ensure only the right users can see or modify datasets?

**Sharon:** Unity Catalog provides fine-grained access control, meaning you can restrict access at different object levels:

✅ **Catalog Level** – Control who can see and access an entire catalog.  
✅ **Schema Level** – Manage access to specific schemas within a catalog.  
✅ **Table Level** – Grant permissions to specific tables or even apply **column-level security**.

**John:** So, instead of giving broad access, we can ensure that **only authorized users** can access certain datasets?

**Sharon:** Exactly!  Users should only have access to **what they need**.

For example:

*   The **Finance team** might need access to the **transactions table** but should **not** see customer **personal details**.
*   The **Marketing team** may need **only aggregated sales data**, not raw transactions.

**John:** That makes sense!

**Tags**


##### Input 3
**Type:** Choice

**Question:** Before Unity Catalog, how were users managed in Databricks workspaces?

**Options:** 
- Users were centrally managed across all workspaces.

- Users were automatically granted access to all catalogs.

- Users had to be manually added to each workspace as there was no centralized management.

- Permissions were inherited across all workspaces without manual intervention.

**Correct Options:** 
- Users had to be manually added to each workspace as there was no centralized management.

**Solution:** 
Before Unity Catalog, Databricks used a Hive Metastore, which had several limitations related to user management and access control:

🔴 Limitations of Hive Metastore (Before Unity Catalog)
1️⃣ Workspace-Specific Metastore → Each Databricks workspace had its own separate Hive Metastore, meaning data governance was isolated per workspace.

2️⃣ No Cross-Workspace Access → Users and tables were tied to a single workspace, making it difficult to share data across teams and workspaces.

3️⃣ Manual User Management → Users had to be manually added to each workspace, and access controls were configured separately per workspace.

4️⃣ No Centralized Governance → Since each workspace had its own metastore, policies, permissions, and audits were not standardized across all workspaces.

🟢 How Unity Catalog Solves This
✅ Single, Account-Level Metastore → Unlike Hive Metastore, Unity Catalog introduces a centralized metastore at the account level.

✅ Cross-Workspace Data Sharing → All workspaces linked to Unity Catalog can access shared catalogs and schemas seamlessly.

✅ Centralized User & Access Management → Users and groups are managed centrally at the account level, eliminating the need for manual workspace-specific user management.

✅ Fine-Grained Access Control → Permissions can now be applied at the catalog, schema, and table level, instead of only at the workspace level.

**Tags**
- access-control-security / role-based-access-control (skill)

##### Input 4
**Type:** Text

**John:** But how do we actually **assign and manage these permissions**?

**Sharon:** We do that using **Roles & Privileges** in Unity Catalog. But before we get into roles, let’s quickly go over the **objects** where permissions are applied—you’re already familiar with

**John:** Right, that makes sense! So how do **roles define access** at each level?

**Sharon:** Roles determine **who can grant what level of access** on these objects. Here’s how it works:

**Databricks Admin Role**

Has **full access** to all objects across all catalogs.

**Catalog Admin Role**

Can manage **all objects within a specific catalog**.

**Schema Admin Role**

Controls **all objects within a schema**.

**Table Admin Role**

Has **access only to specific tables**.

**John:** Got it! Do we have a list of available permissions?

**Sharon:** Yes! We assign permissions by granting the following key **privileges** to roles at different levels:

**SELECT**

Read access to an object.

**MODIFY**

Allows adding, deleting, and modifying data.

**CREATE**

Grants permission to create new objects.

**READ\_METADATA**

Allows viewing object details without access to data.

**USAGE**

Required for any action on a database object.

**ALL PRIVILEGES**

Grants full control.

For example, if we want to **allow analysts to query data but not modify it**, we grant them the **SELECT** privilege on specific tables.

**John:** That’s great! So by assigning the right roles with the right privileges, we can ensure secure and controlled access across the Unity Catalog.

**Sharon:** Exactly!

**Tags**


##### Input 5
**Type:** Choice

**Question:** Which of the following sections in the UI can be used to manage permissions and grants to tables?

**Options:** 
- User Settings

- Admin UI

- Workspace admin settings

- User access control lists

- Data Explorer(Catalog)

**Correct Options:** 
- Data Explorer(Catalog)

**Tags**
- databricks / unity-catalog / catalog-securables (tool)

##### Input 6
**Type:** Text

**John:** Now, can you show me how to assign these permissions using the UI?

**Sharon:** Sure! Let me walk you through it. This is where you can view the permissions that have already been granted for a particular object, such as the customer's table under a catalog.

![Image-image.png](https://cdn.enqurious.com/images/ec0da6b2-f388-4e16-89fe-695a8bf30c2a_image.webp)

**John:** Oh, if I want to permit a user, do I need to click on Grant?

**Sharon:** Exactly! Once you click Grant, you’ll see an interface where you can assign new privileges. Let me take another example—here, I’ve opened the Permissions page for the globalmartdb schema.

📌 Granting Permissions on a Schema:
- 1️⃣ Click Grant in the Permissions tab of the schema.
- 2️⃣ Select the Principal (User, Group, or Service Account). For example, add a Data Analyst as the principal to assign specific permissions.
- 3️⃣ Choose the appropriate privileges:

    - Use Schema → Required for accessing objects inside the schema.
    - SELECT → Grants read access to tables within the schema.
    - CREATE TABLE → Allows users to create tables in the schema.

- 4️⃣ Click Grant to apply for permissions.

![Image-image.png](https://cdn.enqurious.com/images/36ccd1d2-d9d2-4e09-8388-ba6a0bcd5f11_image.webp)

**John:** Oh, that’s great! So if a Data Analyst needs to read data from this schema, we first add them as a Principal, then grant them Use Schema and SELECT permissions. If they also need to create tables, we check Create Table too.

**Sharon:** Exactly!

**John:** That means the Data Analyst won’t be able to modify, insert, or delete any data unless explicitly granted additional permissions, right?

**Sharon:** Spot on! If you also provide Modify permission, then they’ll be able to insert, update, or delete data in the tables they create within this schema. Without it, they can only read or create tables but not modify any data.

**John:** That’s a huge security advantage! With fine-grained access control, we can restrict permissions based on user roles while maintaining flexibility.

**Sharon:** Exactly! If you need to remove access, simply click on Revoke to remove the Data Analyst's permissions. You can also refer to the official documentation to explore the complete list of available privileges.

**John:** Sure, Sharon! I’ll check that out.

**Tags**


##### Input 7
**Type:** Choice

**Question:** Which of the following is NOT a valid privilege in Unity Catalog?

**Options:** 
- SELECT

- MODIFY

- DELETE

- CREATE TABLE

- EXECUTE

**Correct Options:** 
- DELETE

**Tags**
- databricks / unity-catalog / catalog-privileges-and-permissions (tool)

##### Input 8
**Type:** Text

**John:** Can you show me how to grant permissions using code in a notebook?

**Sharon:** Sure! Here’s the general syntax for granting permissions:

    GRANT <privilege-type> ON <securable-type> <securable-name> TO <principal>

For example, if we want to allow an Analyst Group to query the `customers` table without modifying any data, we can grant access at the group level instead of assigning permissions to individual users.

Using **SQL commands**, we grant **SELECT** privileges like this:

    GRANT SELECT ON TABLE test_catalog.globalmartdb.customers TO `analyst_group`;
    

Now, all users in the `analyst_group` can read the data but cannot modify it. Granting permissions at the group level ensures consistent access control while reducing the need for manual user assignments.

**John:** That’s smart! Managing access via groups makes team-wide permissions much easier to handle. If I need to **remove access**, would this be the correct syntax?

    REVOKE CREATE TABLE ON TABLE test_catalog.globalmartdb.customers TO `analyst_group`;

Sharon: Yes, that's correct! This revokes the `CREATE TABLE` privilege from the `analyst_group`, ensuring they can no longer create tables within the `customers` schema.

**Tags**


##### Input 9
**Type:** Choice

**Question:** A new Data Analytics team has been assigned to a customer insights project. They need full privileges on the transactions table to manage and analyze the data.

Which of the following commands can be used to grant full permissions on the table to the new Data Analytics team?

**Options:** 
- GRANT ALL PRIVILEGES ON TABLE transactions TO GROUP analytics_team;

- GRANT SELECT, CREATE, MODIFY ON TABLE transactions TO GROUP analytics_team;

- GRANT SELECT ON TABLE transactions TO GROUP analytics_team;

- GRANT USAGE ON TABLE transactions TO GROUP analytics_team;

- GRANT ALL PRIVILEGES ON TABLE analytics_team TO transactions;

**Correct Options:** 
- GRANT ALL PRIVILEGES ON TABLE transactions TO GROUP analytics_team;

**Tags**
- databricks / unity-catalog / catalog-privileges-and-permissions (tool)

##### Input 10
**Type:** Choice

**Question:** A new user, John, who currently has no access to the catalog or schema, has requested access to the customer table within the sales schema. Since the table contains sensitive information, a view was created excluding sensitive columns, and access was granted using:

        GRANT SELECT ON view_name TO 'john@company.com';

However, when John tries to query the view, he encounters an error:
- "View does not exist."

What could be causing this issue, and how can it be resolved?

**Options:** 
- John needs ADMIN privileges on the view.

- John requires SELECT privileges on the underlying table of the view.

- John needs to be added to a special group that has access to PII data.

- John must be the owner of the view.

- John requires USAGE privilege on the sales schema.

**Correct Options:** 
- John requires USAGE privilege on the sales schema.

**Solution:** 
Even though John has SELECT permission on the view, he still needs USAGE privilege on the schema (sales) to access objects inside it.

📌 USAGE privilege allows a user to "see" objects within a schema but does not grant data access.

💡 Solution: Grant John USAGE on the sales schema:

    GRANT USAGE ON SCHEMA sales TO 'john@company.com';

Now, John can successfully query the view!

**Tags**
- databricks / unity-catalog / catalog-privileges-and-permissions (tool)

