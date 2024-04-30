import threading
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import os
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import tkinter.scrolledtext as scrolledtext


# VIN DECODE FUNCTION (NHTSA API)
def vin_decode(vin):
    url = (
        f'https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json'
    )
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'Results' in data:
            results = data['Results']
            return results
        else:
            return 'VIN decoding failed'
    else:
        return (
            f'Error: Failed to fetch data from NHTSA API'
            f'\nError code: {response.status_code}'
        )


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


# COUNT THE LINES IN TKINTER TEXT WIDGET
def count_lines(text_widget):
    last_line_index = text_widget.index("end-1c")
    line_number = last_line_index.split('.')[0]
    return int(line_number)


# GUI
class App(ctk.CTk):
    def __init__(self):
        # Main setup
        super().__init__()
        self.title('P&S Inventory Search')
        self.geometry('520x600')
        self.minsize(520, 600)
        self.appearance = 'dark'
        ctk.set_appearance_mode(f'{self.appearance}')
        ctk.set_default_color_theme('dark-blue')

        self.how_to_use = ('How to use:'
                           '\n\n-Click File > Update Inventory... to get '
                           'latest yard inventory'
                           '\n-Enter search parameters into the input fields '
                           'then click "Search"'
                           '\n-Results will display here'
                           '\n-CLick the "Clear" button to clear entry '
                           'fields and search display'
                           '\n\nNote: "Engine(L)" needs at least a "Make" '
                           'parameter to function'
                           )

        # Menu bar
        self.menubar = tk.Menu(self)

        self.file_menu = tk.Menu(self.menubar,
                                 tearoff=0,
                                 bg='#333333',
                                 fg='white'
                                 )
        self.file_menu.add_command(label="Update Inventory...",
                                   command=self.update_inventory_button_func
                                   )
        self.file_menu.add_separator()
        self.file_menu.add_command(label='How to use',
                                   command=self.how_to_use_func
                                   )
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Close",
                                   command=exit
                                   )
        self.menubar.add_cascade(menu=self.file_menu,
                                 label='File'
                                 )
        self.view_menu = tk.Menu(self.menubar,
                                 tearoff=0,
                                 bg='#333333',
                                 fg='white'
                                 )
        self.theme_menu = tk.Menu(self.view_menu,
                                  tearoff=0,
                                  bg='#333333',
                                  fg='white'
                                  )
        self.menubar.add_cascade(menu=self.view_menu,
                                 label='View'
                                 )
        self.view_menu.add_cascade(menu=self.theme_menu,
                                   label='Change theme'
                                   )
        self.theme_menu.add_command(label='Dark theme',
                                    command=self.dark_theme
                                    )
        self.theme_menu.add_separator()
        self.theme_menu.add_command(label='Light theme',
                                    command=self.light_theme
                                    )
        self.config(menu=self.menubar)

        # Create grid
        self.columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)

        # Labels
        search_label = ctk.CTkLabel(self,
                                    text="Pull and Save Inventory Search",
                                    font=("Consolas", 18)
                                    )
        search_label.grid(row=0,
                          column=0,
                          padx=10,
                          pady=5,
                          sticky="W" + "E" + "N" + "S"
                          )
        year_label = ctk.CTkLabel(self,
                                  text="Year:",
                                  font=('Consolas', 14)
                                  )
        year_label.grid(row=1,
                        column=0,
                        padx=10,
                        pady=5,
                        sticky="W" + "E" + "N" + "S"
                        )
        make_label = ctk.CTkLabel(self,
                                  text="Make:",
                                  font=('Consolas', 14)
                                  )
        make_label.grid(row=2,
                        column=0,
                        padx=10,
                        pady=5,
                        sticky="W" + "E" + "N" + "S"
                        )
        model_label = ctk.CTkLabel(self,
                                   text="Model:",
                                   font=('Consolas',
                                         14)
                                   )
        model_label.grid(row=3,
                         column=0,
                         padx=10,
                         pady=5,
                         sticky="W" + "E" + "N" + "S"
                         )
        engine_label = ctk.CTkLabel(self,
                                    text="Engine(L):",
                                    font=('Consolas', 14)
                                    )
        engine_label.grid(row=4,
                          column=0,
                          padx=10,
                          pady=5,
                          sticky="W" + "E" + "N" + "S"
                          )

        # Entry boxes
        self.year_entry = ctk.CTkEntry(self)
        self.year_entry.grid(row=1,
                             column=1,
                             padx=10,
                             pady=5,
                             sticky="W" + "E" + "N" + "S"
                             )
        self.make_entry = ctk.CTkEntry(self)
        self.make_entry.grid(row=2,
                             column=1,
                             padx=10,
                             pady=5,
                             sticky="W" + "E" + "N" + "S"
                             )
        self.model_entry = ctk.CTkEntry(self)
        self.model_entry.grid(row=3,
                              column=1,
                              padx=10,
                              pady=5,
                              sticky="W" + "E" + "N" + "S"
                              )
        self.engine_entry = ctk.CTkEntry(self)
        self.engine_entry.grid(row=4,
                               column=1,
                               padx=10,
                               pady=5,
                               sticky="W" + "E" + "N" + "S"
                               )

        # Buttons
        self.search_button = ctk.CTkButton(self,
                                           text="Search",
                                           font=('Consolas', 14),
                                           command=self.search_button_fuc
                                           )
        self.search_button.grid(row=5,
                                column=0,
                                padx=10,
                                pady=5,
                                columnspan=1,
                                sticky="W" + "E" + "N" + "S")
        self.clear_button = ctk.CTkButton(self,
                                          text="Clear",
                                          font=('Consolas', 14),
                                          command=self.clear_params
                                          )
        self.clear_button.grid(row=5,
                               column=1,
                               padx=10,
                               pady=5,
                               columnspan=1,
                               sticky="W" + "E" + "N" + "S"
                               )

        # Search display
        self.text_display = scrolledtext.ScrolledText(self)
        self.text_display.config(font=('Consolas', 12),
                                 background='#333333',
                                 foreground='white'
                                 )
        self.text_display.insert('1.0', self.how_to_use)
        self.text_display.config(state=tk.DISABLED)
        self.text_display.grid(row=6,
                               column=0,
                               columnspan=4,
                               padx=10,
                               pady=5,
                               sticky="W" + "E" + "N" + "S"
                               )

        # Run
        self.mainloop()

    def dark_theme(self):
        ctk.set_appearance_mode('dark')
        self.text_display.config(font=('Consolas', 12),
                                 bg='#333333',
                                 fg='white'
                                 )
        self.file_menu.config(bg='#333333',
                              fg='white'
                              )
        self.view_menu.config(bg='#333333',
                              fg='white'
                              )
        self.theme_menu.config(bg='#333333',
                               fg='white'
                               )

    def light_theme(self):
        ctk.set_appearance_mode('light')
        self.text_display.config(font=('Consolas', 12),
                                 bg='white',
                                 fg='black'
                                 )
        self.file_menu.config(bg='white',
                              fg='black'
                              )
        self.view_menu.config(bg='white',
                              fg='black'
                              )
        self.theme_menu.config(bg='white',
                               fg='black'
                               )

    def search_button_fuc(self):
        threading.Thread(target=self.search_inventory).start()

    def update_inventory_button_func(self):
        threading.Thread(target=self.scrape_inventory).start()

    # CREATE CSV FILES OF THE YARD INVENTORY
    def make_file(self, location_name, url):
        init_message = (
            f'Initializing request for {location_name} location...\n'
        )
        self.write_to_display(init_message)
        print(init_message)

        init_fail = 'Initiation failed!\n'
        seperator = '\n---------------\n'

        # CALL REQUEST TO WEBSITE
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/123.0.0.0 Safari/537.36'
        }

        response = requests.get(url, headers=headers)
        page_count = None

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # GET TOTAL TABLE PAGES
            input_tags = soup.find_all("input",
                                       {"class": "form-control"}
                                       )
            page_tag = input_tags[1]
            page_count = int(page_tag.get('data-pagecount'))

        else:
            # GET REQUEST FAILED
            get_request_failed = (
                f"{init_fail}Failed to fetch data from the URL:", url,
                f"\nResponse Status: {response.status_code}{seperator}")
            self.write_to_display(get_request_failed)
            print(get_request_failed)

        # TABLE DATA
        page_data = []
        page_index = 0
        start_index = 1

        # LOOP THROUGH ALL TABLE PAGES
        scraping_message = (
            f'Scraping {page_count} pages from the '
            f'{location_name} yard site.\n'
        )
        self.write_to_display(scraping_message)
        print(scraping_message)

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
                self.scrape_update(
                    f'\nScraped {page_index}/{page_count} pages'
                )
            else:
                # REQUEST FAILED
                url_failed_message = (
                    f"{init_fail}Failed to fetch data from the URL:", url,
                    f"\nResponse Status: {response.status_code}{seperator}"
                )
                self.write_to_display(url_failed_message)
                print(url_failed_message)
        # ALL YARD DATA
        yard_inventory = pd.concat(page_data)

        # CREATE A NEW CSV FILE IN DATA_CACHE
        # ENSURE FOLDER EXISTS
        if not os.path.exists('data_cache'):
            os.makedirs('data_cache')

            # CONSTRUCT FULL FILE PATH
        file_path = os.path.join('data_cache',
                                 f'{location_name}_inventory.csv'
                                 )

        # WRITE DATA TO CSV
        yard_inventory.to_csv(file_path, index=False)

        writing_csv_message = (
            f'\n{yard_inventory.shape[0]} vehicles written to '
            f'{location_name}_inventory.csv in data_cache folder.'
            f'\n{location_name} initiation complete!{seperator}'
        )
        self.write_to_display(writing_csv_message)
        print(writing_csv_message)

    # SCRAPES THE PULL AND SAVE WEBSITES TO UPDATE THE INVENTORY
    def scrape_inventory(self):
        self.update_display('')
        self.make_file('Spokane',
                       "https://newautopart.net/includes/pullandsave"
                       "/spokane/yard_locationslist.php"
                       )
        self.make_file('Mead',
                       "https://newautopart.net/includes/pullandsave/mead"
                       "/yard_locationslist.php"
                       )
        self.write_to_display('INVENTORY UPDATE FINISHED!')

    def search_inventory(self):
        combined_inventory = CombinedInventory(
            'Spokane_inventory.csv', 'Mead_inventory.csv'
        )
        year_param = None
        make_param = None
        model_param = None
        liters_param = None
        if self.year_entry.get():
            year_param = self.year_entry.get()
        if self.make_entry.get():
            make_param = self.make_entry.get()
        if self.model_entry.get():
            model_param = self.model_entry.get()
        if self.engine_entry.get():
            liters_param = self.engine_entry.get()
        if liters_param and make_param is None:
            messagebox.showinfo(
                title="Invalid search",
                message='Must have a "Make" input to search for Engine'
            )
        if liters_param and make_param:
            self.update_display(
                'Calling NHTSA API\nThis may take a few moments...'
            )

        results = combined_inventory.search(year=year_param,
                                            make=make_param,
                                            model=model_param,
                                            liters=liters_param
                                            )
        self.update_display(results)
        print(results)

    def update_display(self, content):
        self.text_display.config(state=tk.NORMAL)
        self.text_display.delete(1.0, tk.END)
        self.text_display.insert(tk.END, content)
        self.text_display.config(state=tk.DISABLED)

    def write_to_display(self, content):
        self.text_display.config(state=tk.NORMAL)
        self.text_display.insert(tk.END, content)
        self.text_display.config(state=tk.DISABLED)

    def clear_params(self):
        self.year_entry.delete(0, tk.END)
        self.make_entry.delete(0, tk.END)
        self.model_entry.delete(0, tk.END)
        self.engine_entry.delete(0, tk.END)
        self.text_display.config(state=tk.NORMAL)
        self.text_display.delete(1.0, tk.END)
        self.text_display.config(state=tk.DISABLED)

    def how_to_use_func(self):
        self.update_display(self.how_to_use)

    def scrape_update(self, content):
        self.text_display.config(state=tk.NORMAL)
        if count_lines(self.text_display) < 4:
            self.text_display.delete(3.0, tk.END)
        else:
            self.text_display.delete(9.0, tk.END)
        self.text_display.insert(tk.END, content)


