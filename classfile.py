import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import time
import os


# CREATE CSV FILES OF THE YARD INVENTORY
class InventoryInit:
    def __init__(self, location_name, url):
        # NAME THE OBJ
        self.name = location_name
        self.url = url
        print(f'Initializing request for {self.name} location...\n')

        init_fail = 'Initiation failed!\n'

        # CALL REQUEST TO WEBSITE
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/123.0.0.0 Safari/537.36'
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # GET TOTAL TABLE PAGES
            input_tags = soup.find_all("input", {"class": "form-control"})
            page_tag = input_tags[1]
            page_count = page_tag.get('data-pagecount')

            self.page_count = int(page_count)

        else:
            # GET REQUEST FAILED
            print(f"{init_fail}Failed to fetch data from the URL:", url,
                  f"\nResponse Status: {response.status_code}\n--------------------")

        # TABLE DATA
        page_data = []
        total_page_index = self.page_count
        page_index = 0
        start_index = 1

        # LOOP THROUGH ALL TABLE PAGES
        print(f'Scraping {self.page_count} pages from the {self.name} yard site.\nThis may take a moment...\n')
        while total_page_index > page_index:
            url = self.url + f'?start={start_index}'
            # SCRAPE TABLE DATA
            response = requests.get(url, headers=headers)
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
                      f"\nResponse Status: {response.status_code}\n--------------------")
        # ALL DATA
        yard_inventory = pd.concat(page_data)

        # CREATE A NEW CSV FILE IN DATA_CACHE
        # ENSURE FOLDER EXISTS
        if not os.path.exists('data_cache'):
            os.makedirs('data_cache')

            # CONSTRUCT FULL FILE PATH
        file_path = os.path.join('data_cache', f'{self.name}_inventory.csv')

        # WRITE DATA TO CVS
        yard_inventory.to_csv(file_path, index=False)

        time.sleep(2)
        print(f'Data written to {self.name}_inventory.csv in data_cache folder.\n{self.name} initiation complete!'
              f'\n--------------------')


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

    # SEARCH BY MAKE
    def search_make(self, make):
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
            return f'No instances of {make} found in {self.location1} or {self.location2}'
        elif results1.empty:
            return f'No instance of the make "{make}" found in {self.location1}\n {output2}'
        elif results2.empty:
            return f'{output1}\nNo instance of the make "{make}" found in {self.location2}'
        else:
            return f'{output1}\n---------------\n{output2}\n---------------'

    # SEARCH BY MODEL
    def search_model(self, model):
        model = model.upper()

        results1 = self.inventory1[self.inventory1['Model'] == f'{model}']
        results2 = self.inventory2[self.inventory2['Model'] == f'{model}']
        count1 = results1.shape[0]
        count2 = results2.shape[0]

        output1 = f'{self.location1} inventory\nFound {count1} instances of {model}\n{results1}'
        output2 = f'{self.location2} inventory\nFound {count2} instances of {model}\n{results2}'

        if results1.empty and results2.empty:
            return f'No instances of {model} found in {self.location1} or {self.location2}\n---------------'
        elif results1.empty:
            return (f'No instance of the make "{model}" found in {self.location1}\n---------------\n'
                    f'{output2}\n---------------')
        elif results2.empty:
            return (f'{output1}\n---------------\nNo instance of the make "{model}" found in {self.location2}'
                    f'\n---------------')
        else:
            return f'{output1}\n---------------\n{output2}\n---------------'

    def search_year(self, year):
        year = int(year)
        results1 = self.inventory1[self.inventory1['Year'] == year]
        results2 = self.inventory2[self.inventory2['Year'] == year]
        count1 = results1.shape[0]
        count2 = results2.shape[0]

        output1 = f'{self.location1} inventory\nFound {count1} instances of {year}\n{results1}'
        output2 = f'{self.location2} inventory\nFound {count2} instances of {year}\n{results2}'

        if results1.empty and results2.empty:
            return f'No instances of {year} found in {self.location1} or {self.location2}\n---------------'
        elif results1.empty:
            return (f'No instance of the make "{year}" found in {self.location1}\n---------------\n'
                    f'{output2}\n---------------')
        elif results2.empty:
            return (f'{output1}\n---------------\nNo instance of the make "{year}" found in {self.location2}'
                    f'\n---------------')
        else:
            return f'{output1}\n---------------\n{output2}\n---------------'

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
                return f'No instance of {year} {make} {model} found in {self.location1}\n---------------\n{output2}'
            elif results2.empty:
                return f'{output1}\n---------------\nNo instances of {year} {make} {model} found in {self.location2}'
            else:
                return f'{output1}\n---------------\n{output2}\n---------------'

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
                return f'No instance of {make} {model} found in {self.location1}\n---------------\n{output2}'
            elif results2.empty:
                return f'{output1}\n---------------\nNo instances of {make} {model} found in {self.location2}'
            else:
                return f'{output1}\n---------------\n{output2}\n---------------'

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
                return (f'No instance of {year} {make} found in {self.location1}\n---------------\n{output2}'
                        f'\n---------------')
            elif results2.empty:
                return (f'{output1}\n---------------\nNo instances of {year} {make} found in {self.location2}'
                        f'\n---------------')
            else:
                return f'{output1}\n---------------\n{output2}\n---------------'

        elif model and year:
            model = model.upper()
            year = int(year)

            results1 = self.inventory1[(self.inventory1['Year'] == f'{year}') &
                                       (self.inventory1['Model'] == f'{model}')]
            results2 = self.inventory2[(self.inventory2['year'] == f'{year}') &
                                       (self.inventory2['Model'] == f'{model}')]
            count1 = results1.shape[0]
            count2 = results2.shape[0]

            output1 = f'{self.location1} inventory\nFound {count1} instances of {year} {model}\n{results1}'
            output2 = f'{self.location2} inventory\nFound {count2} instances of {year} {model}\n{results2}'

            if results1.empty and results2.empty:
                return f'No instances of {year} {model} found in {self.location1} or {self.location2}'
            elif results1.empty:
                return f'No instance of {year} {model} found in {self.location1}\n---------------\n{output2}'
            elif results2.empty:
                return f'{output1}\n---------------\nNo instances of {year} {model} found in {self.location2}'
            else:
                return f'{output1}\n---------------\n{output2}\n---------------'

        elif make:
            return self.search_make(make)

        elif model:
            return self.search_model(model)
        elif year:
            return self.search_year(year)

        else:
            return (f'{self.location1} inventory\n{self.inventory1}\n---------------\n{self.location2} inventory'
                    f'\n{self.inventory2}')

    def search_engine(self, size, make):
        pass
