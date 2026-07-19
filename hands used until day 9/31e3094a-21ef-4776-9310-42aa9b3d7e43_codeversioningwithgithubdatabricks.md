# Code Versioning with Github & Databricks
## Content Type
Scenario

## Overview
<p style="text-align:justify;">
This module introduces the fundamentals of Git integration with Databricks, enabling seamless collaboration, version control, and efficient project management. It covers essential Git operations such as creating repositories, committing changes, pushing and pulling updates, branching, resolving merge conflicts, and managing pull requests within Databricks.

<p style="text-align:justify;">
By the end of this module, learners will understand how to leverage Git workflows inside Databricks, avoid common challenges like merge conflicts, and apply best practices for collaborative development using branches and pull requests. This knowledge will help teams work efficiently without overwriting each other’s work, ensuring code integrity and streamlined project management.

## Learning Objectives
-  Set up and integrate Git with Databricks for effective version control.
-  Understand and apply Git workflows such as commit, push, and pull operations within Databricks.
- Create and manage pull requests (PRs) to review and merge changes into the main branch.

## Prerequisites
- Basic understanding of Git and version control concepts
-  Familiarity with Databricks and its workspace navigation.

## Duration of Completion
30 minutes

## Level
Intermediate

## Industries
- general

## Tags
- approach (skill)
- code-versioning (skill)
- batch-etl (skill)
- databricks (tool)

#### Overview
<p style="text-align:justify;">
This module introduces the fundamentals of Git integration with Databricks, enabling seamless collaboration, version control, and efficient project management. It covers essential Git operations such as creating repositories, committing changes, pushing and pulling updates, branching, resolving merge conflicts, and managing pull requests within Databricks.

<p style="text-align:justify;">
By the end of this module, learners will understand how to leverage Git workflows inside Databricks, avoid common challenges like merge conflicts, and apply best practices for collaborative development using branches and pull requests. This knowledge will help teams work efficiently without overwriting each other’s work, ensuring code integrity and streamlined project management.

#### Level
intermediate

#### Industries
- general

