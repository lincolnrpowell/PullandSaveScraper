import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import os


# CREATE CSV FILES OF THE YARD INVENTORY
def make_file(location_name, url):
    print(f'Initializing request for {location_name} location...\n')

    init_fail = 'Initiation failed!\n'
    seperator = '\n---------------\n'

    # CALL REQUEST TO WEBSITE
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/123.0.0.0 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    page_count = None

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # GET TOTAL TABLE PAGES
        input_tags = soup.find_all("input", {"class": "form-control"})
        page_tag = input_tags[1]
        page_count = int(page_tag.get('data-pagecount'))

    else:
        # GET REQUEST FAILED
        print(f"{init_fail}Failed to fetch data from the URL:", url,
              f"\nResponse Status: {response.status_code}{seperator}")

    # TABLE DATA
    page_data = []
    page_index = 0
    start_index = 1

    # LOOP THROUGH ALL TABLE PAGES
    print(f'Scraping {page_count} pages from the {location_name} yard site.\nThis may take a moment...\n')
    while page_count > page_index:
        url_index = url + f'?start={start_index}'
        # SCRAPE TABLE DATA
        response = requests.get(url_index, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            tables = soup.find('table', 'table')
            df1 = pd.read_html(StringIO(str(tables)))
            out_put = df1[0]

            table = out_put[['Row', 'Vin', 'Year', 'Make', 'Model']]
            page_data.append(table)
            start_index += 50
            page_index += 1
        else:
            # REQUEST FAILED
            print(f"{init_fail}Failed to fetch data from the URL:", url,
                  f"\nResponse Status: {response.status_code}{seperator}")
    # ALL YARD DATA
    yard_inventory = pd.concat(page_data)

    # CREATE A NEW CSV FILE IN DATA_CACHE
    # ENSURE FOLDER EXISTS
    if not os.path.exists('data_cache'):
        os.makedirs('data_cache')

        # CONSTRUCT FULL FILE PATH
    file_path = os.path.join('data_cache', f'{location_name}_inventory.csv')

    # WRITE DATA TO CVS
    yard_inventory.to_csv(file_path, index=False)

    print(f'Data written to {location_name}_inventory.csv in data_cache folder.\n{location_name} initiation complete!'
          f'{seperator}')


# VIN DECODE FUNCTION (NHTSA API)
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


# GETS ENGINE DISPLACEMENT IN LITERS FROM VIN
def get_displacement(vin):
    results = vin_decode(vin)
    for result in results:
        if 'Variable' in result and 'Value' in result:
            if result['Variable'] == 'Displacement (L)':
                engine_displacement = result['Value']
                if engine_displacement is None:
                    engine_displacement = 0.0
                return round(float(engine_displacement), 1)


class CombinedInventory:
    def __init__(self, file1, file2):
        self.file1 = file1
        self.file2 = file2
        self.location1 = file1.split("_")[0]
        self.location2 = file2.split("_")[0]

        file_path1 = os.path.join('data_cache', f'{self.file1}')
        file_path2 = os.path.join('data_cache', f'{self.file2}')

        self.inventory1 = pd.read_csv(file_path1)
        self.inventory2 = pd.read_csv(file_path2)

        self.seperator = '\n---------------\n'

    def search(self, make=None, model=None, year=None):
        if make and model and year:
            if make.upper() == 'CHEVY':
                make = 'CHEVROLET'
            elif make.upper() == 'NISSAN' or make.upper() == 'DATSUN':
                make = 'DATSUN - NISSAN'
            else:
                make = make.upper()
            model = model.upper()
            year = int(year)

            results1 = self.inventory1[(self.inventory1['Make'] == f'{make}') &
                                       (self.inventory1['Model'] == f'{model}') &
                                       (self.inventory1['Year'] == year)]
            results2 = self.inventory2[(self.inventory2['Make'] == f'{make}') &
                                       (self.inventory2['Model'] == f'{model}') &
                                       (self.inventory2['Year'] == year)]
            count1 = results1.shape[0]
            count2 = results2.shape[0]

            output1 = f'{self.location1} inventory\nFound {count1} instances of {year} {make} {model}\n{results1}'
            output2 = f'{self.location2} inventory\nFound {count2} instances of {year} {make} {model}\n{results2}'

            if results1.empty and results2.empty:
                return f'No instances of {year} {make} {model} found in {self.location1} or {self.location2}'
            elif results1.empty:
                return f'No instance of {year} {make} {model} found in {self.location1}{self.seperator}{output2}'
            elif results2.empty:
                return f'{output1}{self.seperator}No instances of {year} {make} {model} found in {self.location2}'
            else:
                return f'{output1}{self.seperator}{output2}{self.seperator}'

        elif make and model:
            if make.upper() == 'CHEVY':
                make = 'CHEVROLET'
            elif make.upper() == 'NISSAN' or make.upper() == 'DATSUN':
                make = 'DATSUN - NISSAN'
            else:
                make = make.upper()

            model = model.upper()

            results1 = self.inventory1[(self.inventory1['Make'] == f'{make}') &
                                       (self.inventory1['Model'] == f'{model}')]
            results2 = self.inventory2[(self.inventory2['Make'] == f'{make}') &
                                       (self.inventory2['Model'] == f'{model}')]
            count1 = results1.shape[0]
            count2 = results2.shape[0]

            output1 = f'{self.location1} inventory\nFound {count1} instances of {make} {model}\n{results1}'
            output2 = f'{self.location2} inventory\nFound {count2} instances of {make} {model}\n{results2}'

            if results1.empty and results2.empty:
                return f'No instances of {make} {model} found in {self.location1} or {self.location2}'
            elif results1.empty:
                return f'No instance of {make} {model} found in {self.location1}{self.seperator}{output2}'
            elif results2.empty:
                return f'{output1}{self.seperator}No instances of {make} {model} found in {self.location2}'
            else:
                return f'{output1}{self.seperator}{output2}{self.seperator}'

        elif make and year:
            if make.upper() == 'CHEVY':
                make = 'CHEVROLET'
            elif make.upper() == 'NISSAN' or make.upper() == 'DATSUN':
                make = 'DATSUN - NISSAN'
            else:
                make = make.upper()

            year = int(year)

            results1 = self.inventory1[(self.inventory1['Make'] == f'{make}') &
                                       (self.inventory1['Year'] == year)]
            results2 = self.inventory2[(self.inventory2['Make'] == f'{make}') &
                                       (self.inventory2['Year'] == year)]
            count1 = results1.shape[0]
            count2 = results2.shape[0]

            output1 = f'{self.location1} inventory\nFound {count1} instances of {year} {make} \n{results1}'
            output2 = f'{self.location2} inventory\nFound {count2} instances of {year} {make} \n{results2}'

            if results1.empty and results2.empty:
                return f'No instances of {year} {make} found in {self.location1} or {self.location2}'
            elif results1.empty:
                return (f'No instance of {year} {make} found in {self.location1}{self.seperator}{output2}'
                        f'{self.seperator}')
            elif results2.empty:
                return (f'{output1}{self.seperator}No instances of {year} {make} found in {self.location2}'
                        f'{self.seperator}')
            else:
                return f'{output1}{self.seperator}{output2}{self.seperator}'

        elif model and year:
            model = model.upper()
            year = int(year)

            results1 = self.inventory1[(self.inventory1['Year'] == f'{year}') &
                                       (self.inventory1['Model'] == f'{model}')]
            results2 = self.inventory2[(self.inventory2['Year'] == f'{year}') &
                                       (self.inventory2['Model'] == f'{model}')]
            count1 = results1.shape[0]
            count2 = results2.shape[0]

            output1 = f'{self.location1} inventory\nFound {count1} instances of {year} {model}\n{results1}'
            output2 = f'{self.location2} inventory\nFound {count2} instances of {year} {model}\n{results2}'

            if results1.empty and results2.empty:
                return f'No instances of {year} {model} found in {self.location1} or {self.location2}'
            elif results1.empty:
                return f'No instance of {year} {model} found in {self.location1}{self.seperator}{output2}'
            elif results2.empty:
                return f'{output1}{self.seperator}No instances of {year} {model} found in {self.location2}'
            else:
                return f'{output1}{self.seperator}{output2}{self.seperator}'

        elif make:
            if make.upper() == 'CHEVY':
                make = 'CHEVROLET'
            elif make.upper() == 'NISSAN' or make.upper() == 'DATSUN':
                make = 'DATSUN - NISSAN'
            else:
                make = make.upper()

            results1 = self.inventory1[self.inventory1['Make'] == f'{make}']
            results2 = self.inventory2[self.inventory2['Make'] == f'{make}']
            count1 = results1.shape[0]
            count2 = results2.shape[0]

            output1 = f'{self.location1} inventory\nFound {count1} instances of {make}\n{results1}'
            output2 = f'{self.location2} inventory\nFound {count2} instances of {make}\n{results2}'

            if results1.empty and results2.empty:
                return f'No instances of the make {make} found in {self.location1} or {self.location2}'
            elif results1.empty:
                return f'No instance of the make "{make}" found in {self.location1}\n {output2}'
            elif results2.empty:
                return f'{output1}\nNo instance of the make "{make}" found in {self.location2}'
            else:
                return f'{output1}{self.seperator}{output2}{self.seperator}'

        elif model:
            model = model.upper()

            results1 = self.inventory1[self.inventory1['Model'] == f'{model}']
            results2 = self.inventory2[self.inventory2['Model'] == f'{model}']
            count1 = results1.shape[0]
            count2 = results2.shape[0]

            output1 = f'{self.location1} inventory\nFound {count1} instances of {model}\n{results1}'
            output2 = f'{self.location2} inventory\nFound {count2} instances of {model}\n{results2}'

            if results1.empty and results2.empty:
                return f'No instances of the model {model} found in {self.location1} or {self.location2}{self.seperator}'
            elif results1.empty:
                return (f'No instance of the model "{model}" found in {self.location1}{self.seperator}'
                        f'{output2}{self.seperator}')
            elif results2.empty:
                return (f'{output1}{self.seperator}No instance of the model "{model}" found in {self.location2}'
                        f'{self.seperator}')
            else:
                return f'{output1}{self.seperator}{output2}{self.seperator}'
        elif year:
            year = int(year)
            results1 = self.inventory1[self.inventory1['Year'] == year]
            results2 = self.inventory2[self.inventory2['Year'] == year]
            count1 = results1.shape[0]
            count2 = results2.shape[0]

            output1 = f'{self.location1} inventory\nFound {count1} instances of {year}\n{results1}'
            output2 = f'{self.location2} inventory\nFound {count2} instances of {year}\n{results2}'

            if results1.empty and results2.empty:
                return f'No instances of the year {year} found in {self.location1} or {self.location2}{self.seperator}'
            elif results1.empty:
                return (f'No instance of the year "{year}" found in {self.location1}{self.seperator}'
                        f'{output2}{self.seperator}')
            elif results2.empty:
                return (f'{output1}{self.seperator}No instance of the year "{year}" found in {self.location2}'
                        f'{self.seperator}')
            else:
                return f'{output1}{self.seperator}{output2}{self.seperator}'

        else:
            return (f'{self.location1} inventory\n{self.inventory1}{self.seperator}{self.location2} inventory'
                    f'\n{self.inventory2}')

    # SEARCH THROUGH INVENTORY FOR ENGINE BY VEHICLE MAKE AND ENGINE DISPLACEMENT OR CYLINDER NUMBER
    def search_engine(self, make, size):
        if make.upper() == 'CHEVY':
            make = 'CHEVROLET'
        elif make.upper() == 'NISSAN' or make.upper() == 'DATSUN':
            make = 'DATSUN - NISSAN'
        else:
            make = make.upper()

        results1 = self.inventory1[self.inventory1['Make'] == f'{make}']
        results2 = self.inventory2[self.inventory2['Make'] == f'{make}']

        df_copy1 = results1.copy()
        df_copy2 = results2.copy()

        print(f'Sending {results1.shape[0] + results2.shape[0]} items to the NHTSA API\nThis may take a few moments...'
              f'\n---------------')

        df_copy1['Engine'] = df_copy1['Vin'].apply(get_displacement)
        df_copy2['Engine'] = df_copy2['Vin'].apply(get_displacement)

        out_putdf1 = df_copy1[df_copy1['Engine'] == size]
        out_putdf2 = df_copy2[df_copy2['Engine'] == size]
        count1 = out_putdf1.shape[0]
        count2 = out_putdf2.shape[0]

        out_put1 = f'{self.location1} inventory\nFound {count1} instances of {make} {size}L\n{out_putdf1}'
        out_put2 = f'{self.location2} inventory\nFound {count2} instances of {make} {size}L\n{out_putdf2}'

        if count1 == 0 and count2 == 0:
            return (f'No instances of a {make} {size}L found in {self.location1} or {self.location2}'
                    f'{self.seperator}')
        elif count1 ==0 :
            return (f'No instances of a {make} {size}L found in {self.location1}{self.seperator}{out_put2}'
                    f'{self.seperator}')
        elif count2 == 0:
            return (f'{out_put1}{self.seperator}No instances of a {make} {size}L found in {self.location2}'
                    f'{self.seperator}')
        else:
            return f'{out_put1}{self.seperator}{out_put2}{self.seperator}'
