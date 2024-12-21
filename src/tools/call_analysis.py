from typing import Optional
from pydantic import BaseModel, Field
from src.utils import invoke_llm
from src.prompts import CALL_ANALYSIS_PROMPT


class CallAnalysisOutput(BaseModel):
    """Response model for the Sales Call Analysis Specialist."""
    
    summary: str = Field(
        ..., description="A concise summary highlighting the key talking points and interactions during the call."
    )
    interested: str = Field(
        ..., description="Determination of the lead's interest level: 'Interested', 'Not Interested', or 'Undecided'."
    )
    justification: Optional[str] = Field(
        default=None, description="Justification for the interest evaluation, providing context from the call transcript."
    )

def analyze_call_transcript(lead_name, transcript):
    # Can include other information about the lead like previous engagements to help analysis
    # For now just include the name
    inputs = (
        f"# Lead Name: {lead_name}\n"
        f"# Call Transcript:\n {transcript}"
    )
    call_analysis = invoke_llm(
        system_prompt=CALL_ANALYSIS_PROMPT, 
        user_message=inputs,
        response_format=CallAnalysisOutput,
        json_output=True
    )
    
    return call_analysis


