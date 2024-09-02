import requests

class BarcodeLookup:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://barcode-lookup.p.rapidapi.com/v3/products"

    def lookup(self, barcode):
        headers = {
            'x-rapidapi-host': 'barcode-lookup.p.rapidapi.com',
            'x-rapidapi-key': self.api_key
        }

        params = {
            'barcode': barcode
        }

        response = requests.get(self.api_url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

if __name__ == "__main__":
    api_key = "f7cab8925dmsh2c2525c3bba4c34p16957fjsn5e1df9455a57"
    barcode_lookup = BarcodeLookup(api_key)

    barcode = "9780439625593"
    try:
        product_info = barcode_lookup.lookup(barcode)
        print(product_info)
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"An error occurred: {err}")
