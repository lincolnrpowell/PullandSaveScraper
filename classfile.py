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

#pd.set_option('display.max_columns', None)
#pd.set_option('display.max_rows', None)


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
def get_displacement(results):
    for result in results:
        if 'Variable' in result and 'Value' in result:
            if result['Variable'] == 'Displacement (L)':
                engine_displacement = result['Value']
                if engine_displacement is None:
                    engine_displacement = 0.0
                return round(float(engine_displacement), 1)


def get_engine_model(results):
    for result in results:
        if 'Variable' in result and 'Value' in result:
            if result['Variable'] == 'Engine Model':
                engine_model = result['Value']
                if engine_model is None:
                    engine_displacement = 'No info'
                return engine_model


def get_cylinder_count(results):
    for result in results:
        if 'Variable' in result and 'Value' in result:
            if result['Variable'] == 'Engine Number of Cylinders':
                cylinder_count = result['Value']
                if cylinder_count:
                    cylinder_count = cylinder_count
                return cylinder_count


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
        self.geometry('700x700')
        self.minsize(520, 600)
        self.appearance = 'dark'
        ctk.set_appearance_mode(f'{self.appearance}')
        ctk.set_default_color_theme('dark-blue')

        self.how_to_use = ('How to use:'
                           '\n\n-Click File > Update Inventory... to get '
                           'latest yard inventory.'
                           '\n-Enter search parameters into the input fields, '
                           'then click Search.'
                           '\n-Results will display in this text box.'
                           '\n-If searching for an Engine, please provide at'
                           'least a "Make"\nparameter. The more parameters '
                           'that are entered, the faster the API call will be.'
                           '\n-CLick the "Clear" button to clear entry '
                           'fields and search display.'
                           '\n\nNote:'
                           '\nThe results are only as accurate as the info '
                           'provided by the Pull\nand Save websites and the '
                           'NHSTA API. Some search results may not be\ntruly '
                           'accurate.'
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
                                   command=self.destroy
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
                                    command=self.dark_theme_button_func
                                    )
        self.theme_menu.add_separator()
        self.theme_menu.add_command(label='Light theme',
                                    command=self.light_theme_button_func
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
        displacement_label = ctk.CTkLabel(self,
                                          text="Displacement(L):",
                                          font=('Consolas', 14)
                                          )
        displacement_label.grid(row=4,
                                column=0,
                                padx=10,
                                pady=5,
                                sticky="W" + "E" + "N" + "S"
                                )
        cylinder_label = ctk.CTkLabel(self,
                                      text='Cylinders:',
                                      font=('Consolas', 14)
                                      )
        cylinder_label.grid(row=5,
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
        self.displacement_entry = ctk.CTkEntry(self)
        self.displacement_entry.grid(row=4,
                                     column=1,
                                     padx=10,
                                     pady=5,
                                     sticky="W" + "E" + "N" + "S"
                                     )
        self.cylinder_entry = ctk.CTkEntry(self)
        self.cylinder_entry.grid(row=5,
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
        self.search_button.grid(row=6,
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
        self.clear_button.grid(row=6,
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
        self.text_display.grid(row=7,
                               column=0,
                               columnspan=4,
                               padx=10,
                               pady=5,
                               sticky="W" + "E" + "N" + "S"
                               )

        # Run
        self.mainloop()

    def dark_theme_button_func(self):
        threading.Thread(target=self.dark_theme).start()

    def light_theme_button_func(self):
        threading.Thread(target=self.light_theme).start()

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
        # Check to see if the inventory has been scraped
        if not os.path.exists('data_cache'):
            no_data = ('Data not yet scraped!\nPlease update '
                       'the inventory before continuing.')
            self.update_display(no_data)
            print(no_data)
        else:
            combined_inventory = CombinedInventory(
                'Spokane_inventory.csv', 'Mead_inventory.csv'
            )
            year_param = None
            make_param = None
            model_param = None
            displacement_param = None
            cylinders_param = None
            if self.year_entry.get():
                year_param = self.year_entry.get()
            if self.make_entry.get():
                make_param = self.make_entry.get()
            if self.model_entry.get():
                model_param = self.model_entry.get()
            if self.displacement_entry.get():
                displacement_param = self.displacement_entry.get()
            if self.cylinder_entry.get():
                cylinders_param = self.cylinder_entry.get()
            if displacement_param and make_param is None:
                messagebox.showinfo(
                    title="Invalid search",
                    message='Must have a "Make" input to search for Engine'
                )
            if cylinders_param and make_param is None:
                messagebox.showinfo(
                    title="Invalid search",
                    message='Must have a "Make" input to search for Engine'
                )
            if displacement_param and make_param:
                self.update_display(
                    'Calling NHTSA API\nThis may take a few moments...'
                )
            if cylinders_param and make_param:
                self.update_display(
                    'Calling NHTSA API\nThis may take a few moments...'
                )

            results = combined_inventory.search(year=year_param,
                                                make=make_param,
                                                model=model_param,
                                                displacement=displacement_param,
                                                cylinders=cylinders_param
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
        self.displacement_entry.delete(0, tk.END)
        self.cylinder_entry.delete(0, tk.END)
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

    def search(self, year=None,
               make=None,
               model=None,
               displacement=None,
               cylinders=None
               ):
        if make:
            if make.upper() == 'CHEVY':
                make = 'CHEVROLET'
            elif make.upper() == 'NISSAN' or make.upper() == 'DATSUN':
                make = 'DATSUN - NISSAN'
            else:
                make = make.upper()
        if model:
            model = model.upper()
        if displacement:
            displacement = float(displacement)
        if year:
            year = int(year)
        if cylinders:
            cylinders = str(cylinders)

        if displacement and not make:
            return 'Invalid search parameters'
        if cylinders and not make:
            return 'Invalid search parameters'

        if year and make and model and displacement and cylinders:
            results_df1 = self.inventory1[
                (self.inventory1['Year'] == year) &
                (self.inventory1['Make'] == f'{make}') &
                (self.inventory1['Model'] == f'{model}')
                ]
            results_df2 = self.inventory2[
                (self.inventory2['Year'] == year) &
                (self.inventory2['Make'] == f'{make}') &
                (self.inventory2['Model'] == f'{model}')
                ]

            df_copy1 = results_df1.copy()
            df_copy2 = results_df2.copy()

            api_message = (f'Sending {df_copy1.shape[0] + df_copy2.shape[0]} '
                           f'items to NHTSA API.'
                           f'\nThis may take a few moments...')
            print(api_message)

            for index, row in df_copy1.iterrows():
                vin = row['Vin']
                decode_data = vin_decode(vin)
                if decode_data:
                    df_copy1.at[index, 'Displacement'] = get_displacement(
                        decode_data
                    )
                    df_copy1.at[index, 'Cylinders'] = get_cylinder_count(
                        decode_data
                    )
                    df_copy1.at[index, 'Engine Model'] = get_engine_model(
                        decode_data
                    )

            for index, row in df_copy2.iterrows():
                vin = row['Vin']
                decode_data = vin_decode(vin)
                if decode_data:
                    df_copy2.at[index, 'Displacement'] = get_displacement(
                        decode_data
                    )
                    df_copy2.at[index, 'Cylinders'] = get_cylinder_count(
                        decode_data
                    )
                    df_copy2.at[index, 'Engine Model'] = get_engine_model(
                        decode_data
                    )

            out_put_df1 = df_copy1[(df_copy1['Displacement'] == displacement) &
                                   (df_copy1['Cylinders'] == cylinders)
                                   ]
            out_put_df2 = df_copy2[(df_copy2['Displacement'] == displacement) &
                                   (df_copy2['Cylinders'] == cylinders)
                                   ]

            count1 = out_put_df1.shape[0]
            count2 = out_put_df2.shape[0]

            out_put_str1 = (
                f'{self.location1} inventory\nFound {count1} instances of '
                f'{year} {make} {model} {displacement}L {cylinders}cyl'
                f'\n{out_put_df1}\n---------------\n'
            )
            out_put_str2 = (
                f'{self.location2} inventory\nFound {count2} instances of '
                f'{year} {make} {model} {displacement}L {cylinders}cyl'
                f'\n{out_put_df2}\n---------------\n'
            )

            if count1 == 0:
                out_put_str1 = (f'No instances of {year} {make} {model} '
                                f'{displacement}L {cylinders}cyl found in '
                                f'{self.location1} inventory'
                                f'\n---------------\n')
            if count2 == 0:
                out_put_str2 = (f'No instances of {year} {make} {model} '
                                f'{displacement}L {cylinders}cyl found in '
                                f'{self.location2} inventory'
                                f'\n---------------\n')

            return f'{out_put_str1}{out_put_str2}'

        elif make and model and displacement and cylinders:
            results_df1 = self.inventory1[
                (self.inventory1['Make'] == f'{make}') &
                (self.inventory1['Model'] == f'{model}')
                ]
            results_df2 = self.inventory2[
                (self.inventory2['Make'] == f'{make}') &
                (self.inventory2['Model'] == f'{model}')
                ]

            df_copy1 = results_df1.copy()
            df_copy2 = results_df2.copy()

            api_message = (f'Sending {df_copy1.shape[0] + df_copy2.shape[0]} '
                           f'items to NHTSA API.'
                           f'\nThis may take a few moments...')
            print(api_message)

            for index, row in df_copy1.iterrows():
                vin = row['Vin']
                decode_data = vin_decode(vin)
                if decode_data:
                    df_copy1.at[index, 'Displacement'] = get_displacement(
                        decode_data
                    )
                    df_copy1.at[index, 'Cylinders'] = get_cylinder_count(
                        decode_data
                    )
                    df_copy1.at[index, 'Engine Model'] = get_engine_model(
                        decode_data
                    )

            for index, row in df_copy2.iterrows():
                vin = row['Vin']
                decode_data = vin_decode(vin)
                if decode_data:
                    df_copy2.at[index, 'Displacement'] = get_displacement(
                        decode_data
                    )
                    df_copy2.at[index, 'Cylinders'] = get_cylinder_count(
                        decode_data
                    )
                    df_copy2.at[index, 'Engine Model'] = get_engine_model(
                        decode_data
                    )

            out_put_df1 = df_copy1[(df_copy1['Displacement'] == displacement) &
                                   (df_copy1['Cylinders'] == cylinders)
                                   ]
            out_put_df2 = df_copy2[(df_copy2['Displacement'] == displacement) &
                                   (df_copy2['Cylinders'] == cylinders)
                                   ]

            count1 = out_put_df1.shape[0]
            count2 = out_put_df2.shape[0]

            out_put_str1 = (
                f'{self.location1} inventory\nFound {count1} instances of '
                f'{make} {model} {displacement}L {cylinders}cyl'
                f'\n{out_put_df1}\n---------------\n'
            )
            out_put_str2 = (
                f'{self.location2} inventory\nFound {count2} instances of '
                f'{make} {model} {displacement}L {cylinders}cyl'
                f'\n{out_put_df2}\n---------------\n'
            )

            if count1 == 0:
                out_put_str1 = (f'No instances of {make} {model} '
                                f'{displacement}L {cylinders}cyl found in '
                                f'{self.location1} inventory'
                                f'\n---------------\n')
            if count2 == 0:
                out_put_str2 = (f'No instances of {make} {model} '
                                f'{displacement}L {cylinders}cyl found in '
                                f'{self.location2} inventory'
                                f'\n---------------\n')

            return f'{out_put_str1}{out_put_str2}'

        elif make and displacement and cylinders:
            results_df1 = self.inventory1[self.inventory1['Make'] == f'{make}']
            results_df2 = self.inventory2[self.inventory2['Make'] == f'{make}']

            df_copy1 = results_df1.copy()
            df_copy2 = results_df2.copy()

            api_message = (f'Sending {df_copy1.shape[0] + df_copy2.shape[0]} '
                           f'items to NHTSA API.'
                           f'\nThis may take a few moments...')
            print(api_message)

            for index, row in df_copy1.iterrows():
                vin = row['Vin']
                decode_data = vin_decode(vin)
                if decode_data:
                    df_copy1.at[index, 'Displacement'] = get_displacement(
                        decode_data
                    )
                    df_copy1.at[index, 'Cylinders'] = get_cylinder_count(
                        decode_data
                    )
                    df_copy1.at[index, 'Engine Model'] = get_engine_model(
                        decode_data
                    )

            for index, row in df_copy2.iterrows():
                vin = row['Vin']
                decode_data = vin_decode(vin)
                if decode_data:
                    df_copy2.at[index, 'Displacement'] = get_displacement(
                        decode_data
                    )
                    df_copy2.at[index, 'Cylinders'] = get_cylinder_count(
                        decode_data
                    )
                    df_copy2.at[index, 'Engine Model'] = get_engine_model(
                        decode_data
                    )

            out_put_df1 = df_copy1[(df_copy1['Displacement'] == displacement) &
                                   (df_copy1['Cylinders'] == cylinders)
                                   ]
            out_put_df2 = df_copy2[(df_copy2['Displacement'] == displacement) &
                                   (df_copy2['Cylinders'] == cylinders)
                                   ]

            count1 = out_put_df1.shape[0]
            count2 = out_put_df2.shape[0]

            out_put_str1 = (
                f'{self.location1} inventory\nFound {count1} instances of '
                f'{make} {displacement}L {cylinders}cyl'
                f'\n{out_put_df1}\n---------------\n'
            )
            out_put_str2 = (
                f'{self.location2} inventory\nFound {count2} instances of '
                f'{make} {displacement}L {cylinders}cyl'
                f'\n{out_put_df2}\n---------------\n'
            )

            if count1 == 0:
                out_put_str1 = (f'No instances of {make} {displacement}L '
                                f'{cylinders}cyl found in '
                                f'{self.location1} inventory'
                                f'\n---------------\n')
            if count2 == 0:
                out_put_str2 = (f'No instances of {make} {displacement}L '
                                f'{cylinders}cyl found in '
                                f'{self.location2} inventory'
                                f'\n---------------\n')

            return f'{out_put_str1}{out_put_str2}'

        elif year and make and model and cylinders:
            results_df1 = self.inventory1[
                (self.inventory1['Year'] == year) &
                (self.inventory1['Make'] == f'{make}') &
                (self.inventory1['Model'] == f'{model}')
                ]
            results_df2 = self.inventory2[
                (self.inventory2['Year'] == year) &
                (self.inventory2['Make'] == f'{make}') &
                (self.inventory2['Model'] == f'{model}')
                ]

            df_copy1 = results_df1.copy()
            df_copy2 = results_df2.copy()

            api_message = (f'Sending {df_copy1.shape[0] + df_copy2.shape[0]} '
                           f'items to NHTSA API.'
                           f'\nThis may take a few moments...')
            print(api_message)

            for index, row in df_copy1.iterrows():
                vin = row['Vin']
                decode_data = vin_decode(vin)
                if decode_data:
                    df_copy1.at[index, 'Displacement'] = get_displacement(
                        decode_data
                    )
                    df_copy1.at[index, 'Cylinders'] = get_cylinder_count(
                        decode_data
                    )
                    df_copy1.at[index, 'Engine Model'] = get_engine_model(
                        decode_data
                    )

            for index, row in df_copy2.iterrows():
                vin = row['Vin']
                decode_data = vin_decode(vin)
                if decode_data:
                    df_copy2.at[index, 'Displacement'] = get_displacement(
                        decode_data
                    )
                    df_copy2.at[index, 'Cylinders'] = get_cylinder_count(
                        decode_data
                    )
                    df_copy2.at[index, 'Engine Model'] = get_engine_model(
                        decode_data
                    )

            out_put_df1 = df_copy1[df_copy1['Cylinders'] == cylinders]
            out_put_df2 = df_copy2[df_copy2['Cylinders'] == cylinders]

            count1 = out_put_df1.shape[0]
            count2 = out_put_df2.shape[0]

            out_put_str1 = (
                f'{self.location1} inventory\nFound {count1} instances of '
                f'{year} {make} {model} {cylinders}cyl'
                f'\n{out_put_df1}\n---------------\n'
            )
            out_put_str2 = (
                f'{self.location2} inventory\nFound {count2} instances of '
                f'{year} {make} {model} {cylinders}cyl'
                f'\n{out_put_df2}\n---------------\n'
            )

            if count1 == 0:
                out_put_str1 = (f'No instances of {year} {make} {model} '
                                f'{cylinders}cyl found in '
                                f'{self.location1} inventory'
                                f'\n---------------\n')
            if count2 == 0:
                out_put_str2 = (f'No instances of {year} {make} {model} '
                                f'{cylinders}cyl found in '
                                f'{self.location2} inventory'
                                f'\n---------------\n')

            return f'{out_put_str1}{out_put_str2}'

        elif year and make and model and displacement:
            results_df1 = self.inventory1[
                (self.inventory1['Year'] == year) &
                (self.inventory1['Make'] == f'{make}') &
                (self.inventory1['Model'] == f'{model}')
                ]
            results_df2 = self.inventory2[
                (self.inventory2['Year'] == year) &
                (self.inventory2['Make'] == f'{make}') &
                (self.inventory2['Model'] == f'{model}')
                ]

            df_copy1 = results_df1.copy()
            df_copy2 = results_df2.copy()

            api_message = (f'Sending {df_copy1.shape[0] + df_copy2.shape[0]} '
                           f'items to NHTSA API.'
                           f'\nThis may take a few moments...')
            print(api_message)

            for index, row in df_copy1.iterrows():
                vin = row['Vin']
                decode_data = vin_decode(vin)
                if decode_data:
                    df_copy1.at[index, 'Displacement'] = get_displacement(
                        decode_data
                    )
                    df_copy1.at[index, 'Cylinders'] = get_cylinder_count(
                        decode_data
                    )
                    df_copy1.at[index, 'Engine Model'] = get_engine_model(
                        decode_data
                    )

            for index, row in df_copy2.iterrows():
                vin = row['Vin']
                decode_data = vin_decode(vin)
                if decode_data:
                    df_copy2.at[index, 'Displacement'] = get_displacement(
                        decode_data
                    )
                    df_copy2.at[index, 'Cylinders'] = get_cylinder_count(
                        decode_data
                    )
                    df_copy2.at[index, 'Engine Model'] = get_engine_model(
                        decode_data
                    )

            out_put_df1 = df_copy1[df_copy1['Displacement'] == displacement]
            out_put_df2 = df_copy2[df_copy2['Displacement'] == displacement]

            count1 = out_put_df1.shape[0]
            count2 = out_put_df2.shape[0]

            out_put_str1 = (
                f'{self.location1} inventory\nFound {count1} instances of '
                f'{year} {make} {model} {displacement}L'
                f'\n{out_put_df1}\n---------------\n'
            )
            out_put_str2 = (
                f'{self.location2} inventory\nFound {count2} instances of '
                f'{year} {make} {model} {displacement}L'
                f'\n{out_put_df2}\n---------------\n'
            )

            if count1 == 0:
                out_put_str1 = (f'No instances of {year} {make} {model} '
                                f'{displacement}L found in '
                                f'{self.location1} inventory'
                                f'\n---------------\n')
            if count2 == 0:
                out_put_str2 = (f'No instances of {year} {make} {model} '
                                f'{displacement}L found in '
                                f'{self.location2} inventory'
                                f'\n---------------\n')

            return f'{out_put_str1}{out_put_str2}'

        elif make and model and cylinders:
            results_df1 = self.inventory1[
                (self.inventory1['Make'] == f'{make}') &
                (self.inventory1['Model'] == f'{model}')
                ]
            results_df2 = self.inventory2[
                (self.inventory2['Make'] == f'{make}') &
                (self.inventory2['Model'] == f'{model}')
                ]

            df_copy1 = results_df1.copy()
            df_copy2 = results_df2.copy()

            api_message = (f'Sending {df_copy1.shape[0] + df_copy2.shape[0]} '
                           f'items to NHTSA API.'
                           f'\nThis may take a few moments...')
            print(api_message)

            for index, row in df_copy1.iterrows():
                vin = row['Vin']
                decode_data = vin_decode(vin)
                if decode_data:
                    df_copy1.at[index, 'Displacement'] = get_displacement(
                        decode_data
                    )
                    df_copy1.at[index, 'Cylinders'] = get_cylinder_count(
                        decode_data
                    )
                    df_copy1.at[index, 'Engine Model'] = get_engine_model(
                        decode_data
                    )

            for index, row in df_copy2.iterrows():
                vin = row['Vin']
                decode_data = vin_decode(vin)
                if decode_data:
                    df_copy2.at[index, 'Displacement'] = get_displacement(
                        decode_data
                    )
                    df_copy2.at[index, 'Cylinders'] = get_cylinder_count(
                        decode_data
                    )
                    df_copy2.at[index, 'Engine Model'] = get_engine_model(
                        decode_data
                    )

            out_put_df1 = df_copy1[df_copy1['Cylinders'] == cylinders]
            out_put_df2 = df_copy2[df_copy2['Cylinders'] == cylinders]

            count1 = out_put_df1.shape[0]
            count2 = out_put_df2.shape[0]

            out_put_str1 = (
                f'{self.location1} inventory\nFound {count1} instances of '
                f'{make} {model} {cylinders}cyl'
                f'\n{out_put_df1}\n---------------\n'
            )
            out_put_str2 = (
                f'{self.location2} inventory\nFound {count2} instances of '
                f'{make} {model} {cylinders}cyl'
                f'\n{out_put_df2}\n---------------\n'
            )

            if count1 == 0:
                out_put_str1 = (f'No instances of {make} {model} '
                                f'{cylinders}cyl found in '
                                f'{self.location1} inventory'
                                f'\n---------------\n')
            if count2 == 0:
                out_put_str2 = (f'No instances of {make} {model} '
                                f'{cylinders}cyl found in '
                                f'{self.location2} inventory'
                                f'\n---------------\n')

            return f'{out_put_str1}{out_put_str2}'

        elif make and model and displacement:
            results_df1 = self.inventory1[
                (self.inventory1['Make'] == f'{make}') &
                (self.inventory1['Model'] == f'{model}')
                ]
            results_df2 = self.inventory2[
                (self.inventory2['Make'] == f'{make}') &
                (self.inventory2['Model'] == f'{model}')
                ]

            df_copy1 = results_df1.copy()
            df_copy2 = results_df2.copy()

            api_message = (f'Sending {df_copy1.shape[0] + df_copy2.shape[0]} '
                           f'items to NHTSA API.'
                           f'\nThis may take a few moments...')
            print(api_message)

            for index, row in df_copy1.iterrows():
                vin = row['Vin']
                decode_data = vin_decode(vin)
                if decode_data:
                    df_copy1.at[index, 'Displacement'] = get_displacement(
                        decode_data
                    )
                    df_copy1.at[index, 'Cylinders'] = get_cylinder_count(
                        decode_data
                    )
                    df_copy1.at[index, 'Engine Model'] = get_engine_model(
                        decode_data
                    )

            for index, row in df_copy2.iterrows():
                vin = row['Vin']
                decode_data = vin_decode(vin)
                if decode_data:
                    df_copy2.at[index, 'Displacement'] = get_displacement(
                        decode_data
                    )
                    df_copy2.at[index, 'Cylinders'] = get_cylinder_count(
                        decode_data
                    )
                    df_copy2.at[index, 'Engine Model'] = get_engine_model(
                        decode_data
                    )

            out_put_df1 = df_copy1[df_copy1['Displacement'] == displacement]
            out_put_df2 = df_copy2[df_copy2['Displacement'] == displacement]

            count1 = out_put_df1.shape[0]
            count2 = out_put_df2.shape[0]

            out_put_str1 = (
                f'{self.location1} inventory\nFound {count1} instances of '
                f'{make} {model} {displacement}L'
                f'\n{out_put_df1}\n---------------\n'
            )
            out_put_str2 = (
                f'{self.location2} inventory\nFound {count2} instances of '
                f'{make} {model} {displacement}L'
                f'\n{out_put_df2}\n---------------\n'
            )

            if count1 == 0:
                out_put_str1 = (f'No instances of {make} {model} '
                                f'{displacement}L found in '
                                f'{self.location1} inventory'
                                f'\n---------------\n')
            if count2 == 0:
                out_put_str2 = (f'No instances of {make} {model} '
                                f'{displacement}L found in '
                                f'{self.location2} inventory'
                                f'\n---------------\n')

            return f'{out_put_str1}{out_put_str2}'

        elif make and cylinders:
            results_df1 = self.inventory1[self.inventory1['Make'] == f'{make}']
            results_df2 = self.inventory2[self.inventory2['Make'] == f'{make}']

            df_copy1 = results_df1.copy()
            df_copy2 = results_df2.copy()

            api_message = (f'Sending {df_copy1.shape[0] + df_copy2.shape[0]} '
                           f'items to NHTSA API.'
                           f'\nThis may take a few moments...')
            print(api_message)

            for index, row in df_copy1.iterrows():
                vin = row['Vin']
                decode_data = vin_decode(vin)
                if decode_data:
                    df_copy1.at[index, 'Displacement'] = get_displacement(
                        decode_data
                    )
                    df_copy1.at[index, 'Cylinders'] = get_cylinder_count(
                        decode_data
                    )
                    df_copy1.at[index, 'Engine Model'] = get_engine_model(
                        decode_data
                    )

            for index, row in df_copy2.iterrows():
                vin = row['Vin']
                decode_data = vin_decode(vin)
                if decode_data:
                    df_copy2.at[index, 'Displacement'] = get_displacement(
                        decode_data
                    )
                    df_copy2.at[index, 'Cylinders'] = get_cylinder_count(
                        decode_data
                    )
                    df_copy2.at[index, 'Engine Model'] = get_engine_model(
                        decode_data
                    )

            out_put_df1 = df_copy1[df_copy1['Cylinders'] == cylinders]
            out_put_df2 = df_copy2[df_copy2['Cylinders'] == cylinders]

            count1 = out_put_df1.shape[0]
            count2 = out_put_df2.shape[0]

            out_put_str1 = (
                f'{self.location1} inventory\nFound {count1} instances of '
                f'{make} {cylinders}cyl'
                f'\n{out_put_df1}\n---------------\n'
            )
            out_put_str2 = (
                f'{self.location2} inventory\nFound {count2} instances of '
                f'{make} {cylinders}cyl'
                f'\n{out_put_df2}\n---------------\n'
            )

            if count1 == 0:
                out_put_str1 = (f'No instances of {make} '
                                f'{cylinders}cyl found in '
                                f'{self.location1} inventory'
                                f'\n---------------\n')
            if count2 == 0:
                out_put_str2 = (f'No instances of {make} '
                                f'{cylinders}cyl found in '
                                f'{self.location2} inventory'
                                f'\n---------------\n')

            return f'{out_put_str1}{out_put_str2}'

        elif make and displacement:
            results_df1 = self.inventory1[self.inventory1['Make'] == f'{make}']
            results_df2 = self.inventory2[self.inventory2['Make'] == f'{make}']

            df_copy1 = results_df1.copy()
            df_copy2 = results_df2.copy()

            api_message = (f'Sending {df_copy1.shape[0] + df_copy2.shape[0]} '
                           f'items to NHTSA API.'
                           f'\nThis may take a few moments...')
            print(api_message)

            for index, row in df_copy1.iterrows():
                vin = row['Vin']
                decode_data = vin_decode(vin)
                if decode_data:
                    df_copy1.at[index, 'Displacement'] = get_displacement(
                        decode_data
                    )
                    df_copy1.at[index, 'Cylinders'] = get_cylinder_count(
                        decode_data
                    )
                    df_copy1.at[index, 'Engine Model'] = get_engine_model(
                        decode_data
                    )

            for index, row in df_copy2.iterrows():
                vin = row['Vin']
                decode_data = vin_decode(vin)
                if decode_data:
                    df_copy2.at[index, 'Displacement'] = get_displacement(
                        decode_data
                    )
                    df_copy2.at[index, 'Cylinders'] = get_cylinder_count(
                        decode_data
                    )
                    df_copy2.at[index, 'Engine Model'] = get_engine_model(
                        decode_data
                    )

            out_put_df1 = df_copy1[df_copy1['Displacement'] == displacement]
            out_put_df2 = df_copy2[df_copy2['Displacement'] == displacement]

            count1 = out_put_df1.shape[0]
            count2 = out_put_df2.shape[0]

            out_put_str1 = (
                f'{self.location1} inventory\nFound {count1} instances of '
                f'{make} {displacement}L'
                f'\n{out_put_df1}\n---------------\n'
            )
            out_put_str2 = (
                f'{self.location2} inventory\nFound {count2} instances of '
                f'{make} {displacement}L'
                f'\n{out_put_df2}\n---------------\n'
            )

            if count1 == 0:
                out_put_str1 = (f'No instances of {make} '
                                f'{displacement}L found in '
                                f'{self.location1} inventory'
                                f'\n---------------\n')
            if count2 == 0:
                out_put_str2 = (f'No instances of {make} '
                                f'{displacement}L found in '
                                f'{self.location2} inventory'
                                f'\n---------------\n')

            return f'{out_put_str1}{out_put_str2}'

        elif year and make and model:
            results_df1 = self.inventory1[
                (self.inventory1['Year'] == year) &
                (self.inventory1['Make'] == f'{make}') &
                (self.inventory1['Model'] == f'{model}')
                ]
            results_df2 = self.inventory2[
                (self.inventory2['Year'] == year) &
                (self.inventory2['Make'] == f'{make}') &
                (self.inventory2['Model'] == f'{model}')
                ]

            out_put_df1 = results_df1
            out_put_df2 = results_df2

            count1 = out_put_df1.shape[0]
            count2 = out_put_df2.shape[0]

            out_put_str1 = (
                f'{self.location1} inventory\nFound {count1} instances of '
                f'{year} {make} {model}'
                f'\n{out_put_df1}\n---------------\n'
            )
            out_put_str2 = (
                f'{self.location2} inventory\nFound {count2} instances of '
                f'{year} {make} {model}'
                f'\n{out_put_df2}\n---------------\n'
            )

            if count1 == 0:
                out_put_str1 = (f'No instances of {year} {make} {model} '
                                f'found in {self.location1} inventory'
                                f'\n---------------\n')
            if count2 == 0:
                out_put_str2 = (f'No instances of {year} {make} {model} '
                                f'found in {self.location2} inventory'
                                f'\n---------------\n')

            return f'{out_put_str1}{out_put_str2}'

        elif year and make:
            results_df1 = self.inventory1[
                (self.inventory1['Year'] == year) &
                (self.inventory1['Make'] == f'{make}')]
            results_df2 = self.inventory2[
                (self.inventory2['Year'] == year) &
                (self.inventory2['Make'] == f'{make}')]

            out_put_df1 = results_df1
            out_put_df2 = results_df2

            count1 = out_put_df1.shape[0]
            count2 = out_put_df2.shape[0]

            out_put_str1 = (
                f'{self.location1} inventory\nFound {count1} instances of '
                f'{year} {make} {model}'
                f'\n{out_put_df1}\n---------------\n'
            )
            out_put_str2 = (
                f'{self.location2} inventory\nFound {count2} instances of '
                f'{year} {make} {model}'
                f'\n{out_put_df2}\n---------------\n'
            )

            if count1 == 0:
                out_put_str1 = (f'No instances of {year} {make} '
                                f'found in {self.location1} inventory'
                                f'\n---------------\n')
            if count2 == 0:
                out_put_str2 = (f'No instances of {year} {make} '
                                f'found in {self.location2} inventory'
                                f'\n---------------\n')

            return f'{out_put_str1}{out_put_str2}'

        elif year and model:
            results_df1 = self.inventory1[
                (self.inventory1['Year'] == year) &
                (self.inventory1['Model'] == f'{model}')
                ]
            results_df2 = self.inventory2[
                (self.inventory2['Year'] == year) &
                (self.inventory2['Model'] == f'{model}')
                ]

            out_put_df1 = results_df1
            out_put_df2 = results_df2

            count1 = out_put_df1.shape[0]
            count2 = out_put_df2.shape[0]

            out_put_str1 = (
                f'{self.location1} inventory\nFound {count1} instances of '
                f'{year} {model}'
                f'\n{out_put_df1}\n---------------\n'
            )
            out_put_str2 = (
                f'{self.location2} inventory\nFound {count2} instances of '
                f'{year} {model}'
                f'\n{out_put_df2}\n---------------\n'
            )

            if count1 == 0:
                out_put_str1 = (f'No instances of {year} {make} '
                                f'found in {self.location1} inventory'
                                f'\n---------------\n')
            if count2 == 0:
                out_put_str2 = (f'No instances of {year} {make} '
                                f'found in {self.location2} inventory'
                                f'\n---------------\n')

            return f'{out_put_str1}{out_put_str2}'

        elif make and model:
            results_df1 = self.inventory1[
                (self.inventory1['Make'] == f'{make}') &
                (self.inventory1['Model'] == f'{model}')
                ]
            results_df2 = self.inventory2[
                (self.inventory2['Make'] == f'{make}') &
                (self.inventory2['Model'] == f'{model}')
                ]

            out_put_df1 = results_df1
            out_put_df2 = results_df2

            count1 = out_put_df1.shape[0]
            count2 = out_put_df2.shape[0]

            out_put_str1 = (
                f'{self.location1} inventory\nFound {count1} instances of '
                f'{make} {model}'
                f'\n{out_put_df1}\n---------------\n'
            )
            out_put_str2 = (
                f'{self.location2} inventory\nFound {count2} instances of '
                f'{make} {model}'
                f'\n{out_put_df2}\n---------------\n'
            )

            if count1 == 0:
                out_put_str1 = (f'No instances of {make} {model} '
                                f'found in {self.location1} inventory'
                                f'\n---------------\n')
            if count2 == 0:
                out_put_str2 = (f'No instances of {make} {model} '
                                f'found in {self.location2} inventory'
                                f'\n---------------\n')

            return f'{out_put_str1}{out_put_str2}'

        elif year:
            results_df1 = self.inventory1[self.inventory1['Year'] == year]
            results_df2 = self.inventory2[self.inventory2['Year'] == year]

            out_put_df1 = results_df1
            out_put_df2 = results_df2

            count1 = out_put_df1.shape[0]
            count2 = out_put_df2.shape[0]

            out_put_str1 = (
                f'{self.location1} inventory\nFound {count1} instances of '
                f'{model}'
                f'\n{out_put_df1}\n---------------\n'
            )
            out_put_str2 = (
                f'{self.location2} inventory\nFound {count2} instances of '
                f'{model}'
                f'\n{out_put_df2}\n---------------\n'
            )

            if count1 == 0:
                out_put_str1 = (f'No instances of {year} '
                                f'found in {self.location1} inventory'
                                f'\n---------------\n')
            if count2 == 0:
                out_put_str2 = (f'No instances of {year} '
                                f'found in {self.location2} inventory'
                                f'\n---------------\n')

            return f'{out_put_str1}{out_put_str2}'

        elif make:
            results_df1 = self.inventory1[self.inventory1['Make'] == f'{make}']
            results_df2 = self.inventory2[self.inventory2['Make'] == f'{make}']

            out_put_df1 = results_df1
            out_put_df2 = results_df2

            count1 = out_put_df1.shape[0]
            count2 = out_put_df2.shape[0]

            out_put_str1 = (
                f'{self.location1} inventory\nFound {count1} instances of '
                f'{model}'
                f'\n{out_put_df1}\n---------------\n'
            )
            out_put_str2 = (
                f'{self.location2} inventory\nFound {count2} instances of '
                f'{model}'
                f'\n{out_put_df2}\n---------------\n'
            )

            if count1 == 0:
                out_put_str1 = (f'No instances of {make} '
                                f'found in {self.location1} inventory'
                                f'\n---------------\n')
            if count2 == 0:
                out_put_str2 = (f'No instances of {make} '
                                f'found in {self.location2} inventory'
                                f'\n---------------\n')

            return f'{out_put_str1}{out_put_str2}'

        elif model:
            results_df1 = self.inventory1[
                self.inventory1['Model'] == f'{model}']
            results_df2 = self.inventory2[
                self.inventory2['Model'] == f'{model}']

            out_put_df1 = results_df1
            out_put_df2 = results_df2

            count1 = out_put_df1.shape[0]
            count2 = out_put_df2.shape[0]

            out_put_str1 = (
                f'{self.location1} inventory\nFound {count1} instances of '
                f'{model}'
                f'\n{out_put_df1}\n---------------\n'
            )
            out_put_str2 = (
                f'{self.location2} inventory\nFound {count2} instances of '
                f'{model}'
                f'\n{out_put_df2}\n---------------\n'
            )

            if count1 == 0:
                out_put_str1 = (f'No instances of {model} '
                                f'found in {self.location1} inventory'
                                f'\n---------------\n')
            if count2 == 0:
                out_put_str2 = (f'No instances of {model} '
                                f'found in {self.location2} inventory'
                                f'\n---------------\n')

            return f'{out_put_str1}{out_put_str2}'

        else:
            return (
                f'{self.location1} inventory'
                f'\n{self.inventory1.shape[0]} items'
                f'\n{self.inventory1}'
                f'\n---------------'
                f'\n{self.location2} inventory'
                f'\n{self.inventory2.shape[0]} items'
                f'\n{self.inventory2}'
            )

