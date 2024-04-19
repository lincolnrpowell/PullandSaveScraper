#FILE FOR TESTING CODE

import requests


def vin_decode(vin):
    url = f'https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'Results' in data:
            results = data['Results']
            return results
        else:
            return 'VIN decoding failed'
    else:
        return f'Error: Failed to fetch data from NHTSA API\nError code: {response.status_code}'

def get_displacement(vin):
    results = vin_decode(vin)
    for result in results:
        if 'Variable' in result and 'Value' in result:
            if result['Variable'] == 'Displacement (L)':
                engine_displacement = result['Value']
                return engine_displacement

print(get_displacement("4S3BH686827608971"))
