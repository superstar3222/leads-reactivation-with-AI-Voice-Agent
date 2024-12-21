import json
from datetime import datetime
from litellm import completion
from pydantic import BaseModel, Field

# Define the base information needed about the lead
class Lead(BaseModel):
    id: str = Field(..., description="The unique identifier for the lead being processed")
    first_name: str = Field(..., description="The first name of the lead")
    last_name: str = Field(..., description="The last name of the lead")
    address: str = Field(..., description="The address of the lead")
    email: str = Field(..., description="The email address of the lead")
    phone: str = Field(..., description="The phone number of the lead")

def get_current_date_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def calculate_duration_in_minutes(started_at, ended_at) -> float:
    # Define the format for parsing the datetime strings
    datetime_format = "%Y-%m-%dT%H:%M:%SZ"
    
    # Convert the datetime strings to datetime objects
    start_time = datetime.strptime(started_at, datetime_format)
    end_time = datetime.strptime(ended_at, datetime_format)
    
    # Calculate the difference in minutes
    duration = (end_time - start_time).total_seconds() / 60
    
    return duration

def invoke_llm(
    system_prompt, 
    user_message, 
    model="gpt-4o-mini", 
    response_format=None, 
    json_output=False
):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    response = completion(
        model=model,
        messages=messages,
        temperature=0.1,
        response_format=response_format
    )
    output = response.choices[0].message.content
    
    if json_output:
        return json.loads(output)
    return output