#### Tags
- approach (skill)
- code-versioning (skill)
- batch-etl (skill)
- databricks (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

In a collaborative environment, multiple users work on the same **Databricks notebooks**, leading to frequent updates and version changes. But what happens when someone **accidentally introduces a bug or overwrites important code**? Without proper version control, reverting to a stable version becomes challenging.

John, a data engineer, realizes the need for **version control** and knows tools like **GitHub** can help. However, he's unsure **how to integrate GitHub with Databricks**. He reaches out to Sharon to understand:

*   **Which version control tool works best with Databricks?**
*   **How to connect Databricks notebooks to GitHub?**
*   **How to track changes and restore previous versions efficiently?**

This sets the stage for exploring **Databricks-GitHub integration** for seamless code management.

**Tags**


##### Input 2
**Type:** Text

**John:** Sharon, After deciding that Git was the right tool for version control, but I’m not sure how to integrate it with Databricks. Can you guide me through the setup?

**Sharon:** Of course! Before we dive into Git integration, let’s first understand your working environment—your Databricks workspace.

**John:** Right! That’s where we create notebooks and run our code, correct?

**Sharon:** Exactly! Think of your Databricks workspace as your virtual desk in the cloud. It’s where you collaborate with your team on notebooks, data analysis, and machine learning projects.

**John:** Got it! So, how does Git fit into this workspace?

**Sharon:** When we integrate Git into Databricks, we link our workspace to Git repositories. This allows us to track changes, collaborate seamlessly, and restore previous versions if needed.

**John:** That makes sense! But where does the code actually get stored?

**Sharon:** Good question! Git uses two types of repositories:

1.  **Local Repository** – A copy of the project stored in your **Databricks workspace**.
2.  **Remote Repository** – A shared version stored on platforms like **GitHub**, where your team can collaborate.

**John:** So, the local repository is my personal working copy, and the remote repository is the master version for the whole team?

**Sharon:** Exactly! Your local repository lets you make changes before pushing them to the remote repository, ensuring a smooth workflow.

**John:** This makes so much sense now! So, the next step is to integrate Git with Databricks?

**Sharon:** Yes! I’ll walk you through the steps to set up Git in Databricks next.

**Tags**


##### Input 3
**Type:** Choice

**Question:** What is a Git repository?

**Options:** 
- A folder containing unrelated files

- A space where code and its history are stored and manged

- A tool used for coding without tracking changes

- A document management system

**Correct Options:** 
- A space where code and its history are stored and manged

**Tags**
- code-versioning (skill)

##### Input 4
**Type:** Choice

**Question:** What is the difference between a local and a remote repository in Databricks concerning Git?

**Options:** 
- A local repository is on your Databricks workspace, while a remote repository could be on GitHub or another remote server.

- A local repository is shared across the team, while a remote repository is private.

- A local repository is hosted online, while a remote repository is stored on your personal computer.

- There is no difference between a local and remote repository in Databricks.

**Correct Options:** 
- A local repository is on your Databricks workspace, while a remote repository could be on GitHub or another remote server.

**Tags**
- code-versioning (skill)

##### Input 5
**Type:** Text

**Sharon:** Now that we’ve linked our Databricks workspace to Git and understand local and remote repositories, let’s see how to share code changes with the team.

When you modify a notebook in Databricks, the changes are saved in your local repository.

![Image-image.png](https://cdn.enqurious.com/images/493179ca-8ad7-4f2b-867d-42f60ae99efb_image.webp)

To make these changes visible to your team, enable collaboration, and maintain a clear version history, you need to push them to the remote repository. The remote repository, hosted on GitHub, acts as the central hub where the project is stored, updated, and accessed by all contributors.


![Image-image.png](https://cdn.enqurious.com/images/ec37b28f-e4b2-4e5d-a544-e67c3223d0a9_image.webp)


**Tags**


##### Input 6
**Type:** Text

**John:** I have a question. Since we've only been working on our repository on Databricks. How should we reflect those changes in the remote repository hosted on GitHub?

**Sharon:** That's a great question! This brings us to an important concept: while you've made changes within your Databricks environment, these changes are still only on Databricks, and not yet visible to the team on GitHub.

This is where Commit & Push comes into play. It allows you to save your changes from Databricks and upload them to the remote repository on GitHub, so the rest of the team can access, review, and collaborate on your work.

Let’s dive into how Commit and Push work within the Databricks workflow

**Tags**


##### Input 7
**Type:** Text

**Sharon:** In Git, there are two key steps to saving and sharing code changes—Commit and Push.

**Commit** saves your changes locally in Databricks, creating a new version.

**Push** uploads these changes to the remote repository on GitHub, making them available to the team.

**John:** So, I need to commit first and then push separately?



**Sharon:** Normally, yes! But Databricks makes this easier by combining both steps into a single Commit & Push option. This ensures your changes are tracked locally and automatically pushed to GitHub in one step.



**📌 Refer to Image 1: This shows how Databricks allows you to Commit & Push in a single action.**
 
          
![Image-image.png](https://cdn.enqurious.com/images/4d6b6bea-fbe7-475f-acef-da3554cd88db_image.webp)

**John:** What if I need to go back to an earlier version?

**Sharon:** Every commit creates a new version in Git. If something goes wrong, you can roll back to a previous commit and restore your project to a stable state.

**📌 Refer to Image 2: This shows the commit history in GitHub, where each version is recorded, allowing you to track and revert changes as needed.**

![Image-image.png](https://cdn.enqurious.com/images/166cb3ac-112f-4956-8307-1f91c1614756_image.webp)

This is why version control in Git is crucial—it lets you update your code safely while maintaining a reliable history of changes.

**Tags**


##### Input 8
**Type:** Text

### **Imagine This Scenario:**

You’ve been working on your local code for hours and **pushed** your changes to GitHub. Meanwhile, your teammate also made updates and pushed their changes.

Now, the **remote repository is ahead** of your local version—you’re out of sync!

How do you ensure you're working with the **latest version** without missing any updates?

This brings us to the next step—**Pulling Changes**. But before we dive in, why do you think keeping our local and remote versions in sync is so important?

**Tags**


##### Input 9
**Type:** Text

**John:** Hey Sharon, I saw that Sam pushed some updates to GitHub. How do I get those changes into my Databricks environment?

**Sharon:** Your Databricks repository doesn’t auto-sync with GitHub. You need to pull the updates to keep your local copy up to date.

**John:** How do I do that?

**Sharon:** Click the "Pull" button in Databricks. If you see a number next to it (like 1), it means there are new updates. Once you pull, your repository will sync with GitHub, ensuring you have the latest changes.
 
          
![Image-image.png](https://cdn.enqurious.com/images/1e56ffa3-59a8-4bb5-b188-dce8c54dbd23_image.webp)

**John:** Got it! So pulling ensures I’m always working with the latest version?

**Sharon:** Exactly! It helps avoid conflicts and keeps everyone on the same page.

**Tags**


##### Input 10
**Type:** Text

**Commit vs Push vs Pull**
--------------------------

**Operation**

**Description**

**Effect**

**Scenario**

**Commit**

Saves changes to your local repository.

Creates a new version of your project on your local machine, keeping track of changes made.

You’ve made updates to your code and want to save those changes locally before sharing them.

**Push**

Sends committed changes from your local repository to the remote repository on GitHub.

Updates the remote repository on GitHub with the latest changes from your local machine, making them available to others.

You’ve committed your changes locally and now need to share them with your team on GitHub.

**Pull**

Retrieves the latest changes from the remote repository on GitHub to your local repository.

Updates your local repository with changes made by others on GitHub, ensuring your local copy is in sync with the remote version.

Your teammate has made changes and pushed them to GitHub; you need to update your local copy with their latest changes.

**Tags**


##### Input 11
**Type:** Choice

**Question:** When you push changes from Databricks, where are these changes sent?

**Options:** 
- To another Databricks workspace

- To a remote Git repository such as GitHub

- To a backup server

- To your local Databricks environment

**Correct Options:** 
- To a remote Git repository such as GitHub

**Tags**
- code-versioning (skill)

##### Input 12
**Type:** Choice

**Question:** In Databricks, why would you use the pull feature?

**Options:** 
- To delete a branch from the remote repository

- To create a new repository in Databricks

- To change the repository settings

- To update your Databricks workspace with the latest changes from the remote repository

**Correct Options:** 
- To update your Databricks workspace with the latest changes from the remote repository

**Tags**
- code-versioning (skill)

##### Input 13
**Type:** Text

John and Sharon are collaborating on a project in GitHub. John is making direct changes to the main branch but runs into an issue when Sharon pushes updates.

**John:** Sharon, I just tried to push my changes, but GitHub is rejecting them. What’s going on?

**Sharon:** It looks like there’s a merge conflict. Did you pull the latest changes before making your updates?

**John:** Uh, no. I’ve just been working on my local version.

**Sharon:** That’s the issue! I had already made updates and pushed them to GitHub. Since your local version is outdated, GitHub doesn’t know how to merge your changes with mine.

**John:** Oh! So what do I do now?

**Sharon:** Next time, before making any changes, always pull the latest updates. But a better approach is to use branches!

**John:** Branches? What are those?

**Sharon:** Think of a branch as your own workspace. Instead of editing the main branch directly, you create a separate branch to work on your changes. That way, you don’t interfere with ongoing work in the main branch.

**John:** I see! So I create a branch, work on my changes, and then merge it back into the main branch when I’m done?

**Sharon:** Exactly! This way, multiple people can work on different features at the same time without conflicts.

**John:** That makes a lot of sense. How do I create a branch?

**Sharon:** It’s simple! You can create a branch in GitHub or directly in Databricks. 

![Image-image.png](https://cdn.enqurious.com/images/a9853d69-a3de-4462-9fed-1eec4f482bad_image.webp)

Once your work is done, you create a Pull Request to merge it into the main branch after review.

**John:** That’s great! I’ll start working on my feature in a separate branch now 
          


**Tags**


##### Input 14
**Type:** Choice

**Question:** Can you delete a branch directly from Databricks?

**Options:** 
- Yes, Databricks provides a built-in option to delete branches

- No, branch deletion must be done through GitHub 

**Correct Options:** 
- No, branch deletion must be done through GitHub 

**Tags**
- code-versioning (skill)

##### Input 15
**Type:** Text

**John:** Alright, Sharon, I created a branch for my changes like you suggested. Now, how do I merge it back into the main branch?

**Sharon:** Good job, John! To merge your branch, you need to create a Pull Request (PR).

**John:** What exactly is a Pull Request?

**Sharon:** A Pull Request is a way to propose changes to the main branch. It allows your teammates to review your code, suggest improvements, and approve it before merging.
Here’s how you create a Pull Request in GitHub:
- Go to your GitHub repository.
- Click on Pull Requests → New Pull Request.
- Select:
    - Base branch (where you want to merge your changes, e.g., main)

    - Compare branch (your working branch, e.g., john-feature)

    - Click Create Pull Request and add a brief description of your changes.

📌 Refer to the image below:
          
![Image-image.png](https://cdn.enqurious.com/images/072c0753-5bcf-4926-b72e-7b14313f407b_image.webp)

![Image-image.png](https://cdn.enqurious.com/images/e4937bfa-568a-44a5-9969-404546c6a4df_image.webp)


**John:** What happens next?

**Sharon:** Your teammates (including me) will review your changes. If everything looks good, we approve it. If there are any issues, we’ll leave comments for you to fix. 

Once the review is complete:

- Click Merge Pull Request.
- Confirm the merge to integrate your changes into the main branch.
📌 Refer to the image below:
![Image-image.png](https://cdn.enqurious.com/images/3a4a1898-7e67-4ea0-a70c-466e8b4e9784_image.webp)

**John:** That’s simple! So PRs help maintain code quality and avoid direct edits to the main branch?

**Sharon:** Exactly! They keep the project organized and allow multiple people to work on features simultaneously without conflicts. It’s a crucial step to ensure code quality and collaboration efficiency.

**Tags**


##### Input 16
**Type:** Choice

**Question:** What causes a merge conflict in Git?

**Options:** 
- When two branches have identical changes

- When two people push changes to the same line of code in a file without pulling the latest updates

- When a commit message is missing

- When the repository is not initialized

**Correct Options:** 
- When two people push changes to the same line of code in a file without pulling the latest updates

**Tags**
- code-versioning (skill)

##### Input 17
**Type:** Text

**John:** Alright, Sharon, I created a branch for my changes like you suggested. Now, how do I merge it back into the main branch?

**Sharon:** Good job, John! To merge your branch, you need to create a **Pull Request (PR)**.

**John:** What exactly is a Pull Request?

**Sharon:** A Pull Request is a way to propose changes to the main branch. It allows your teammates to review your code, suggest improvements, and approve it before merging.

Here’s how you create a Pull Request in GitHub:

1.  Go to your GitHub repository.
2.  Click on **Pull Requests** → **New Pull Request**.
3.  Select:
    *   **Base branch** (where you want to merge your changes, e.g., `main`)
    *   **Compare branch** (your working branch, e.g., `john-feature`)
4.  Click **Create Pull Request** and add a brief description of your changes.

📌 **Refer to the image below:**

![](https://cdn.enqurious.com/images/ab6e866e-7400-47e3-8702-01660e7293b5_image%20(13).webp)

**Tags**


##### Input 18
**Type:** Choice

**Question:** What is a Pull Request (PR) in GitHub?

**Options:** 
- A request to delete a repository

- A way to merge changes from one branch into another after a review

- A command to reset a branch

- A method to create a new repository

**Correct Options:** 
- A way to merge changes from one branch into another after a review

**Tags**
- code-versioning (skill)

##### Input 19
**Type:** Text

**Sharon:** Alright, John, we’ve covered how Git works in Databricks—creating repositories, committing changes, pushing, pulling, and using branches. With Git, you can confidently track changes and collaborate smoothly on any project.

**John:** It’s great to see how branches help keep our work organized and prevent conflicts.

**Sharon:** Exactly, John! Git ensures seamless teamwork and keeps our code versioned and safe. Just remember to commit and push regularly, and always use branches for different tasks.

**John:** Got it! This will make collaboration much easier.

**Tags**


##### Input 20
**Type:** File Upload

**Question:** Upload screenshots showing:
- The approach you used to connect your Databricks workspace to GitHub.
- That you have successfully pushed your notebooks from Databricks to GitHub.

**Max No. of Files:** 15

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**
- code-versioning (skill)

