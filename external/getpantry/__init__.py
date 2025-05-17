from requests import get
import json

def get_pantry_data_by_basket(token: str, basket_name: str):
    """Get pantry data from a URL"""
    url = f"https://getpantry.cloud/apiv1/pantry/{token}/basket/{basket_name}"
    response = get(url)
    return response.json()