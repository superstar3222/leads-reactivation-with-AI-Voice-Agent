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
                    leads.append({
                        "id": lead["id"],
                        "first_name": lead.get("firstName", ""),
                        "last_name": lead.get("lastName", ""),
                        "email": lead.get("email"),
                        "address": lead.get("address", ""),
                        "phone": lead.get("phone", "")
                    })
            return leads
        else:
            # Fetch leads matching the status
            records = crm_api.get_leads_by_status(status)  # Replace with your CRM API call
            return [
                {
                    "id": record["id"],
                    "first_name": record.get("firstName", ""),
                    "last_name": record.get("lastName", ""),
                    "email": record.get("email"),
                    "address": record.get("address", ""),
                    "phone": record.get("phone", "")
                }
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
By default, the `vapi_automation::evaluate_call` function uses a my own set of data fields (e.g., "Status", "Score", "Analysis Reports", "Outreach Report", "Last Contacted") when updating a CRM record. However, different CRMs or database schemas may use different field names or additional fields that need to be handled.

### Steps to Customize the `vapi_automation::evaluate_call` Function

1. **Identify the Fields in Your CRM**
   Each CRM or database may have different field names or additional fields. Start by identifying which fields you need to map from your system to the CRM. This may include:
   - Custom field names (e.g., `lead_score` instead of `Score`)
   - Additional fields (e.g., `custom_field_1`, `custom_field_2`)

2. **Modify the `new_data` Dictionary**
   The `new_data` dictionary in the `update_CRM` function is where the lead data is prepared before updating the CRM. You can modify this dictionary to include your custom fields.

   For example, if your CRM has a custom field `custom_lead_score` instead of `Score`, you can modify the dictionary like this:

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
- **Field Names**: Always check the database to ensure that the field names you're using match the database schema (names are case-sensitive).
