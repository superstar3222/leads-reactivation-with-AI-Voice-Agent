import os
from vapi import Vapi
from ..base_agent import BaseAgent


class VapiAI(BaseAgent):
    """
    A class that integrates with the Vapi API for handling voice call automation tasks.
    This class provides methods for creating and managing agents, tools, phone numbers, and making/handling calls through Vapi.

    Attributes:
        client (Vapi): An instance of the Vapi client initialized with the API key.
        allowed_tools (dict): A dictionary of tools allowed for interaction by the agent.
    """
    
    def __init__(self, tools: dict={}):
        """
        Initialize the VapiAI class and set up the Vapi client with the provided API key.
        
        Args:
            tools (dict): A dictionary of tools available for the agent.
        """
        self.client = Vapi(token=os.getenv("VAPI_API_KEY"))
        self.allowed_tools = tools

    async def make_call(self, request: dict):
        """
        Create and initiate a call through the Vapi API.
        
        Args:
            request (dict): The payload with details for the call request.
        """
        print(f"Making a Vapi call")
        response = self.client.calls.create(**request)
        return response
    
    async def handle_webhook_call(self, request: dict):
        """
        Handle incoming webhook calls based on the message type in the payload.
        
        Args:
            request (dict): The request payload containing event details.
        """
        # Parse the JSON payload from the request
        payload = await request.json()
        
        response = None
        message_type = payload['message']['type']
        if message_type == "tool-calls":
            response = await self.tools_call_handler(payload["message"])
        elif message_type == "end-of-call-report":
            response = await self.end_of_call_report_handler(payload["message"])
        else:
            pass
        
        return response

    def create_agent(self, request: dict):
        """
        Create a new assistant/agent via the Vapi API.
        
        Args:
            request (dict): A dictionary containing all required parameters for creating the agent.
        """
        print("Vapi creating assistant.")
        output = self.client.assistants.create(**request)
        return {"status": "success", "details": output}

    def update_agent(self, agent_id: str, request: dict):
        """
        Update an existing assistant/agent via the Vapi API.
        
        Args:
            agent_id (str): The ID of the agent to be updated.
            request (dict): A dictionary containing the new configuration for the agent.
        """
        print("Vapi updating assistant.")
        output = self.client.assistants.update(id=agent_id, **request)
        return {"status": "success", "details": output}

    def create_tool(self, request: dict):
        """
        Create a new tool in Vapi.
        
        Args:
            request (dict): A dictionary containing the parameters to create the tool.
        """
        print("Vapi creating tool.")
        tool_creation_output = self.client.tools.create(request=request)
        return {"status": "success", "details": tool_creation_output}

    def update_tool(self, tool_id: str, request: dict):
        """
        Update an existing tool in Vapi.
        
        Args:
            tool_id (str): The ID of the tool to be updated.
            request (dict): A dictionary containing the new configuration for the tool.
        """
        print("Updating Vapi tool")
        output = self.client.tools.update(id=tool_id, **request)
        return {"status": "success", "details": output}

    def add_phone_number(self, request: dict):
        """
        Add a phone number to Vapi.
        
        Args:
            request (dict): A dictionary containing the parameters for the phone number.
        
        Returns:
            dict: A dictionary with the status and details of the phone number creation.
        """
        print("Adding phone number in Vapi")
        phone_creation_output = self.client.phone_numbers.create(request=request)
        return {"status": "success", "details": phone_creation_output}
    
    def get_allowed_tools(self):
        """
        Retrieve the list of allowed tools for the agent.
        
        Returns:
            dict: A dictionary of allowed tools.
        """
        return self.allowed_tools
    
    async def tools_call_handler(self, payload):
        """
        Handle tool calls as specified in the webhook payload and return the results.
        
        Args:
            payload (dict): The payload containing the tool call details.
        
        Returns:
            dict: The results of the tool calls.
        """
        results = []
        
        tool_call_list = payload.get("toolCallList")
        for tool_call in tool_call_list:
            call_id = tool_call.get("id")
            function_call = tool_call.get("function")
            name = function_call.get('name')
            arguments = function_call.get('arguments')
            
            if name in self.allowed_tools:
                result = await self.allowed_tools[name](**arguments)
                results.append({
                    "name": name,
                    "toolCallId": call_id,
                    "result": result
                })
            else:
                results.append({
                    "name": name,
                    "toolCallId": call_id,
                    "result": "Unknown function"
                })

        return {"results": results}
    
    async def end_of_call_report_handler(self, payload):
        """
        Handle the end of call report and initiate post-call processing.
        
        Args:
            payload (dict): The payload containing the call's end details.
        """
        call_output = self.process_call_outputs(payload)
        self.post_call_processing(call_output)
        
    def pre_call_processing(self, payload):
        """
        Perform pre-call processing to prepare the lead data.
        This method must be overridden in a subclass to implement specific pre-call logic.
        
        Args:
            payload: Payload containing lead details.
        """
        pass
    
    def get_call_input_params(self, payload):
        """
        Build the input parameters for initiating a call.
        This method must be overridden in a subclass to implement specific pre-call logic.
        """
        pass
    
    def process_call_outputs(self, payload):
        """
        Process the outputs from the completed call.
        This method must be overridden in a subclass to implement specific pre-call logic.
        
        Args:
            payload: Payload containing call details received from Vapi.
        """
        pass
       
    def post_call_processing(self, payload):
        """
        Perform post-call processing to analyze results and update the CRM.
        This method must be overridden in a subclass to implement specific pre-call logic.
        
        Args:
            payload: Payload containing processed call details.
        """
        pass
