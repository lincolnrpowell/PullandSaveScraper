# FILE FOR TESTING CODE

import requests
import os
import pandas as pd

file_path = os.path.join('data_cache', 'Spokane_inventory.csv')

test_inventory = pd.read_csv(file_path)

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
                if engine_displacement is None:
                    engine_displacement = 0.0
                return round(float(engine_displacement), 1)

def search_year(year):
    pass
def serch_make(make):
    pass
def search_model(model):
    pass
def search_engine(liters):
    pass


