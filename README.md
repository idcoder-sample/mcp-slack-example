
# MCP Slack Example

## Table of Contents
- [Overview](#overview)
  - [Available Formats](#available-formats)
  - [Purpose of This Application](#purpose-of-this-application)
- [Prerequisites](#prerequisites)
  - [Slack Setup Instructions](#slack-setup-instructions)
- [Getting Started](#getting-started)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Usage Example](#usage-example)
- [Script Flow (Simplified)](#script-flow-simplified)
- [Main Components](#main-components)
  - [MCPSlackClient](#mcpslackclient)
  - [summarize_ticket()](#summarize_ticket)
  - [classify_alert()](#classify_alert)
  - [post_message()](#post_message)
- [Limitations / Known Issues](#limitations--known-issues)
- [Coming Up Next](#coming-up-next)


## Overview
This Python script acts as an integration between:
- OpenAI's GPT-4 for ticket Classification and Summarization/Extraction
- A Slack bot via Model Context Protocol (MCP) to post messages into the correct Slack channel

> ⚠️ **Disclaimer:**  
> This is a basic example demonstrating how to integrate Slack with the MCP server.

### Available Formats

This example is provided in two formats:
- **Python script (`.py`)**
- **Jupyter Notebook (`.ipynb`)**

Choose the format that best suits your workflow (e.g., local development or use in Jupyter/Google Colab), and download the respective file.

### Purpose of This Application
The goal of this application is to automate support ticket handling. It simplifies operations by:
1. Understanding support issues using AI
2. Classifying them accurately
3. Posting structured information to relevant Slack channels for quicker resolution

## Prerequisites

Before you begin, make sure you have the following set up:

- ✅ A **Slack account** and a dedicated **Slack channel**
- ✅ An **OpenAI GPT account**

### Slack Setup Instructions

To set up your Slack environment, follow the instructions provided here:  
👉 [Slack Integration Setup Guide](https://github.com/modelcontextprotocol/servers/tree/main/src/slack)

Make sure to add your slack app into your desired channel. In my case, i named my slack-app as TicketClassification and added to 5 channel.
![AddApp1](doc/add_app_to_channel_1.png)
![AddApp2](doc/add_app_to_channel_2.png)
![AddApp3](doc/app_added_to_channel.png)

---

## Getting Started

### Requirements
- Python 3.8+
- `openai` package
- Access to OpenAI API Key
- Slack App with Bot Token
- MCP installed (`npx @modelcontextprotocol/server-slack`)

### Installation
1. Install Python packages:
```bash
pip install mcp openai
```

2. Prepare `config.json` file with the following structure (If Slack channel is configured differently, please note the next step):
```json
{
  "OPENAI_API_KEY": "your-api-key",
  "SLACK_BOT_TOKEN": "xoxb-your-token",
  "SLACK_TEAM_ID": "Txxxxxx",
  "SLACK_CHANNELID_CHANNELMOBILE": "Cxxxx01",
  "SLACK_CHANNELID_CHANNELWEB": "Cxxxx02",
  "SLACK_CHANNELID_SERVICEPAYMENT": "Cxxxx03",
  "SLACK_CHANNELID_SERVICEPROVISIONING": "Cxxxx04",
  "SLACK_CHANNELID_ALL": "Cxxxx99"
}
```

3. (Optional) Channel options was hardcoded, so if you want to change the channel name, you can configure in the JSON file above, and also change some of codes to meet you expectation:

On the Initialization
```python
# Extract values from the config dictionary
OPENAI_API_KEY = config["OPENAI_API_KEY"]
SLACK_BOT_TOKEN = config["SLACK_BOT_TOKEN"]
SLACK_TEAM_ID = config["SLACK_TEAM_ID"]
SLACK_CHANNELID_CHANNELMOBILE = config["SLACK_CHANNELID_CHANNELMOBILE"]
SLACK_CHANNELID_CHANNELWEB = config["SLACK_CHANNELID_CHANNELWEB"]
SLACK_CHANNELID_SERVICEPAYMENT = config["SLACK_CHANNELID_SERVICEPAYMENT"]
SLACK_CHANNELID_SERVICEPROVISIONING = config["SLACK_CHANNELID_SERVICEPROVISIONING"]
SLACK_CHANNELID_ALL = config["SLACK_CHANNELID_ALL"]
```
On the prompt
```python
classificationQuery = [{
      "role": "user",
      "content": f"""You are a customer support classifier assistant.
      Your task is to classify the following ticket message into one of these five categories:

      Categories:
      1. channel-mobile – Issues related to mobile applications or mobile platforms.
      2. channel-web – Issues related to websites or web interfaces.
      3. service-payment – Issues related to billing, payment transactions, or refunds.
      4. service-provisioning – Issues related to service activation, account setup, or access provisioning.
      5. unknown – If the issue doesn't clearly fit any of the above categories.

      Instructions:
      - Return only the category name, do not change the categories name provided above
      - Be as precise as possible. Do not guess if the message is unclear — use "unknown".

      ---

      Ticket message:
      "{ticket_message}"

      Category:"""
  }]
```
On the post_message
```python
# Choose Slack channel based on classification result
if classification == "channel-mobile":
    channel_id = SLACK_CHANNELID_CHANNELMOBILE
elif classification == "channel-web":
    channel_id = SLACK_CHANNELID_CHANNELWEB
elif classification == "service-payment":
    channel_id = SLACK_CHANNELID_SERVICEPAYMENT
elif classification == "service-provisioning":
    channel_id = SLACK_CHANNELID_SERVICEPROVISIONING
else:
    channel_id = SLACK_CHANNELID_ALL  # Fallback/default channel
```

### Usage Example
```bash
python mcp_slack_client.py
```
Follow the prompts:
1. Enter the ticket message
   ![RunningExample](doc/notebook_running_example.png)
3. Let GPT-4 summarize and classify it
4. The script will post to the right Slack channel
   ![SummaryExample](doc/summary_successfully_posted.png)

---

## Script Flow (Simplified)
```mermaid
graph TD
    A[Start] --> B[Load config.json]
    B --> C[Connect to MCP Server]
    C --> D[Input: Ticket Message]
    D --> E[Summarize with OpenAI GPT-4]
    E --> F[Classify Summary]
    F --> G[Select Slack Channel]
    G --> H[Post Message to Slack]
    H --> I[Done / Await new input]
```

---

## Main Components

### `MCPSlackClient`
This class encapsulates everything:
- OpenAI client setup
- MCP session connection
- Ticket summarization and classification
- Slack message posting

### `summarize_ticket()`
Uses GPT-4 to extract:
- `raw_ticket_message`: The full user message
- `payment_channel`: Method used, like card, wallet, etc.
- `package_detail`: Any plan/package mentioned
- `timestamp`: When issue occurred (if stated)

### `classify_alert()`
Classifies the message into one of:
- `channel-mobile`
- `channel-web`
- `service-payment`
- `service-provisioning`
- `unknown`

### `post_message()`
Selects Slack channel based on classification and posts the summary.

---

## Limitations / Known Issues
- The classification depends on GPT-4's interpretation, which may vary.
- Customize the channel name and classification to suit your specific needs.
- For production use, a more comprehensive scenario handling mechanism is required. This example is intended for demonstration purposes only.
- Consider integrating ticket-related messages directly with your existing ticketing or logging systems (e.g., Grafana, Remedy, or Jira).

---

## Coming Up Next
- Alerts are triggered directly from Grafana (integrated as an input source for ticket generation).
- Integrates with the file system logs to fetch relevant logs based on the detected scenario  
  (e.g., payment-related issues will automatically retrieve logs from the payment service).
