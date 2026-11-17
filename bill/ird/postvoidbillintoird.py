import requests

IRD_CODE_MEANINGS = {
    100: "API credentials do not match",
    101: "Bill already exists",
    102: "Exception while saving bill details",
    103: "Unknown exception",
    104: "Model invalid",
    200: "Success",
}

def post_credit_note_to_ird(payload):
    """
    Posts a credit note (void) to IRD CBMS.
    Returns a dict: {success: bool, code: int|None, message: str, raw: str}
    """
    cbms_url = "https://cbapi.ird.gov.np/api/billreturn"
    headers = {"Content-Type": "application/json"}

    try:
        r = requests.post(cbms_url, json=payload, headers=headers, timeout=10)
    except Exception as e:
        return {
            "success": False,
            "code": None,
            "message": f"Network error: {e}",
            "raw": None,
        }

    # HTTP-level failure
    if r.status_code != 200:
        return {
            "success": False,
            "code": None,
            "message": f"HTTP {r.status_code}: {r.text}",
            "raw": r.text,
        }

    # IRD returns a numeric code in the body
    raw = (r.text or "").strip()
    try:
        code = int(raw)
    except (ValueError, TypeError):
        return {
            "success": False,
            "code": None,
            "message": f"Unparseable IRD response: {raw!r}",
            "raw": raw,
        }

    message = IRD_CODE_MEANINGS.get(code, f"Unknown IRD code {code}")

    return {
        "success": code == 200,
        "code": code,
        "message": message,
        "raw": raw,
    }