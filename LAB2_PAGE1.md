# Lab 2: Create and Migrate Microsoft Foundry Resource

## Overview

This exercise guides you through migrating your subscription/resource to a new region if needed. Resources may need to move to a different region for various reasons.

**Note:** Resource migration may occur if there is an urgent need to switch to a different region.

---

## Task 1: Create a Microsoft Foundry Resource

In this task, you will create a Microsoft Foundry Resource that will be used when you complete the previous lab. You will get to explore it throughout the migration process and ultimately, configure your new resource from anywhere anytime.

### Steps:

1. **Navigate to Azure Portal**
   - Go to the [Azure Portal](https://portal.azure.com)

2. **Create Foundry Resource**
   - Search for "Microsoft Foundry"
   - Select the resource type from search results
   - Note: The actual Hub (AI) Characters may vary based on what's available. If you don't see exactly what's in the example, try include what's in the resource name. Just be sure this resource work for the advertising of this lab.

3. **Configure Basic Settings**
   - **Subscription:** Select your subscription (e.g., "Azure for Students")
   - **Resource group:** Create new or use existing (e.g., `kingersoll-contososupport_rg`)
   - **Region:** Select region (West US or your preferred region)
   - Review other default settings

4. **Select appropriate resource tier and set tags**
   - Use default values for other parameters

---

## Task 2: Migrate your OpenAI API and LLM

**Under:** Later in life, you can move items if you decide to move locations (i.e., you rent new multi-open data center sites).

### Migration Steps:

1. **Navigate to OpenAI resource and create content**
   - If it's eligible, a Y/N notice should be given for your OpenAI Resource (should be `contososupportoai-<alias>`)

2. **Select the Foundry portal to navigate to the Azure AI Foundry portal for your tenant**

3. **Create or select a project based on your naming convention**

4. **At the Overview page, select Next or main menu**

5. **From the resource project card and tabs, you can read details about your new external summary**

---

## Task 3: Deploy the GPT-4o model

You must select and deploy the GPT-4o model to your Foundry instance so your app can interact with it.

### Deployment Steps:

1. **Access Model Deployments**
   - From the "My Assets" section of Foundry portal
   - Select **Models + Endpoints** → **Deploy Model** → **Deploy base model**

2. **Search and Select Model**
   - In the search box, enter "gpt-4o"
   - Select the **gpt-4o** model (Chat completion, Responses)
   - Click **Confirm**

3. **Configure Deployment**
   - **Deployment name:** gpt-4o
   - **Deployment type:** Global-Standard
   - Review and adjust settings as needed

4. **Complete Deployment**
   - Click **Deploy** button
   - Wait for deployment to complete (status: Succeeded)

---

## Summary

In this first exercise, you created your Microsoft Foundry Resource and initiated the Deploy option and API key. In later exercise, you can use the endpoint and the key.

---

## Key Takeaways

- Microsoft Foundry resources can be created and migrated between regions
- The Foundry portal (https://ai.azure.com) is separate from the Azure portal
- GPT-4o deployment is done through Models + Endpoints in the Foundry portal
- Deployment provides endpoint URLs and API keys for integration
