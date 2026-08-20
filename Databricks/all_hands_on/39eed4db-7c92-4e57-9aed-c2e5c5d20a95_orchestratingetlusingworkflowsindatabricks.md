# Orchestrating ETL using Workflows in Databricks
## Content Type
Masterclass

## Overview
<p style="text-align:justify;">
This module introduces you to orchestration using Databricks Workflows. You will learn how to build and automate end-to-end pipelines by configuring tasks, dependencies, and advanced settings. The module also covers monitoring, debugging, and optimizing workflows for efficient resource utilization. Hands-on examples will guide you in implementing workflow best practices.
<p style="text-align:justify;">

## Learning Objectives
- Understand the purpose of orchestrating workflows in Databricks.
- Configure tasks and dependencies in Databricks Workflows.

## Prerequisites
- Understanding of data processing concepts and ETL pipelines.
- Basic knowledge of clusters, including the difference between Job Clusters and All-Purpose Clusters

## Duration of Completion
50 minutes

## Level
Intermediate

## Industries
- e-commerce

## Tags
- batch-etl (skill)
- approach (skill)
- databricks (tool)

## Scenarios
### Introduction to Workflows in Databricks
#### Overview
<p style="text-align:justify;">
This module introduces you to orchestration using Databricks Workflows. You will learn how to build and automate end-to-end pipelines by configuring tasks, dependencies, and advanced settings. The module also covers monitoring, debugging, and optimizing workflows for efficient resource utilization. Hands-on examples will guide you in implementing workflow best practices.

#### Level
intermediate

#### Industries
- e-commerce

