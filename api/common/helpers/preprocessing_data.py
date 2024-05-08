

def convert_raw_suburbs(raw_suburbs) -> str:
    if isinstance(raw_suburbs, dict):

        suburb = raw_suburbs.get("suburb", "")
        state = raw_suburbs.get("state", "")
        post_code = raw_suburbs.get("postCode", "")

        if suburb and state and post_code:
            combined = f"{suburb}, {state} {post_code}"
            return combined
        else:
            return None

    elif isinstance(raw_suburbs, list):
        return raw_suburbs[0]
