import os
from src.base.voice_agent_providers.vapi import VapiAI
from src.prompts import VOICE_AGENT_PROMPT
from dotenv import load_dotenv

load_dotenv()

# Before creating your assistant, you must first create the needed tools
# Copy their ids(str) in the list below.
# If your assistant does not require any tool, leave empty
tool_ids_list = ["4befe734-cca9-44af-895a-8b2a0aa4f731"]

assistant_config = {
    "name": "Alex",
    "transcriber": {
        "provider": "deepgram",  # Transcriber provider
        "language": "en"
    },
    "model": {
        "provider": "openai",  # Model provider
        "model": "gpt-4o",  # Model ID
        "toolIds": tool_ids_list,
        "messages": [
            {
                "role": "system",
                "content": VOICE_AGENT_PROMPT
            }
        ]
    },
    "voice": {
        "provider": "openai",  # Voice provider
        "voiceId": "alloy"  # Voice ID
    },
    "first_message": "Hi, is this {{firstName}}?",
    "end_call_message": "Thanks for your time.",
    "analysis_plan": {
        "summaryPlan": {
            "messages": [],
            "enabled": False,
        },
        "structuredDataPlan": {
            "messages": [],
            "enabled": False,
        },
        "successEvaluationPlan": {
            "rubric": "NumericScale",
            "messages": [],
            "enabled": False
        }
    },
    "server_url": f"{os.getenv('SERVER_URL')}/webhook"
}


vapi_client = VapiAI()

# Create a new assistant using the above config
# output = vapi_client.create_agent(assistant_config)
# print(output)

# # Get the assistant id, copy it to .env
# print(output["id"])


# Update an existing assistant with the above config
assistant_id = "ed9dc040-735c-4c0f-89d8-e926e4eac54c"
output = vapi_client.update_agent(assistant_id, assistant_config)
print(output)