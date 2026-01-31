import json

def estimate_tokens(data: any) -> int:
    """
    A very rough heuristic to estimate the number of tokens.
    A common rule of thumb is 1 token ~ 4 characters for English text.
    For JSON, we can just count characters as a rough proxy.
    """
    if not data:
        return 0
    
    text = ""
    if isinstance(data, dict):
        text = json.dumps(data)
    elif isinstance(data, str):
        text = data
    else:
        text = str(data)

    # 1 token ~= 4 chars
    return len(text) // 4
