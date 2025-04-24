
# MCP Slack Example

## Overview
This Python script acts as an integration between:
- OpenAI's GPT-4 for ticket classification and summarization
- A Slack bot via Model Context Protocol (MCP) to post messages into the correct Slack channel

> ⚠️ **Disclaimer:**  
> This is a basic example demonstrating how to integrate Slack with the MCP server.

## Available Formats

This example is provided in two formats:
- **Python script (`.py`)**
- **Jupyter Notebook (`.ipynb`)**

Choose the format that best suits your workflow (e.g., local development or use in Jupyter/Google Colab), and download the respective file.

## Prerequisites

Before you begin, make sure you have the following set up:

- ✅ A **Slack account** and a dedicated **Slack channel**
- ✅ An **OpenAI GPT account**

### Slack Setup Instructions

To set up your Slack environment, follow the instructions provided here:  
👉 [Slack Integration Setup Guide](https://github.com/modelcontextprotocol/servers/tree/main/src/slack)


### Purpose of This Application
The goal of this application is to automate support ticket handling. It simplifies operations by:
1. Understanding support issues using AI
2. Classifying them accurately
3. Posting structured information to relevant Slack channels for quicker resolution

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
pip install openai
```

2. Prepare `config.json` file with the following structure:
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

## Usage Example
```bash
python mcp_slack_client.py
```
Follow the prompts:
1. Enter the ticket message
2. Let GPT-4 summarize and classify it
3. The script will post to the right Slack channel

---

## Limitations / Known Issues
- The classification depends on GPT-4's interpretation, which may vary.
- No retry or backoff logic for network/API failures.
- Slack API or MCP tool failures aren't deeply handled.
- Requires internet and valid API credentials.

---

## Coming Up Next
- Add unit tests with mock GPT responses
- Support other messaging platforms (e.g., Teams, Discord)
- Add logging for production use

---

## Questions?
Ping the project maintainer or open an issue in your team repo.
