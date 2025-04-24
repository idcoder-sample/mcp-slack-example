
# Import necessary modules
import asyncio  # For asynchronous operations
from typing import Optional  # For type hinting optional values
from contextlib import AsyncExitStack  # Manages async context managers
import os
import json  # To load configuration from JSON file

# Import MCP and OpenAI libraries
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI

# Load configuration values from config.json file
with open("config.json", "r") as json_file:
    config = json.load(json_file)

# Extract values from the config dictionary
OPENAI_API_KEY = config["OPENAI_API_KEY"]
SLACK_BOT_TOKEN = config["SLACK_BOT_TOKEN"]
SLACK_TEAM_ID = config["SLACK_TEAM_ID"]
SLACK_CHANNELID_CHANNELMOBILE = config["SLACK_CHANNELID_CHANNELMOBILE"]
SLACK_CHANNELID_CHANNELWEB = config["SLACK_CHANNELID_CHANNELWEB"]
SLACK_CHANNELID_SERVICEPAYMENT = config["SLACK_CHANNELID_SERVICEPAYMENT"]
SLACK_CHANNELID_SERVICEPROVISIONING = config["SLACK_CHANNELID_SERVICEPROVISIONING"]
SLACK_CHANNELID_ALL = config["SLACK_CHANNELID_ALL"]

# Define the main client class to handle Slack + AI interaction
class MCPSlackClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()  # Handles context management for resources
        self.client = OpenAI(api_key=OPENAI_API_KEY)  # Initialize OpenAI client

    # Establish connection to the MCP Slack server
    async def connect_to_server(self):
        server_params = StdioServerParameters(
            command="npx",  # Command to run
            args=["-y", "@modelcontextprotocol/server-slack"],  # CLI args
            env={"SLACK_BOT_TOKEN": SLACK_BOT_TOKEN, "SLACK_TEAM_ID": SLACK_TEAM_ID},  # Set environment variables
        )

        # Start the MCP Slack server with stdio connection
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport

        # Open session with the server
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()  # Initialize session

        # Print the list of tools supported by the server
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    # Use GPT to classify the type of issue described in the ticket
    async def classify_alert(self, ticket_message):
        try:
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

            response = self.client.chat.completions.create(model="gpt-4", messages=classificationQuery)
            classification = response.choices[0].message.content.strip()

            print(classification)
            return classification

        except Exception as e:
            print(f"Error during classification: {str(e)}")

    # Use GPT to extract important info from the ticket and convert it into structured data
    async def summarize_ticket(self, ticket_message):
        try:
            summarizationQuery = [{
                "role": "user",
                "content": f"""
                You are a support assistant that extracts structured information from customer ticket messages.

                Your task is to extract the following details from the ticket message:

                - raw_ticket_message: (The original customer message)
                - payment_channel: (Where the payment was attempted, e.g., "credit card", "bank transfer", "mobile wallet", etc.)
                - package_detail: (Any mention of a plan, package, or product, e.g., "Premium Plan", "10GB data pack", etc.)
                - timestamp: (Any date/time mentioned in the message, or the time the issue occurred)

                If any detail is not available, return `null` for that field.

                ---

                Ticket message:
                "{ticket_message}"

                ---

                Return the result in the following format (no explanation):

                {{
                  "raw_ticket_message": "...",
                  "payment_channel": "...",
                  "package_detail": "...",
                  "timestamp": "..."
                }}
                """
            }]
            response = self.client.chat.completions.create(model="gpt-4", messages=summarizationQuery)
            summary = response.choices[0].message.content.strip()

            print(summary)
            return summary

        except Exception as e:
            print(f"Error during summarization: {str(e)}")

    # Post the summarized message to the correct Slack channel based on classification
    async def post_message(self, classification, summary):
        try:
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

            # Post the message to the selected channel
            await self.session.call_tool("slack_post_message", {
                "channel_id": channel_id,
                "text": summary
            })
            print("Message posted successfully.")
        except Exception as e:
            print(f"Error posting message: {str(e)}")

    # Optional chat loop for posting custom messages (used for manual testing/debugging)
    async def chat_loop(self):
        print("\nMCP Slack client started!")
        print("(1) Post Message to Slack Channel")
        print("(2) Exit")

        while True:
            try:
                choice = input("\nChoice: ").strip()
                if choice == "2":
                    break

                channel = input("Slack channel ID: ").strip()

                if choice == "1":
                    message = input("Message to post: ").strip()
                    await self.post_message(channel, message)
                else:
                    print("Invalid choice.")

            except Exception as e:
                print(f"\nError: {str(e)}")

    # Clean up async resources
    async def cleanup(self):
        await self.exit_stack.aclose()


# Main async function to run the full pipeline
async def main():
    client = MCPSlackClient()

    try:
        await client.connect_to_server()  # Connect to MCP Slack server
        
        ticket_message = input("Input Ticket Details: ").strip()

        summary = await client.summarize_ticket(ticket_message)  # Step 1: Summarize the ticket
        classification = await client.classify_alert(summary)    # Step 2: Classify the summary
        await client.post_message(classification, summary)       # Step 3: Post to correct Slack channel

    finally:
        await client.cleanup()  # Close any open resources


# Entry point when the script is run directly
if __name__ == "__main__":
    asyncio.run(main())