# Combine the inventory
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

    def search(self, make=None, model=None, year=None, liters=None):
        if make:
            if make.upper() == 'CHEVY':
                make = 'CHEVROLET'
            elif make.upper() == 'NISSAN' or make.upper() == 'DATSUN':
                make = 'DATSUN - NISSAN'
            else:
                make = make.upper()
        if model:
            model = model.upper()
        if liters:
            liters = float(liters)
        if year:
            year = int(year)

        if make and model and year and liters:
            results1 = self.inventory1[
                (self.inventory1['Make'] == f'{make}') &
                (self.inventory1['Model'] == f'{model}') &
                (self.inventory1['Year'] == year)
                ]
            results2 = self.inventory2[
                (self.inventory2['Make'] == f'{make}') &
                (self.inventory2['Model'] == f'{model}') &
                (self.inventory2['Year'] == year)
                ]
            df_copy1 = results1.copy()
            df_copy2 = results2.copy()
            api_message = (
                f'Sending {results1.shape[0] + results2.shape[0]} '
                f'items to the NHTSA API\nThis may take a few moments...'
                f'\n---------------')
            print(api_message)

            df_copy1['Engine'] = df_copy1['Vin'].apply(get_displacement)
            df_copy2['Engine'] = df_copy2['Vin'].apply(get_displacement)
            out_put_df1 = df_copy1[df_copy1['Engine'] == liters]
            out_put_df2 = df_copy2[df_copy2['Engine'] == liters]
            count1 = out_put_df1.shape[0]
            count2 = out_put_df2.shape[0]
            out_put1 = (
                f'{self.location1} inventory\nFound {count1} instances of'
                f' {year} {make} {model} {liters}L\n{out_put_df1}'
            )
            out_put2 = (
                f'{self.location2} inventory\nFound {count2} instances of '
                f'{year} {make} {model} {liters}L\n{out_put_df2}')
            if count1 == 0 and count2 == 0:
                return (
                    f'No instances of {year} {make} {model} {liters}L '
                    f'found in {self.location1} or {self.location2}'
                )
            elif count1 == 0:
                return (
                    f'No instance of {year} {make} {model} {liters}L '
                    f'found in {self.location1} {self.seperator}{out_put2}'
                )
            elif count2 == 0:
                return (
                    f'{out_put1}{self.seperator}No instances of '
                    f'{year} {make} {model} {liters}L '
                    f'found in {self.location2}'
                )
            else:
                return f'{out_put1}{self.seperator}{out_put2}{self.seperator}'
        elif make and model and liters:
            results1 = self.inventory1[
                (self.inventory1['Make'] == f'{make}') &
                (self.inventory1['Model'] == f'{model}')
                ]
            results2 = self.inventory2[
                (self.inventory2['Make'] == f'{make}') &
                (self.inventory2['Model'] == f'{model}')
                ]
            df_copy1 = results1.copy()
            df_copy2 = results2.copy()

            api_message = (
                f'Sending {results1.shape[0] + results2.shape[0]} '
                f'items to the NHTSA API'
                f'\nThis may take a few moments...'
                f'\n---------------'
            )

            print(api_message)

            df_copy1['Engine'] = df_copy1['Vin'].apply(get_displacement)
            df_copy2['Engine'] = df_copy2['Vin'].apply(get_displacement)
            out_put_df1 = df_copy1[df_copy1['Engine'] == liters]
            out_put_df2 = df_copy2[df_copy2['Engine'] == liters]
            count1 = out_put_df1.shape[0]
            count2 = out_put_df2.shape[0]
            out_put1 = (
                f'{self.location1} inventory'
                f'\nFound {count1} instances of {make} {model} {liters}L'
                f'\n{out_put_df1}'
            )
            out_put2 = (
                f'{self.location2} inventory'
                f'\nFound {count2} instances of {make} {model} {liters}L'
                f'\n{out_put_df2}'
            )
            if count1 == 0 and count2 == 0:
                return (f'No instances of {make} {model} {liters}L '
                        f'found in {self.location1} or {self.location2}'
                        )
            elif count1 == 0:
                return (
                    f'No instance of {make} {model} {liters}L '
                    f'found in {self.location1}{self.seperator}{out_put2}'
                )
            elif count2 == 0:
                return (
                    f'{out_put1}{self.seperator}No instances of '
                    f'{make} {model} {liters}L found in {self.location2}'
                )
            else:
                return f'{out_put1}{self.seperator}{out_put2}{self.seperator}'
        elif make and year and liters:
            results1 = self.inventory1[
                (self.inventory1['Make'] == f'{make}') &
                (self.inventory1['Year'] == year)
                ]
            results2 = self.inventory2[
                (self.inventory2['Make'] == f'{make}') &
                (self.inventory2['Year'] == year)
                ]
            df_copy1 = results1.copy()
            df_copy2 = results2.copy()
            api_message = (
                f'Sending {results1.shape[0] + results2.shape[0]}'
                f' items to the NHTSA API'
                f'\nThis may take a few moments...'
                f'\n---------------'
            )
            print(api_message)

            df_copy1['Engine'] = df_copy1['Vin'].apply(get_displacement)
            df_copy2['Engine'] = df_copy2['Vin'].apply(get_displacement)
            out_put_df1 = df_copy1[df_copy1['Engine'] == liters]
            out_put_df2 = df_copy2[df_copy2['Engine'] == liters]
            count1 = out_put_df1.shape[0]
            count2 = out_put_df2.shape[0]
            out_put1 = (
                f'{self.location1} inventory\nFound {count1} instances of '
                f'{year} {make} {liters}L'
                f'\n{out_put_df1}'
            )
            out_put2 = (
                f'{self.location2} inventory\nFound {count2} instances of '
                f'{year} {make} {liters}L'
                f'\n{out_put_df2}'
            )
            if count1 == 0 and count2 == 0:
                return (f'No instances of {year} {make} {liters}L found in '
                        f'{self.location1} or {self.location2}'
                        )
            elif count1 == 0:
                return (
                    f'No instance of {year} {make} {liters}L found in '
                    f'{self.location1}{self.seperator}{out_put2}'
                )
            elif count2 == 0:
                return (
                    f'{out_put1}{self.seperator}No instances of '
                    f'{year} {make} {liters}L found in {self.location2}'
                )
            else:
                return f'{out_put1}{self.seperator}{out_put2}{self.seperator}'
        elif make and liters:
            results1 = self.inventory1[self.inventory1['Make'] == f'{make}']
            results2 = self.inventory2[self.inventory2['Make'] == f'{make}']
            df_copy1 = results1.copy()
            df_copy2 = results2.copy()
            api_message = (
                f'Sending {results1.shape[0] + results2.shape[0]} '
                f'items to the NHTSA API'
                f'\nThis may take a few moments...'
                f'\n---------------'
            )
            print(api_message)

            df_copy1['Engine'] = df_copy1['Vin'].apply(get_displacement)
            df_copy2['Engine'] = df_copy2['Vin'].apply(get_displacement)
            out_put_df1 = df_copy1[df_copy1['Engine'] == liters]
            out_put_df2 = df_copy2[df_copy2['Engine'] == liters]
            count1 = out_put_df1.shape[0]
            count2 = out_put_df2.shape[0]
            out_put1 = (
                f'{self.location1} inventory'
                f'\nFound {count1} instances of {make} {liters}L'
                f'\n{out_put_df1}'
            )
            out_put2 = (
                f'{self.location2} inventory'
                f'\nFound {count2} instances of {make} {liters}L'
                f'\n{out_put_df2}'
            )
            if count1 == 0 and count2 == 0:
                return (
                    f'No instances of {make} {liters}L '
                    f'found in {self.location1} or {self.location2}'
                )
            elif count1 == 0:
                return (
                    f'No instance of {make} {liters}L '
                    f'found in {self.location1}{self.seperator}{out_put2}'
                )
            elif count2 == 0:
                return (
                    f'{out_put1}{self.seperator}No instances of '
                    f'{make} {liters}L found in {self.location2}'
                )
            else:
                return f'{out_put1}{self.seperator}{out_put2}{self.seperator}'
        elif model and liters:
            return 'Invalid search parameters'
        elif year and liters:
            return 'Invalid search parameters'
        elif make and model and year:
            results1 = self.inventory1[
                (self.inventory1['Make'] == f'{make}') &
                (self.inventory1['Model'] == f'{model}') &
                (self.inventory1['Year'] == year)
                ]
            results2 = self.inventory2[
                (self.inventory2['Make'] == f'{make}') &
                (self.inventory2['Model'] == f'{model}') &
                (self.inventory2['Year'] == year)
                ]
            count1 = results1.shape[0]
            count2 = results2.shape[0]
            output1 = (
                f'{self.location1} inventory\nFound {count1} '
                f'instances of {year} {make} {model}\n{results1}'
            )
            output2 = (
                f'{self.location2} inventory\nFound {count2} '
                f'instances of {year} {make} {model}\n{results2}'
            )
            if results1.empty and results2.empty:
                return (
                    f'No instances of {year} {make} {model} '
                    f'found in {self.location1} or {self.location2}'
                )
            elif results1.empty:
                return (
                    f'No instance of {year} {make} {model} '
                    f'found in {self.location1}{self.seperator}{output2}'
                )
            elif results2.empty:
                return (
                    f'{output1}{self.seperator}No instances of '
                    f'{year} {make} {model} found in {self.location2}'
                )
            else:
                return f'{output1}{self.seperator}{output2}{self.seperator}'
        elif make and model:
            results1 = self.inventory1[
                (self.inventory1['Make'] == f'{make}') &
                (self.inventory1['Model'] == f'{model}')
                ]
            results2 = self.inventory2[
                (self.inventory2['Make'] == f'{make}') &
                (self.inventory2['Model'] == f'{model}')
                ]
            count1 = results1.shape[0]
            count2 = results2.shape[0]
            output1 = (
                f'{self.location1} inventory\nFound {count1} '
                f'instances of {make} {model}\n{results1}'
            )
            output2 = (
                f'{self.location2} inventory\nFound {count2} '
                f'instances of {make} {model}\n{results2}'
            )
            if results1.empty and results2.empty:
                return (
                    f'No instances of {make} {model} found in '
                    f'{self.location1} or {self.location2}'
                )
            elif results1.empty:
                return (
                    f'No instance of {make} {model} found in '
                    f'{self.location1}{self.seperator}{output2}'
                )
            elif results2.empty:
                return (
                    f'{output1}{self.seperator}No instances of '
                    f'{make} {model} found in {self.location2}'
                )
            else:
                return f'{output1}{self.seperator}{output2}{self.seperator}'
        elif make and year:
            results1 = self.inventory1[
                (self.inventory1['Make'] == f'{make}') &
                (self.inventory1['Year'] == year)
                ]
            results2 = self.inventory2[
                (self.inventory2['Make'] == f'{make}') &
                (self.inventory2['Year'] == year)
                ]
            count1 = results1.shape[0]
            count2 = results2.shape[0]
            output1 = (
                f'{self.location1} inventory\nFound {count1} '
                f'instances of {year} {make} \n{results1}'
            )
            output2 = (
                f'{self.location2} inventory\nFound {count2} '
                f'instances of {year} {make} \n{results2}'
            )
            if results1.empty and results2.empty:
                return (
                    f'No instances of {year} {make} found in '
                    f'{self.location1} or {self.location2}'
                )
            elif results1.empty:
                return (
                    f'No instance of {year} {make} found in{self.location1}'
                    f'{self.seperator}{output2}{self.seperator}'
                )
            elif results2.empty:
                return (
                    f'{output1}{self.seperator}No instances of {year} {make} '
                    f'found in {self.location2}{self.seperator}'
                )
            else:
                return f'{output1}{self.seperator}{output2}{self.seperator}'
        elif model and year:
            results1 = self.inventory1[
                (self.inventory1['Year'] == f'{year}') &
                (self.inventory1['Model'] == f'{model}')
                ]
            results2 = self.inventory2[
                (self.inventory2['Year'] == f'{year}') &
                (self.inventory2['Model'] == f'{model}')
                ]
            count1 = results1.shape[0]
            count2 = results2.shape[0]
            output1 = (
                f'{self.location1} inventory\nFound {count1} '
                f'instances of {year} {model}\n{results1}'
            )
            output2 = (
                f'{self.location2} inventory\nFound {count2} '
                f'instances of {year} {model}\n{results2}'
            )
            if results1.empty and results2.empty:
                return (
                    f'No instances of {year} {model} found in '
                    f'{self.location1} or {self.location2}'
                )
            elif results1.empty:
                return (
                    f'No instance of {year} {model} found in '
                    f'{self.location1}{self.seperator}{output2}'
                )
            elif results2.empty:
                return (
                    f'{output1}{self.seperator}No instances of '
                    f'{year} {model} found in {self.location2}'
                )
            else:
                return f'{output1}{self.seperator}{output2}{self.seperator}'
        elif make:
            results1 = self.inventory1[self.inventory1['Make'] == f'{make}']
            results2 = self.inventory2[self.inventory2['Make'] == f'{make}']
            count1 = results1.shape[0]
            count2 = results2.shape[0]
            output1 = (
                f'{self.location1} inventory\nFound '
                f'{count1} instances of {make}\n{results1}'
            )
            output2 = (
                f'{self.location2} inventory\nFound '
                f'{count2} instances of {make}\n{results2}'
            )
            if results1.empty and results2.empty:
                return (
                    f'No instances of the make {make} found in '
                    f'{self.location1} or {self.location2}'
                )
            elif results1.empty:
                return (
                    f'No instance of the make "{make}" '
                    f'found in {self.location1}\n {output2}'
                )
            elif results2.empty:
                return (
                    f'{output1}\nNo instance of the make '
                    f'"{make}" found in {self.location2}'
                )
            else:
                return f'{output1}{self.seperator}{output2}{self.seperator}'
        elif model:
            results1 = self.inventory1[self.inventory1['Model'] == f'{model}']
            results2 = self.inventory2[self.inventory2['Model'] == f'{model}']
            count1 = results1.shape[0]
            count2 = results2.shape[0]
            output1 = (
                f'{self.location1} inventory\nFound {count1} '
                f'instances of {model}\n{results1}'
            )
            output2 = (
                f'{self.location2} inventory\nFound {count2} '
                f'instances of {model}\n{results2}'
            )
            if results1.empty and results2.empty:
                return (
                    f'No instances of the model {model} found in '
                    f'{self.location1} or {self.location2}{self.seperator}'
                )
            elif results1.empty:
                return (
                    f'No instance of the model "{model}" found in '
                    f'{self.location1}{self.seperator}'
                    f'{output2}{self.seperator}'
                )
            elif results2.empty:
                return (
                    f'{output1}{self.seperator}No instance of the model '
                    f'"{model}" found in {self.location2}{self.seperator}'
                )
            else:
                return f'{output1}{self.seperator}{output2}{self.seperator}'
        elif year:
            results1 = self.inventory1[self.inventory1['Year'] == year]
            results2 = self.inventory2[self.inventory2['Year'] == year]
            count1 = results1.shape[0]
            count2 = results2.shape[0]
            output1 = (
                f'{self.location1} inventory'
                f'\nFound {count1} instances of {year}\n{results1}'
            )
            output2 = (
                f'{self.location2} inventory'
                f'\nFound {count2} instances of {year}\n{results2}'
            )
            if results1.empty and results2.empty:
                return (
                    f'No instances of the year {year} found in '
                    f'{self.location1} or {self.location2}{self.seperator}'
                )
            elif results1.empty:
                return (
                    f'No instance of the year "{year}" found in '
                    f'{self.location1}{self.seperator}'
                    f'{output2}{self.seperator}'
                )
            elif results2.empty:
                return (
                    f'{output1}{self.seperator}No instance of the year '
                    f'"{year}" found in {self.location2}{self.seperator}'
                )
            else:
                return f'{output1}{self.seperator}{output2}{self.seperator}'
        elif liters:
            return 'Invalid search parameters'
        else:
            return (
                f'{self.location1} inventory'
                f'\n{self.inventory1.shape[0]} items'
                f'\n{self.inventory1}'
                f'{self.seperator}{self.location2} inventory'
                f'\n{self.inventory2.shape[0]} items'
                f'\n{self.inventory2}')
