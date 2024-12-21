# Customization

## Customizing CRM Integrations

### Overview
To integrate your custom CRM with the `LeadLoaderBase` class, you need to inherit from `LeadLoaderBase` and implement two methods:
- `fetch_records`: Fetches the leads matching the given status.
- `update_record`: Updates the lead record with new fields.

By default, the available statuses used in the `LeadLoaderBase` class are:
```python
available_statuses = ["NEW","CONTACTED"]
```
However, these statuses can be customized to match the specific lead status values in your CRM.

### Steps to Add a Custom CRM Integration

1. **Create a New Class for Your CRM**
   Inherit from `LeadLoaderBase` and implement the two abstract methods: `fetch_records` and `update_record`.

   ```python
   class CustomCRMLeadLoader(LeadLoaderBase):
       def __init__(self, api_key, custom_parameter):
           # Initialize any API clients or configurations here
           self.api_key = api_key
           self.custom_parameter = custom_parameter
    
    def fetch_records(self, lead_ids=None, status="NEW"):
        """
        Fetch leads from your CRM.
        - If `lead_ids` is provided, fetch those specific leads.
        - Otherwise, fetch leads matching the given status.
        """
        if lead_ids:
            leads = []
            for lead_id in lead_ids:
                lead = crm_api.get_lead(lead_id)  # Replace with your CRM API call
                if lead:
                    # Extract all fields provided by database
                    lead = {"id": record["id"], **record.get("fields", {})}
            return leads
        else:
            # Fetch leads matching the status
            records = crm_api.get_leads_by_status(status)  # Replace with your CRM API call
            return [
                {"id": record["id"], **record.get("fields", {})}  # Extract all fields provided by database dynamically
                for record in records
            ]

    def update_record(self, lead_id, updates: dict):
        """
        Update a single lead record in your CRM.

        Args:
            lead_id (str): ID of the lead to update.
            updates (dict): Dictionary of fields to update.

        Returns:
            dict: Updated lead record.
        """
        lead = crm_api.get_lead(lead_id)  # Replace with your CRM API call
        if not lead:
            raise ValueError(f"Lead with ID {lead_id} not found.")
        updated_lead = crm_api.update_lead(lead_id, updates)  # Replace with your CRM API call
        return updated_lead
   ```

2. **Customizing Lead Statuses**
   If your CRM uses different statuses or additional ones, you can customize this list to match your system. For example, if your CRM uses statuses such as `"IN_PROGRESS"` or `"CALLED"`, you can update the `available_statuses` like this:

   ```python
   available_statuses = ["NEW", "CALLED"]
   ```

   Make sure to update the `fetch_records` method to reflect these changes. For example, if you want to fetch leads with a status of `"IN_PROGRESS"`, you can call `fetch_records(status="IN_PROGRESS")`.

---

## Customizing your CRM Field Names

### Overview
By default, the `vapi_automation::load_leads` and `vapi_automation::evaluate_call_and_update_crm` functions use field names that are specific to my own database (e.g., "Status", "Score", "Analysis Reports", "Outreach Report", "Last Contacted"). However, if your CRM or database uses different field names or additional fields, you will need to update the code to reflect those differences.

### Steps to Customize the Functions

1. **Modify the `vapi_automation::load_leads` Function**
   The `load_leads` function fetches lead data from a database and structures it using specific field names (e.g., "First Name", "Last Name", "Email", etc.). If your database uses different field names, you will need to modify this function accordingly.

   For example, if your database uses `first_name` instead of `First Name`, update the code like this:

   ```python
    def load_leads(self, lead_ids):
        raw_leads = self.lead_loader.fetch_records(lead_ids=lead_ids)
        if not raw_leads:
            return []
        
        # Structure the leads
        leads = [
            Lead(
                id=lead["id"],
                first_name=lead.get("first_name", ""),
                last_name=lead.get("last_name", ""),
                address=lead.get("address", ""),
                email=lead.get("email", ""),
                phone=lead.get("phone", ""),
            )
            for lead in raw_leads
        ]
        print(f"Loaded {len(leads)} leads: {leads}")
        
        return leads
   ```

   **IMPORTANT**: The provided field names are based on the structure I use for my own database. If your database uses different field names, just update the code to reflect that.

2. **Modify the `vapi_automation::evaluate_call_and_update_crm` Function**
   In the `evaluate_call_and_update_crm` function, the `new_data` dictionary is used to prepare lead data before updating the CRM. You can modify this dictionary to include the correct field names for your CRM. For example, if your CRM has a custom field `custom_lead_score` instead of `Score`, you can modify the dictionary like this:

   ```python
    updates = {
        "Status": "CONTACTED",
        "Call ID": call_outputs["call_id"],
        "Call Status": call_outputs["status"],
        "Duration": call_outputs["duration"],
        "Cost": call_outputs["cost"],
        "End Reason": call_outputs["endedReason"],
        "Transcript": call_outputs["transcript"],
        "Call Summary": output.get("call_summary"),
        "Interested": output.get("lead_interested"),
        "Comment": output.get("justification"),
        "custom_field_1": "custom_field_1_value",
        ...
    }
   ```

### Notes:
- **Field Names**: The provided field names are based on the structure I use for my own database. If your database uses different field names, just update the code to reflect that.