#### Tags
- batch-etl (skill)
- approach (skill)
- databricks (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

John, a Data Engineer at GlobalMart, is responsible for managing multiple Databricks jobs for tasks such as data ingestion and data cleaning. Recently, he’s been asked to automate these tasks, and given the number of jobs involved, he realizes that **manually scheduling or triggering each job isn’t practical.**

_**For example,**_ if new data arrives every day at noon, he might not always be available to initiate the process manually. This need for reliable automation prompts him to explore Databricks' scheduling options to orchestrate the pipeline effectively.

  
With these questions in mind, John reaches out to Sharon for guidance on setting up a more reliable and comprehensive automation process in Databricks.

**Tags**


##### Input 2
**Type:** Text

**John:** Hey Sharon! While exploring, I noticed the “Schedule” option (as shown in the image). Does this feature handle automation? Can we set up a notebook to run automatically at a specific time?

![Image-image.png](https://cdn.enqurious.com/images/5ce19266-a10f-4c5e-a838-a9328784868f_image.webp)

**Sharon:** Exactly, John! With the "Schedule" option, you can set this notebook to run at any time you choose. For instance, if you need to pull data every day at 3 am, you can configure it to run automatically, so you don’t have to start it manually.

**John:** That’s really useful! Can you explain a bit more about how it works?

**Sharon:** Absolutely! Here’s a video that guides you through the process of scheduling notebooks in Databricks.

**Tags**


##### Input 3
**Type:** Video

**Video:**
![notebookschedulingpart.mp4](https://cdn.enqurious.com/videos/d759133c-1d24-44b3-8027-6d290e481dc6_notebookschedulingpart.mp4)

**Tags**
- databricks / clusters / job-purpose (tool)

##### Input 4
**Type:** Choice

**Question:** If a notebook is scheduled to pull data from a source every day at noon, what is the advantage of this setup?

**Options:** 
- It prevents other notebooks from running

- It allows data ingestion to happen automatically without manual intervention

- It eliminates the need for data validation

- It ensures that only a single user can access the notebook

**Correct Options:** 
- It allows data ingestion to happen automatically without manual intervention

**Tags**
- databricks / workflows (tool)

##### Input 5
**Type:** Text

After learning how to schedule individual notebooks, John has been tasked with automating a data pipeline in Databricks that includes two notebooks:

*   **Notebook 1**: Handles data ingestion and is scheduled to run daily at 12:30 p.m., typically taking about 10 minutes to complete.
*   **Notebook 2**: Performs basic transformations on the ingested data and is scheduled to run at 12:45 p.m., with a 5-minute buffer.

One day, however, Notebook 1 took longer than expected and wasn’t complete until 12:50 p.m. Since Notebook 2 was scheduled to start at 12:45 p.m., it began running before Notebook 1 had finished. As a result, Notebook 2 failed due to missing data, as the ingestion process in Notebook 1 was still incomplete.

John realizes a key issue:

*   **Lack of Dependency Management**: There’s no setup to ensure Notebook 2 waits for Notebook 1 to finish, leading to failures if delays occur.
*   **No Error Handling**: Without error handling, if one notebook fails or takes longer, it disrupts downstream tasks.

Seeking a solution to coordinate these tasks effectively, John reaches out to Sharon for guidance on managing dependencies and implementing error handling for a more reliable workflow.

**Tags**


##### Input 6
**Type:** Choice

**Question:** In John’s current setup, why did Notebook 2 fail when scheduled to start at 12:45 p.m.?

**Options:** 
- Notebook 1 did not generate any data that day.

- Notebook 2 was scheduled to run before Notebook 1 was completed, leading to missing data for transformations.

- Notebook 1 was scheduled incorrectly.

- Notebook 2 encountered an internal error unrelated to Notebook 1.

**Correct Options:** 
- Notebook 2 was scheduled to run before Notebook 1 was completed, leading to missing data for transformations.

**Tags**
- databricks / workflows (tool)

##### Input 7
**Type:** Choice

**Question:** Why is manual scheduling of each notebook in John’s pipeline a challenge? 

**Options:** 
- It requires a lot of coding

- It can cause issues if one notebook takes longer than expected, disrupting the flow

- It automatically handles dependencies

- It prevents errors from occurring

**Correct Options:** 
- It can cause issues if one notebook takes longer than expected, disrupting the flow

**Tags**
- databricks / clusters / job-purpose (tool)

##### Input 8
**Type:** Text

**John:** Hey Sharon! Manually scheduling each notebook doesn’t seem like the best way to keep everything in sync. Is there a better way to streamline the process?

**Sharon**: Great observations, John! All these issues—dependencies, error handling, and coordinating schedules—are part of **orchestration**.

**John**: I thought orchestration was just about automating tasks at a scheduled time.

**Sharon**: It does automate tasks, but it’s much more than that. Orchestration also allows you to monitor the entire pipeline, send notifications if there’s an error, and confirm when tasks run successfully.

**John**: That sounds helpful! So, it would give me a complete view of the pipeline and alert me if something goes wrong.

**Sharon**: Exactly! In Databricks, we use **Workflows** to enable these orchestration capabilities.

**John**: Workflows? Isn’t that what we used to schedule a single notebook?

**Sharon**: Yes, but Workflows can also orchestrate an entire pipeline. You can create, schedule, and monitor multiple tasks in one place, making managing complex dependencies much easier and keeping everything running smoothly.

**John**: Perfect! Workflows sound like the ideal solution for this. Thanks, Sharon!

**Tags**


##### Input 9
**Type:** Choice

**Question:** What is the main benefit of using orchestration in Databricks Workflows for managing multiple notebooks?

**Options:** 
- It allows individual scheduling for each notebook

- It is used only for running single notebooks

- It focuses solely on scheduling notebooks at a specific time

- It automates and monitors the entire pipeline, managing dependencies and sending notifications for errors or successful runs

**Correct Options:** 
- It automates and monitors the entire pipeline, managing dependencies and sending notifications for errors or successful runs

**Tags**
- databricks / workflows (tool)

##### Input 10
**Type:** Choice

**Question:** Which feature in Databricks provides orchestration capabilities for managing dependencies, scheduling, and monitoring data pipelines?

**Options:** 
- Databricks Jobs

- Databricks Notebooks

- Databricks Workflows

- Databricks Clusters

**Correct Options:** 
- Databricks Workflows

**Tags**
- databricks / workflows (tool)

##### Input 11
**Type:** Short Answer

**Question:** Which type of cluster is preferable for scheduling a job, and why?

**Template:** null

**Tags**
- databricks / clusters / job-purpose (tool)

##### Input 12
**Type:** Text

**John:** So, Sharon, I understand that Workflows can help schedule notebooks. But what if I want to use something other than a notebook, like a Python script? Can I still use Workflows for that?

**Sharon:** Absolutely, John! Workflows aren’t limited to notebooks. You can schedule and orchestrate Python scripts, JAR files, and even SQL queries. Workflows allow you to automate various tasks within the pipeline, not just notebooks.

![Image-workflowstype.gif](https://cdn.enqurious.com/images/8cb80aab-dd18-404c-b4ac-f900a229d4bc_workflowstype.gif)

**John:** That’s great! So, it’s a more versatile tool than I thought. Could you walk me through the main options and parameters?

**Sharon:** Sure! The below quick clips will give you a visual guide to setting up tasks in your workflow.

**Tags**


##### Input 13
**Type:** Choice

**Question:** What types of tasks can you schedule in Databricks Workflows?

**Options:** 
- Only Notebooks

- Python scripts, JAR files, Notebooks, SQL queries

- Only SQL queries

- Only Python scripts

**Correct Options:** 
- Python scripts, JAR files, Notebooks, SQL queries

**Tags**
- approach / concept-clarity (skill)

##### Input 14
**Type:** Text

Here’s what each GIF will show:

- **Task Name:** Clearly label each task to know its function in the pipeline.
        
![Image-workflowtaskname.gif](https://cdn.enqurious.com/images/b7fc0801-d21f-48ae-bbdc-e33bcb3d8bc1_workflowtaskname.gif)

- **Source:** Selecting the location of your notebook
![Image-image.png](https://cdn.enqurious.com/images/c600f52a-35c8-46d9-929e-96d6df141e9f_image.webp)
 
- **Path:** Setting the file path for your task (e.g., selecting a notebook or script from the workspace).
 
          
![Image-workflowspath.gif](https://cdn.enqurious.com/images/b215ff69-e3fc-4d49-9002-38e649a193f4_workflowspath.gif)

- **Cluster:** Cluster: Job Clusters are cost-effective as they start and stop automatically with the task, unlike all-purpose clusters that remain active. You can also assign different clusters to each task for better resource management and performance.
 
          
![Image-workflowscluster.gif](https://cdn.enqurious.com/images/f12b3562-2dd4-43a7-9e14-3bb6d0b2f89d_workflowscluster.gif)

 - **Dependent Libraries:** This section allows you to add any required libraries that the job might need, such as specific Python or Scala libraries, ensuring all dependencies are available during execution. 
          
![Image-image.png](https://cdn.enqurious.com/images/2fb27658-9db4-465f-95fe-fd87e43fb68f_image.webp)

- **Parameters:** Parameters allow you to set input values for each job run, like file paths or dates, making the job more flexible. By using parameters (e.g., file_path), you can change data sources without modifying the code, enhancing automation and reducing errors.

 
          
![Image-image.png](https://cdn.enqurious.com/images/11ca2fe1-ca1c-4dc4-aef5-4b172c8b6695_image.webp)

**Tags**


##### Input 15
**Type:** Choice

**Question:** Which statement is true about Job Clusters in a Databricks pipeline?

**Options:** 
- They remain active continuously, similar to all-purpose clusters.

- They stop automatically after the task is completed, making them cost-effective.

- You cannot assign different clusters for individual tasks.

-  They do not support dependent libraries during execution.

**Correct Options:** 
- You cannot assign different clusters for individual tasks.

**Tags**
- databricks / clusters / job-purpose (tool)

##### Input 16
**Type:** Text

**John:**  Hey Sharon! I noticed options for notifications and retries while setting up the job, but I’m not sure how to use them. Could you explain?

**Sharon:** Sure, John! Notifications are essential for keeping you updated on your job's status. For instance, you can set it to send an email or Slack message if a job fails, completes, or encounters any issues. It’s a great way to stay informed without constantly checking.

**John:** Got it! So, it’ll alert me when something goes wrong.

**Sharon:** Here is the small clip of it

- **Notifications:**
          
![Image-workflowsnotifications_1.gif](https://cdn.enqurious.com/images/36885acd-c1cf-455d-907d-c55a798259bb_workflowsnotifications_1.gif)

**Tags**


##### Input 17
**Type:** Choice

**Question:** John is setting up a data pipeline in Databricks and wants to be notified immediately if a job fails or completes successfully, so he doesn’t have to constantly monitor the workflow. Which feature should he use to achieve this?

**Options:** 
- Set up retries in case of failure

- Use the "Run Now" option to monitor tasks manually

- Configure job clusters to automatically stop after execution

- Enable notifications to receive alerts about the job’s status

**Correct Options:** 
- Enable notifications to receive alerts about the job’s status

**Tags**
- databricks / workflows (tool)

##### Input 18
**Type:** Text

**Sharon:**  Regarding retries, you have two jobs in your pipeline. The first job is resource-heavy, so it needs a lot of processing power. Until it’s done, the second job can’t start because it needs those same resources.

**John:** Right, so the second job should wait for the first to finish.

**Sharon:** Exactly. That’s where retries come in. If the first job runs into a temporary issue, it doesn’t just fail immediately. Instead, it pauses, waits for a bit, then tries again. This gives the job multiple chances to finish before moving on.

In this clip, you can see how we set the number of retries and the waiting time between each attempt. This way, it won’t give up on the first try.

![Image-workflowsretriesmech.gif](https://cdn.enqurious.com/images/7dd2797d-327d-4b62-a32f-364f246b7873_workflowsretriesmech.gif)


**John:** Got it! So, retries give the first job time to complete, freeing up resources for the next one and keeping the pipeline moving smoothly.

**Sharon:** Exactly, John. It’s a helpful way to handle temporary issues without disrupting the whole pipeline. This is the solution for your error-handling problem

**Tags**


##### Input 19
**Type:** Choice

**Question:** John has two jobs in his pipeline. The first job is resource-intensive, and the second depends on completion. What should John configure to ensure the first job has multiple chances to finish in case of temporary issues?

**Options:** 
- Notifications for job failure

- Retries with a wait time between attempts

- Maximum concurrent runs

- Job clusters for each task

**Correct Options:** 
- Retries with a wait time between attempts

**Tags**
- databricks / workflows (tool)

##### Input 20
**Type:** Text

**John:** Sharon, what happens if a task keeps running for a very long time and still fails even after multiple retries? How can we identify and handle such situations?

**Sharon:** That’s a great question, John! This brings us to the concept of a Duration Threshold, which helps manage tasks that exceed their expected runtime.

**John:** Oh, interesting! Can we configure it to automatically stop a task if it takes too long?

**Sharon:** Absolutely! For example, if we set a threshold of 15 minutes and the first task (data ingestion) fails to establish a connection with the data lake within that time, the workflow will automatically terminate the task to avoid further delays.

You can configure a maximum time threshold, such as 15 minutes, in the **Timeout** field to automatically stop the task if it exceeds the specified duration.
         
![Image-image.png](https://cdn.enqurious.com/images/b7972cb3-cf4f-4190-b121-abd1b6e8e09d_image.webp)

**John:** Got it! I also noticed a Warning field. Does that mean it will notify us if the job takes too long or fails?

**Sharon:** Exactly, John! In the Duration field, you can set the expected completion time for the task. If the task takes longer than expected, it will trigger an alert to notify you.

**John:** Oh, I see! That’s really helpful!

**Tags**


##### Input 21
**Type:** Choice

**Question:** John wants to configure his pipeline to handle tasks that exceed their expected runtime. He also wants to be notified if a task takes longer than expected. Which settings should he configure?

**Options:** 
- Retries to reattempt failed tasks and Duration to limit task runtime.

- Notifications to send alerts and Retries to manage failures.

- Timeout to set a maximum runtime and Warning to trigger notifications.

- Warning to set runtime limits and Timeout to send notifications.

**Correct Options:** 
- Timeout to set a maximum runtime and Warning to trigger notifications.

**Tags**
- databricks / workflows (tool)

##### Input 22
**Type:** Text

After configuring the first task for data ingestion in Workflows, John began adding the second task. While doing so, he noticed a field labeled **"Depends On"** (as shown below) and wondered if it could be used to set dependencies, ensuring the second task would only execute after the first task was successfully completed.

![Image-image.png](https://cdn.enqurious.com/images/036be775-bb08-4364-b79b-fde4b4e3b97c_image.webp)

To clarify, John reached out to Sharon for guidance on how this field works and how to use it to configure dependencies.

**Tags**


##### Input 23
**Type:** Text

**John:** Hey Sharon, can we use the Depends On field to set a dependency between tasks?

**Sharon:** Yes, exactly! In the image you shared, the "Depends On" field allows you to set dependencies between notebooks. For example, if you select the data-ingestion task from the dropdown, it ensures that the data-cleaning notebook will only start after the data-ingestion notebook is complete.

**John:** Oh, I see. Let me give this a try.

![Image-image.png](https://cdn.enqurious.com/images/38dce58e-be9e-4755-af1f-983b57f1997d_image.webp)

**John:** Will it look like this?

**Sharon:** Perfect! Once you set it, the data-cleaning notebook becomes dependent on the data-ingestion notebook.

**John:** So, if I don’t set the dependency, will the tasks run parallel?

**Sharon:** Correct! Without a dependency, data-ingestion and data-cleaning will run in parallel, but this can cause issues since data-cleaning depends on the output of data-ingestion, leading to errors or incomplete processing.

**John:** Got it, that makes perfect sense now.

**Tags**


##### Input 24
**Type:** Choice

**Question:** John wants to ensure that a data-cleaning task only starts after a data-ingestion task is completed. Which feature should he configure in Databricks?

**Options:** 
- Notifications

- Depends On field

- Duration Threshold

- Maximum concurrent runs

**Correct Options:** 
- Depends On field

**Tags**
- databricks / workflows (tool)

##### Input 25
**Type:** Choice

**Question:** What happens if John does not set a dependency between data-ingestion and data-cleaning tasks?

**Options:** 
- The tasks will run in parallel, potentially causing issues if data-cleaning starts before data-ingestion finishes.

- The tasks will not run.

- The tasks will run sequentially.

- The data-ingestion task will fail automatically.

**Correct Options:** 
- The tasks will run in parallel, potentially causing issues if data-cleaning starts before data-ingestion finishes.

**Tags**
- databricks / workflows (tool)

##### Input 26
**Type:** Text

**John:** Hey Sharon, I have a question. Suppose I have two ingestion tasks—Data Ingestion from the Data Lake and Data Ingestion from the Database—and a third task, Data Cleaning, which depends on both. How can I ensure the third task runs only after both ingestion tasks are successfully completed?

**Sharon:** That’s a great question, John! The **Run if dependencies** field allows you to set such conditions.

![Image-image.png](https://cdn.enqurious.com/images/6073e2aa-61a1-4fb8-82fa-ebae6e74e8aa_image.webp)

**John:** Oh, so I can use the **All succeeded** option to ensure that Data Cleaning only runs when both ingestion tasks are completed successfully?

**Sharon:** Exactly! The third task will wait until both ingestion tasks finish successfully before starting.

**Tags**


##### Input 27
**Type:** Choice

**Question:** John wants to ensure that the Data Cleaning task only starts after both Data Ingestion from Data Lake and Data Ingestion from Database tasks are successfully completed. Which dependency should he use?

**Options:** 
- None failed

- At least one succeeded

- All succeeded

- All done

**Correct Options:** 
- All succeeded

**Tags**
- databricks / workflows (tool)

##### Input 28
**Type:** Text

**John:** By looking at the **"At least one succeeded"** dependency, it seems that the Data Cleaning task will run as long as either the Data Ingestion from the Data Lake or Data Ingestion from the Database task is successful. Is that correct?

**Sharon:** Yes, that’s correct. The Data Cleaning task will proceed if at least one of the ingestion tasks is successfully completed.

**John:** What’s a practical scenario for this?

**Sharon:** It’s useful when partial data is enough to move forward. For instance, if the database ingestion is delayed, you can start cleaning the data from the data lake while waiting for the database task to finish. This avoids unnecessary workflow delays.

**John:** Got it! Let me try adding these tasks, and this is how it looks:

![Image-image.png](https://cdn.enqurious.com/images/5bbedd9d-a22f-4382-9d5d-e29add55f552_image.webp)

**Tags**


##### Input 29
**Type:** Choice

**Question:** If John wants the Data Cleaning task to proceed as long as either Data Ingestion from Data Lake or Data Ingestion from Database is successful, which dependency should he choose?

**Options:** 
- At least one succeeded

- All succeeded

- None failed

- All failed

**Correct Options:** 
- At least one succeeded

**Tags**
- databricks / workflows (tool)

##### Input 30
**Type:** Text

**John:** Sharon, I see another dependency option called "None failed." I’m a bit confused. With "All succeeded," both tasks must be completed successfully, but with "None failed," it seems like any task can succeed as long as none fails. Is there a difference?

**Sharon:** Good question, John. "None failed" ensures that the next task, like Data Cleaning, will run as long as none of its dependencies fail. For example, if neither Data Ingestion from Data Lake nor Data Ingestion from the Database fails, Data Cleaning will proceed, even if one of them hasn’t been completed successfully.

**John:** Oh, so it’s less strict than "All succeeded" but still ensures there are no critical failures?

**Sharon:** Exactly. It’s useful when you want to avoid running tasks if there are errors, but you don’t need every dependency to complete successfully.

**Tags**


##### Input 31
**Type:** Choice

**Question:** Which dependency ensures that the Data Cleaning task will run as long as none of its dependencies fail, even if one hasn’t completed successfully?

**Options:** 
- At least one succeeded

- None failed

- All done

- At least one failed

**Correct Options:** 
- None failed

**Tags**
- databricks / workflows (tool)

##### Input 32
**Type:** Text

**John:** I’m a bit confused between "All succeeded" and "All done." What’s the difference? 

**Sharon:** "All succeeded" means the next task will only run if all the previous tasks are completed successfully without any errors. On the other hand, "All done" means the next task will run once all previous tasks are finished, whether they succeeded or failed. 

**John:** Oh, so "All succeeded" ensures there are no errors, but "All done" doesn’t care about the success or failure of the tasks?

**Sharon:** For "All done," it’s for tasks like logging or notifications that run regardless of success or failure. For example, a **report generation task** can summarize all completed ingestion tasks, even if one or more failed, ensuring you always get a workflow status update.

**Tags**


##### Input 33
**Type:** Choice

**Question:** John wants to set up a Report Generation task that runs after Data Ingestion from Data Lake and Data Ingestion from Database tasks are completed, regardless of whether they succeeded or failed. Which dependency should he choose? 

**Options:** 
- All succeeded

- All failed

- At least one succeeded

- All done

**Correct Options:** 
- All done

**Tags**
- databricks / workflows (tool)

##### Input 34
**Type:** Text

**John:** Talking about the next dependency, “At least one failed,” does it mean the next task will run if any of the tasks fail?

**Sharon:** Exactly! The use case for this is when you want to handle errors proactively. For example, if either Data Ingestion from Data Lake or Data Ingestion from the Database fails, you could trigger an alert task to notify the team about the failure, allowing you to address the issue immediately.

**John:** Okay, got it. Now, talking about the last dependency, “All Failed,” what's the importance of this dependency?

**Sharon:** "All Failed" is used when you want to trigger a specific recovery or fallback process only if all dependencies fail. For example, if both Data Ingestion from Data Lake and Data Ingestion from the Database fail, you could run a fallback ingestion task to load data from a backup source or a retry mechanism. This ensures your workflow doesn’t stop entirely and has a contingency plan for complete failures.

**John:** Oh, I see! So, it's for critical recovery actions when everything else goes wrong.

**Sharon:** Exactly, John. It’s a safety net to keep your workflow resilient in worst-case scenarios.

**Tags**


##### Input 35
**Type:** Choice

**Question:** Which dependency should John use to trigger a Fallback Task if both Data Ingestion from the Data Lake and Data Ingestion from the Database fail? 

**Options:** 
- At least one failed

- All succeeded

- All failed

- None failed

**Correct Options:** 
- All failed

**Tags**
- databricks / workflows (tool)

##### Input 36
**Type:** Choice

**Question:** If John wants to trigger an Alert Task when either Data Ingestion from Data Lake or Data Ingestion from Database fails, which dependency should he select?

**Options:** 
- All succeeded

- At least one failed

- None failed

- All done

**Correct Options:** 
- At least one failed

**Tags**
- databricks / workflows (tool)

##### Input 37
**Type:** Text

**John:** Alright, I now understand these parameters for tasks. But how can I schedule the pipeline to run every day at 10 am?

**Sharon:** You can always run the job manually by clicking on Run Now as shown below. 

![Image-image.png](https://cdn.enqurious.com/images/438e159e-e859-4183-9e83-a17e73132385_image.webp)


**Sharon:** However, let me share a short clip that explains how to set up a schedule to automate it for 10 am daily.

![Image-howtoschedule.gif](https://cdn.enqurious.com/images/43372b1d-d9a3-457d-adbe-442828a1b352_howtoschedule.gif)

**John:** Got it, thanks! I also noticed some parameters for the entire job—do those apply to the whole pipeline?

**Sharon:** Exactly, John. These parameters include details such as the selected cluster, notifications, alerts for warnings, and timeout settings for the entire job. These are similar to what we configured for individual tasks but apply to the job as a whole. You can also customize job parameters to fit the workflow’s requirements.

Here’s a short clip showcasing all these functionalities.

![Image-jobparameters.gif](https://cdn.enqurious.com/images/2a93a008-ba45-42b4-b1a0-980d16a13f02_jobparameters.gif)

**Tags**


##### Input 38
**Type:** Choice

**Question:** John wants to schedule his pipeline to run every day at 10 am without manually triggering it. What should he configure?

**Options:** 
- Set the Timeout field for individual tasks to 10 am.

- Use the Run Now button daily at 10 am.

- Set up a schedule in the pipeline's job settings for 10 am daily.

- Enable notifications to remind him to run the pipeline manually at 10 am.

**Correct Options:** 
- Set up a schedule in the pipeline's job settings for 10 am daily.

**Tags**
- databricks / workflows (tool)

##### Input 39
**Type:** Text

**John:** I noticed these options in the advanced settings. Do they control how many jobs run at the same time?

![Image-image.png](https://cdn.enqurious.com/images/5f3bb570-0831-498c-b9a2-8665dd70c5fb_image.webp)

**Sharon:** Yes, John! The Maximum concurrent runs limit how many instances of the job can run simultaneously. For example, if set to 1, only one run will process at a time.

**John:** What about the Queue option?

Sharon: If the maximum is reached, the Queue will hold new runs until the current one finishes. For example, if a Data Cleaning job is already running, the next run will wait instead of starting immediately.

**John:** Got it! So, it helps manage resources and avoid overloads.

**Sharon:** Exactly!

**Tags**


##### Input 40
**Type:** Choice

**Question:** If John sets the Maximum concurrent runs to 1 and enables the Queue option, what happens when multiple instances of a job are triggered?

**Options:** 
- The additional runs fail immediately.

- The additional runs are queued and wait for the current one to finish.

- The additional runs start immediately, causing resource contention.

- Only the first run is processed, and the rest are ignored.

**Correct Options:** 
- The additional runs are queued and wait for the current one to finish.

**Tags**
- databricks / workflows (tool)

