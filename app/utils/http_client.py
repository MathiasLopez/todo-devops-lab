import httpx

def get_http_client():
    return httpx.AsyncClient(timeout=10.0, verify=True)
