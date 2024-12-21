import os
from src.base.voice_agent_providers.vapi.vapi_ai import VapiAI
from src.tools.calendar_tool import book_appointement
from src.tools.call_analysis import analyze_call_transcript
from src.utils import Lead, get_current_date_time, calculate_duration_in_minutes


# Tools used directly by the AI VOICE agent
# For this case, the agent needs only a Book appointement tool
TOOLS = {
    "bookAppointment": book_appointement
}

class VapiAutomation(VapiAI):
    def __init__(self, lead_loader):
        """
        Initialize the class VapiAutomation class.

        Args:
            lead_loader: A lead loader instance for managing lead data.
        """
        super().__init__(tools=TOOLS)  # Initialize the base class
        self.lead_loader = lead_loader 
        
    def load_leads(self, lead_ids):
        raw_leads = self.lead_loader.fetch_records(lead_ids=lead_ids)
        if not raw_leads:
            return []
        
        # Structure the leads
        leads = [
            Lead(
                id=lead["id"],
                first_name=lead.get("First Name", ""),
                last_name=lead.get("Last Name", ""),
                address=lead.get("Address", ""),
                email=lead.get("Email", ""),
                phone=lead.get("Phone", ""),
            )
            for lead in raw_leads
        ]
        print(f"Loaded {len(leads)} leads\n: {leads}")
        
        return leads

    def pre_call_processing(self, payload):
        pass
       
    def get_call_input_params(self, lead_data: dict) -> dict:
        """
        Build the payload required to initiate a call via Vapi.

        Args:
            lead_data (dict): Lead data containing phone number and other details.
        
        Returns:
            dict: A formatted payload to pass to the Vapi call API.
        """
        return {
            "phone_number_id": os.getenv("VAPI_PHONE_ID"),
            "assistant_id": os.getenv("VAPI_ASSISTANT_ID"),
            "customer": {
                "number": lead_data.phone,
            },
            "assistant_overrides": {
                "variable_values": {
                    "leadID": lead_data.id,
                    "firstName": lead_data.first_name,
                    "lastName": lead_data.last_name,
                    "email": lead_data.email,
                    "address": lead_data.address,
                    "date": get_current_date_time()
                }
            }
        }

    def process_call_outputs(self, response: dict) -> dict:
        """
        Process the response from a Vapi call and extract relevant details.

        Args:
            response (dict): The raw response from the Vapi API.
        
        Returns:
            dict: Processed call outputs.
        """
        return {
            "call_id": response["call"]["id"],
            "status": response["call"]["status"],
            "duration": response["durationMinutes"],
            "cost": response["cost"],
            "endedReason": response["endedReason"],
            "transcript": response["artifact"]["transcript"],
            "lead_info": response["call"]["assistantOverrides"]["variableValues"]
        }

    def evaluate_call_and_update_crm(self, call_outputs: dict) -> dict:
        """
        Perform post-call analysis and update the CRM with the results.

        Args:
            call_outputs (dict): Processed call outputs.
        
        Returns:
            dict: Updated lead information.
        """
        # Transcript analysis
        lead_name = f'{call_outputs["lead_info"]["firstName"]} {call_outputs["lead_info"]["lastName"]}'
        output = analyze_call_transcript(lead_name, call_outputs['transcript'])

        # Update CRM, Make sure to use the correct field names
        updates = {
            "Status": "CONTACTED",
            "Call ID": call_outputs["call_id"],
            "Call Status": call_outputs["status"],
            "Duration": call_outputs["duration"],
            "Cost": call_outputs["cost"],
            "End Reason": call_outputs["endedReason"],
            "Transcript": call_outputs["transcript"],
            "Call Summary": output.get("summary"),
            "Interested": output.get("interested"),
            "Comment": output.get("justification")
        }

        self.lead_loader.update_record(call_outputs["lead_info"]["leadID"], updates)

        return updates
    
    def post_call_processing(self, call_outputs):
        """
        Post call analysis function invoked by the base VAPIAI class
        upon receiving the end call event for Vapi

        Args:
            call_outputs (dict): Processed call outputs from the Vapi.
        """
        self.evaluate_call_and_update_crm(call_outputs)
