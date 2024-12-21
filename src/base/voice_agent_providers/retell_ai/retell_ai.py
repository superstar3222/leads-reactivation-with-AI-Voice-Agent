import os
import json
from ..base_agent import BaseAgent
from retell import Retell

class RetellAI(BaseAgent):
    def __init__(self, tools: dict={}):
        """
        Initialize the Retell AI client and set the allowed tools.
        
        Args:
            tools (dict): Dictionary of allowed tools accessible to the agent.
        """
        self.client = Retell(api_key=os.getenv("RETELL_API_KEY"))
        self.allowed_tools = tools

    async def make_call(self, request: dict):
        """
        Create a phone call via the Retell API.
        
        Args:
            request (dict): Request payload for initiating the call.
        
        Returns:
            dict: Response from the Retell API.
        """
        response = await self.client.call.create_phone_call(**request)
        return response

    async def handle_webhook_call(self, request: dict):
        """
        Handle incoming webhook requests from Retell.
        
        Args:
            request (dict): The webhook request payload.
        
        Returns:
            dict: Response indicating the result of the webhook processing.
        """
        try:
            post_data = await request.json()
            event = post_data.get("event", "")
            print(post_data)

            # Verify signature
            valid_signature = self._validate_webhook(post_data)
            if not valid_signature:
                return {"status_code": 401, "content": {"message": "Unauthorized"}}

            if event:
                self._handle_retell_event(event, post_data)
            else:
                output = self._handle_tool_call(post_data)
                return output
        except Exception as err:
            print(f"Error in webhook: {err}")
            return {"status_code": 500, "content": {"message": "Internal Server Error"}}

    def get_allowed_tools(self):
        """
        Retrieve the list of tools accessible to the agent.
        
        Returns:
            dict: Dictionary of allowed tools.
        """
        return self.allowed_tools

    def create_agent(self, config: str):
        """
        Create a new agent in the Retell system.
        
        Args:
            config (str): Configuration for the new agent.
        
        Returns:
            dict: Response from the Retell API.
        """
        response = self.client.agent.create(**config)
        return response

    def update_agent(self, agent_id: str, config: dict):
        """
        Update an existing agent in the Retell system.
        
        Args:
            agent_id (str): ID of the agent to update.
            config (dict): Updated configuration for the agent.
        
        Returns:
            dict: Response from the Retell API.
        """
        response = self.client.agent.update(agent_id=agent_id, **config)
        return response

    def create_llm(self, config: dict):
        """
        Create a new LLM in the Retell system.
        
        Args:
            config (dict): Configuration for the new LLM.
        
        Returns:
            dict: Response from the Retell API.
        """
        response = self.client.llm.create(**config)
        return response

    def update_llm(self, llm_id: str, config: dict):
        """
        Update an existing LLM in the Retell system.
        
        Args:
            llm_id (str): ID of the LLM to update.
            config (dict): Updated configuration for the LLM.
        
        Returns:
            dict: Response from the Retell API.
        """
        response = self.client.llm.update(llm_id=llm_id, **config)
        return response

    def add_phone_number(self, config: str):
        """
        Add a phone number to the Retell system.
        
        Args:
            config (str): Configuration for the phone number.
        
        Returns:
            dict: Response from the Retell API.
        """
        phone_number_response = self.client.phone_number.import_(**config)
        return phone_number_response

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
        
        Args:
            payload: Payload containing lead details.
        """
        pass

    def process_call_outputs(self, payload):
        """
        Process the outputs from the completed call.
        This method must be overridden in a subclass to implement specific pre-call logic.
        
        Args:
            payload: Payload containing call details.
        """
        pass

    def post_call_processing(self, call_outputs: dict):
        """
        Perform post-call processing to analyze results and update the CRM.
        This method must be overridden in a subclass to implement specific pre-call logic.
        
        Args:
            call_outputs (dict): Outputs from the call analysis.
        """
        pass

    def _validate_webhook(self, data):
        """
        Validate the webhook signature for authenticity.
        
        Args:
            data (dict): Webhook data received from Retell.
        
        Returns:
            bool: True if the signature is valid, False otherwise.
        """
        valid_signature = self.client.verify(
            json.dumps(data, separators=(",", ":"), ensure_ascii=False),
            api_key=str(os.getenv("RETELL_API_KEY")),
            signature=str(data.get("headers", {}).get("X-Retell-Signature")),
        )
        if not valid_signature:
            print("Received Unauthorized", data["event"], data["data"]["call_id"])
        return valid_signature

    def _handle_retell_event(self, event, data):
        """
        Handle specific events received from Retell.
        
        Args:
            event (str): The type of event received.
            data (dict): Event data payload.
        """
        if event == "call_started":
            print("Call started event", data["data"]["call_id"])
        elif event == "call_ended":
            print("Call ended event", data["data"]["call_id"])
        elif event == "call_analyzed":
            print("Call analyzed event", data["data"]["call_id"])

            # Post-call analysis and update CRM
            call_output = self.process_call_outputs(data["data"])
            self.post_call_processing(call_output)
        else:
            print("Unknown event", event)

    async def _handle_tool_call(self, data):
        """
        Handle requests to execute specific tools via the agent.
        
        Args:
            data (dict): Data containing the function name and arguments.
        
        Returns:
            dict: Result of the tool execution.
        """
        function_name = data.get("name")
        args = data.get("args", {})

        if function_name in self.allowed_tools:
            result = await self.allowed_tools[function_name](**args)
            return {"name": function_name, "result": result}
        else:
            return {"name": function_name, "result": "Unknown function"}
