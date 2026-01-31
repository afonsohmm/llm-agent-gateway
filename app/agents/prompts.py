from typing import List, Dict, Any, Optional
import json

def construct_prompt(
    instruction: str,
    data: Optional[Union[Dict, str]],
    provider: str,
    response_format: str,
    json_schema: Optional[Dict[str, Any]] = None
) -> List[Dict[str, str]]:
    """
    Constructs a list of messages for the LLM based on the input.
    """
    messages = []
    
    # System Prompt
    system_content = "You are a helpful assistant. Follow the user's instructions carefully."
    if response_format == 'json':
        system_content += "\nYour response MUST be a valid JSON object."
        if json_schema:
            system_content += f"\nAdhere to the following JSON schema:\n{json.dumps(json_schema)}"
            
    messages.append({"role": "system", "content": system_content})

    # User Prompt - Instruction
    messages.append({"role": "user", "content": instruction})

    # User Prompt - Data
    if data:
        if isinstance(data, dict):
            data_content = f"Here is the data to process:\n```json\n{json.dumps(data, indent=2)}\n```"
        else:
            data_content = f"Here is the data to process:\n{data}"
        messages.append({"role": "user", "content": data_content})
        
    return messages
