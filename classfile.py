import threading
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import os
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from tkinter import messagebox


# VIN decode function (NHTSA API)
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


# Gets data from the decoded VIN
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


# Count lines in text widget
def count_lines(text_widget):
    last_line_index = text_widget.index("end-1c")
    line_number = last_line_index.split('.')[0]
    return int(line_number)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('P&S Inventory Search')
        self.geometry('900x500')
        self.minsize(900, 500)
        self.appearance = 'light'
        ctk.set_appearance_mode(self.appearance)
        ctk.set_default_color_theme('dark-blue')

        # just so my code isn't mad at me
        self.srch_frame = None
        self.search_btn = None
        self.cylinders_entry = None
        self.displacement_entry = None
        self.model_entry = None
        self.make_entry = None
        self.year_entry = None
        self.text_display = None
        self.mead_tv = None
        self.spokane_tv = None
        self.theme_menu = None
        self.view_menu = None
        self.file_menu = None
        self.menubar = None
        # ---------------

        self.how_to_use = ('How to use:'
                           '\n-Click File > Update Inventory to get the '
                           '\nlatest yard inventory.'
                           '\n-Enter search parameters into the input '
                           '\nfields,'
                           'then click Search.'
                           '\n-Results will display in the boxes below.'
                           '\n-If searching for an engine, please \nprovide at'
                           ' least a "Make" parameter. The \nmore parameters '
                           'that are entered, the \nfaster the API call will '
                           'be.'
                           '\n\nNotes:'
                           '\nThe results are only as accurate as the \ninfo '
                           'provided by the Pull and Save \nwebsites and the '
                           'NHSTA API. Some search \nresults may not be truly '
                           'accurate to what \nis actually in the yard.'
                           )

        # Menu bar
        self.menu_bar()
        # Main Grid
        self.columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.rowconfigure((0, 1, 2, 3, 4), weight=1)

        # Widgets
        self.search_frame()
        self.spokane_frame()
        self.mead_frame()
        self.display_frame()

        self.mainloop()

    # Making Widgets
    def menu_bar(self):
        self.menubar = tk.Menu(self)

        self.file_menu = tk.Menu(self.menubar,
                                 tearoff=0,
                                 bg='white',
                                 fg='black'
                                 )
        self.file_menu.add_command(label="Update Inventory",
                                   command=self.update_inventory_btn_func
                                   )
        self.file_menu.add_separator()
        self.file_menu.add_command(label='How to use',
                                   command=self.how_to_use_fuc
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
                                 bg='white',
                                 fg='black'
                                 )
        self.theme_menu = tk.Menu(self.view_menu,
                                  tearoff=0,
                                  bg='white',
                                  fg='black'
                                  )
        self.menubar.add_cascade(menu=self.view_menu,
                                 label='View'
                                 )
        self.view_menu.add_cascade(menu=self.theme_menu,
                                   label='Change theme'
                                   )
        self.theme_menu.add_command(label='Dark theme',
                                    command=self.dark_theme_btn_func
                                    )
        self.theme_menu.add_separator()
        self.theme_menu.add_command(label='Light theme',
                                    command=self.light_theme_btn_func
                                    )
        self.config(menu=self.menubar)

    def search_frame(self):
        self.srch_frame = tk.LabelFrame(self, text='Search Inventory')
        self.srch_frame.grid(row=0,
                             column=0,
                             columnspan=3,
                             rowspan=2,
                             sticky='nsew',
                             padx=2,
                             pady=5
                             )
        self.srch_frame.columnconfigure((0, 1), weight=1)
        self.srch_frame.rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.srch_frame.config(bg="#ededed",
                               font=('Consolas', 12),
                               fg='black',
                               )
        year_label = ctk.CTkLabel(self.srch_frame,
                                  text='Year:',
                                  font=('Consolas', 14)
                                  )
        year_label.grid(row=0,
                        column=0,
                        padx=5,
                        pady=5,
                        sticky='nsew'
                        )
        make_label = ctk.CTkLabel(self.srch_frame,
                                  text='Make:',
                                  font=('Consolas', 14)
                                  )
        make_label.grid(row=1,
                        column=0,
                        padx=5,
                        pady=5,
                        sticky='nsew'
                        )
        model_label = ctk.CTkLabel(self.srch_frame,
                                   text='Model:',
                                   font=('Consolas', 14)
                                   )
        model_label.grid(row=2,
                         column=0,
                         padx=5,
                         pady=5,
                         sticky='nsew'
                         )
        displacement_label = ctk.CTkLabel(self.srch_frame,
                                          text='Liters:',
                                          font=('Consolas', 14)
                                          )
        displacement_label.grid(row=3,
                                column=0,
                                padx=5,
                                pady=5,
                                sticky='nsew'
                                )
        cylinders_label = ctk.CTkLabel(self.srch_frame,
                                       text='Cylinders:',
                                       font=('Consolas', 14)
                                       )
        cylinders_label.grid(row=4,
                             column=0,
                             padx=5,
                             pady=5,
                             sticky='nsew'
                             )
        self.year_entry = ctk.CTkEntry(self.srch_frame)
        self.year_entry.grid(row=0,
                             column=1,
                             padx=5,
                             pady=5,
                             sticky='nsew'
                             )
        self.make_entry = ctk.CTkEntry(self.srch_frame)
        self.make_entry.grid(row=1,
                             column=1,
                             padx=5,
                             pady=5,
                             sticky='nsew'
                             )
        self.model_entry = ctk.CTkEntry(self.srch_frame)
        self.model_entry.grid(row=2,
                              column=1,
                              padx=5,
                              pady=5,
                              sticky='nsew'
                              )
        self.displacement_entry = ctk.CTkEntry(self.srch_frame)
        self.displacement_entry.grid(row=3,
                                     column=1,
                                     padx=5,
                                     pady=5,
                                     sticky='nsew'
                                     )
        self.cylinders_entry = ctk.CTkEntry(self.srch_frame)
        self.cylinders_entry.grid(row=4,
                                  column=1,
                                  padx=5,
                                  pady=5,
                                  sticky='nsew'
                                  )
        self.search_btn = ctk.CTkButton(self.srch_frame,
                                        text='Search',
                                        command=self.search_btn_func
                                        )
        self.search_btn.grid(row=5,
                             column=0,
                             padx=5,
                             pady=5,
                             columnspan=2,
                             sticky='nsew'
                             )

    def display_frame(self):
        self.text_display = ctk.CTkTextbox(self)
        self.text_display.configure(font=('Consolas', 12))
        self.text_display.insert('1.0', self.how_to_use)
        self.text_display.configure(state=tk.DISABLED)
        self.text_display.grid(row=0,
                               column=3,
                               columnspan=3,
                               rowspan=2,
                               padx=10,
                               pady=5,
                               sticky='nsew'
                               )

    def spokane_frame(self):
        frame = tk.LabelFrame(self, text='Spokane Inventory')
        frame.grid(row=2,
                   column=0,
                   columnspan=3,
                   rowspan=3,
                   pady=5,
                   padx=2,
                   sticky='nsew')
        frame.config(height=600,
                     width=400,
                     bg="#ededed",
                     font=('Consolas', 12),
                     fg='black'
                     )
        self.spokane_tv = ttk.Treeview(frame)
        self.spokane_tv.place(relheight=1, relwidth=1)

        treescrolly = tk.Scrollbar(frame, orient='vertical',
                                   command=self.spokane_tv.yview)
        treescrollx = tk.Scrollbar(frame, orient='horizontal',
                                   command=self.spokane_tv.xview)
        self.spokane_tv.config(xscrollcommand=treescrollx.set,
                   yscrollcommand=treescrolly.set)
        treescrollx.pack(side='bottom', fill='x')
        treescrolly.pack(side='right', fill='y')

    def mead_frame(self):
        frame = tk.LabelFrame(self, text='Mead Inventory')
        frame.grid(row=2,
                   column=3,
                   columnspan=3,
                   rowspan=3,
                   padx=4,
                   pady=5,
                   sticky='nsew')
        frame.config(height=600,
                     width=400,
                     bg="#ededed",
                     font=('Consolas', 12),
                     fg='black'
                     )
        self.mead_tv = ttk.Treeview(frame)
        self.mead_tv.place(relheight=1, relwidth=1)

        treescrolly = tk.Scrollbar(frame, orient='vertical',
                                   command=self.mead_tv.yview)
        treescrollx = tk.Scrollbar(frame, orient='horizontal',
                                   command=self.mead_tv.xview)
        self.mead_tv.config(xscrollcommand=treescrollx.set,
                   yscrollcommand=treescrolly.set)
        treescrollx.pack(side='bottom', fill='x')
        treescrolly.pack(side='right', fill='y')

    # -----Functions-----
    def dark_theme_btn_func(self):
        # threading.Thread(target=self.dark_theme).start()
        self.update_text_display("Sorry, this feature is not yet available")

    def light_theme_btn_func(self):
        threading.Thread(target=self.light_theme).start()

    def dark_theme(self):
        ctk.set_appearance_mode('dark')
        self.text_display.configure(font=('Consolas', 12),
                                    bg='#333333',
                                    fg='white'
                                    )
        self.srch_frame.configure(bg="#333333",
                                  fg='white')
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

    def search_btn_func(self):
        threading.Thread(target=self.search_inventory).start()

    def update_inventory_btn_func(self):
        threading.Thread(target=self.scrape_inventory).start()

    def make_file(self, location_name, url):
        init_message = (
            f'Initializing request for {location_name} location...\n'
        )
        self.write_to_text_display(init_message)
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
            self.write_to_text_display(get_request_failed)
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
        self.write_to_text_display(scraping_message)
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
                self.write_to_text_display(url_failed_message)
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
            f'{location_name}_inventory.csv in data_cache \nfolder.'
            f'\n{location_name} initiation complete!{seperator}'
        )
        self.write_to_text_display(writing_csv_message)
        print(writing_csv_message)

    def scrape_inventory(self):
        self.clear_tables()
        self.update_text_display('')
        self.make_file('Spokane',
                       "https://newautopart.net/includes/pullandsave"
                       "/spokane/yard_locationslist.php"
                       )
        self.make_file('Mead',
                       "https://newautopart.net/includes/pullandsave/mead"
                       "/yard_locationslist.php"
                       )
        self.write_to_text_display('INVENTORY UPDATE FINISHED!')

    def search_inventory(self):  # To do: Add Inventory Class and Search func
        # Check to see if the inventory has been scraped
        if not os.path.exists('data_cache'):
            no_data = ('Data not yet scraped!\nPlease update '
                       'the inventory before continuing.')
            self.update_text_display(no_data)
            print(no_data)
        else:
            spokane_inventory = Inventory('Spokane_inventory.csv')
            mead_inventory = Inventory('Mead_inventory.csv')
            year_param = None
            make_param = None
            model_param = None
            displacement_param = None
            cylinders_param = None
            if self.year_entry.get():
                year_param = self.year_entry.get().upper()
            if self.make_entry.get():
                make_param = self.make_entry.get().upper()
            if self.model_entry.get():
                model_param = self.model_entry.get().upper()
            if self.displacement_entry.get():
                displacement_param = self.displacement_entry.get()
            if self.cylinders_entry.get():
                cylinders_param = self.cylinders_entry.get()
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
                spokane_search_count = spokane_inventory.api_search_count(
                    year=year_param,
                    make=make_param,
                    model=model_param
                )
                mead_search_count = mead_inventory.api_search_count(
                    year=year_param,
                    make=make_param,
                    model=model_param
                )
                self.update_text_display(
                    f'Sending {spokane_search_count + mead_search_count} '
                    f'items to the NHTSA API\nThis may take a few moments...'
                )
            if cylinders_param and make_param:
                spokane_search_count = spokane_inventory.api_search_count(
                    year=year_param,
                    make=make_param,
                    model=model_param
                )
                mead_search_count = mead_inventory.api_search_count(year=year_param,
                                                             make=make_param,
                                                             model=model_param
                                                             )
                self.update_text_display(
                    f'Sending {spokane_search_count + mead_search_count} '
                    f'items to the NHTSA API\nThis may take a few moments...'
                )

            spokane_results = spokane_inventory.search(
                year=year_param,
                make=make_param,
                model=model_param,
                displacement=displacement_param,
                cylinders=cylinders_param
            )
            mead_results = mead_inventory.search(
                year=year_param,
                make=make_param,
                model=model_param,
                displacement=displacement_param,
                cylinders=cylinders_param
            )
            self.clear_tables()
            self.clear_params()
            # Populate Spokane Treeview
            self.spokane_tv['columns'] = list(spokane_results.columns)
            self.spokane_tv['show'] = 'headings'
            for column in self.spokane_tv['columns']:
                self.spokane_tv.heading(column, text=column)
                self.spokane_tv.column(column,
                                       width=tk.font.Font().measure(column))
                self.spokane_tv.column('Vin', width=115)

            spokane_df_rows = spokane_results.to_numpy().tolist()
            for row in spokane_df_rows:
                self.spokane_tv.insert('', 'end', values=row)

            # Populate Mead Treeview
            self.mead_tv['columns'] = list(mead_results.columns)
            self.mead_tv['show'] = 'headings'
            for column in self.mead_tv['columns']:
                self.mead_tv.heading(column, text=column)
                self.mead_tv.column(column,
                                    width=tk.font.Font().measure(column))
                self.mead_tv.column('Vin', width=115)

            mead_df_rows = mead_results.to_numpy().tolist()
            for row in mead_df_rows:
                self.mead_tv.insert('', 'end', values=row)

            spokane_count = spokane_results.shape[0]
            mead_count = mead_results.shape[0]

            if year_param and make_param and model_param and displacement_param and cylinders_param:
                self.update_text_display(
                    f'Found {spokane_count+mead_count} instances of '
                    f'{year_param} {make_param} {model_param} '
                    f'{displacement_param}L {cylinders_param}cyl'
                    f'\n{spokane_count} in Spokane'
                    f'\n{mead_count} in Mead'
                )
            if year_param and make_param and model_param and displacement_param:
                self.update_text_display(
                    f'Found {spokane_count + mead_count} instances of '
                    f'{year_param} {make_param} {model_param} '
                    f'{displacement_param}L'
                    f'\n{spokane_count} in Spokane'
                    f'\n{mead_count} in Mead'
                )
            elif year_param and make_param and model_param and cylinders_param:
                self.update_text_display(
                    f'Found {spokane_count + mead_count} instances of '
                    f'{year_param} {make_param} {model_param} '
                    f'{cylinders_param}cyl'
                    f'\n{spokane_count} in Spokane'
                    f'\n{mead_count} in Mead'
                )
            elif make_param and model_param and displacement_param and cylinders_param:
                self.update_text_display(
                    f'Found {spokane_count + mead_count} instances of '
                    f'{make_param} {model_param} {displacement_param}L '
                    f'{cylinders_param}cyl'
                    f'\n{spokane_count} in Spokane'
                    f'\n{mead_count} in Mead'
                )
            elif make_param and model_param and displacement_param:
                self.update_text_display(
                    f'Found {spokane_count + mead_count} instances of '
                    f'{make_param} {model_param} {displacement_param}L '
                    f'\n{spokane_count} in Spokane'
                    f'\n{mead_count} in Mead'
                )
            elif make_param and model_param and cylinders_param:
                self.update_text_display(
                    f'Found {spokane_count + mead_count} instances of '
                    f'{make_param} {model_param} {cylinders_param}cyl'
                    f'\n{spokane_count} in Spokane'
                    f'\n{mead_count} in Mead'
                )
            elif make_param and displacement_param and cylinders_param:
                self.update_text_display(
                    f'Found {spokane_count + mead_count} instances of '
                    f'{make_param} {displacement_param}L {cylinders_param}cyl'
                    f'\n{spokane_count} in Spokane'
                    f'\n{mead_count} in Mead'
                )
            elif make_param and displacement_param:
                self.update_text_display(
                    f'Found {spokane_count + mead_count} instances of '
                    f'{make_param} {displacement_param}L'
                    f'\n{spokane_count} in Spokane'
                    f'\n{mead_count} in Mead'
                )
            elif make_param and cylinders_param:
                self.update_text_display(
                    f'Found {spokane_count + mead_count} instances of '
                    f'{make_param} {cylinders_param}cyl'
                    f'\n{spokane_count} in Spokane'
                    f'\n{mead_count} in Mead'
                )
            elif year_param and make_param and model_param:
                self.update_text_display(
                    f'Found {spokane_count + mead_count} instances of '
                    f'{year_param} {make_param} {model_param}'
                    f'\n{spokane_count} in Spokane'
                    f'\n{mead_count} in Mead'
                )
            elif year_param and make_param:
                self.update_text_display(
                    f'Found {spokane_count + mead_count} instances of '
                    f'{year_param} {make_param}'
                    f'\n{spokane_count} in Spokane'
                    f'\n{mead_count} in Mead'
                )
            elif year_param and model_param:
                self.update_text_display(
                    f'Found {spokane_count + mead_count} instances of '
                    f'{year_param} {model_param}'
                    f'\n{spokane_count} in Spokane'
                    f'\n{mead_count} in Mead'
                )
            elif make_param and model_param:
                self.update_text_display(
                    f'Found {spokane_count + mead_count} instances of '
                    f'{make_param} {model_param}'
                    f'\n{spokane_count} in Spokane'
                    f'\n{mead_count} in Mead'
                )
            elif year_param:
                self.update_text_display(
                    f'Found {spokane_count + mead_count} instances of '
                    f'{year_param}'
                    f'\n{spokane_count} in Spokane'
                    f'\n{mead_count} in Mead'
                )
            elif make_param:
                self.update_text_display(
                    f'Found {spokane_count + mead_count} instances of '
                    f'{make_param}'
                    f'\n{spokane_count} in Spokane'
                    f'\n{mead_count} in Mead'
                )
            elif model_param:
                self.update_text_display(
                    f'Found {spokane_count + mead_count} instances of '
                    f'{model_param}'
                    f'\n{spokane_count} in Spokane'
                    f'\n{mead_count} in Mead'
                )
            else:
                self.update_text_display(
                    f'{spokane_count + mead_count} total vehicles'
                )

    def clear_tables(self):
        self.spokane_tv.delete(*self.spokane_tv.get_children())
        self.mead_tv.delete(*self.mead_tv.get_children())

    def clear_params(self):
        self.year_entry.delete(0, tk.END)
        self.make_entry.delete(0, tk.END)
        self.model_entry.delete(0, tk.END)
        self.displacement_entry.delete(0, tk.END)
        self.cylinders_entry.delete(0, tk.END)
        self.text_display.configure(state=tk.NORMAL)
        self.text_display.delete(1.0, tk.END)
        self.text_display.configure(state=tk.DISABLED)

    def update_text_display(self, content):
        self.text_display.configure(state=tk.NORMAL)
        self.text_display.delete(1.0, tk.END)
        self.text_display.insert(tk.END, content)
        self.text_display.configure(state=tk.DISABLED)

    def write_to_text_display(self, content):
        self.text_display.configure(state=tk.NORMAL)
        self.text_display.insert(tk.END, content)
        self.text_display.configure(state=tk.DISABLED)

    def how_to_use_fuc(self):
        self.update_text_display(self.how_to_use)

    def scrape_update(self, content):
        self.text_display.configure(state=tk.NORMAL)
        if count_lines(self.text_display) < 4:
            self.text_display.delete(3.0, tk.END)
        else:
            self.text_display.delete(9.0, tk.END)
        self.text_display.insert(tk.END, content)


class Inventory:
    def __init__(self, file):
        self.file = file
        self.location = file.split('-')[0]
        file_path = os.path.join('data_cache', f'{self.file}')

        self.inventory = pd.read_csv(file_path)

    def search(self,
               year=None,
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
                make = str(make.upper())
        if model:
            model = str(model.upper())
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
            results = self.inventory[
                (self.inventory['Year'] == year) &
                (self.inventory['Make'] == make) &
                (self.inventory['Model'] == model)
                ]

            df_copy = results.copy()

            api_message = (f'Sending {df_copy.shape[0]} '
                           f'items to NHTSA API.'
                           f'\nThis may take a few moments...')
            print(api_message)

            for index, row in df_copy.iterrows():
                vin = row['Vin']
                decode_data = vin_decode(vin)
                if decode_data:
                    df_copy.at[index, 'Liters'] = get_displacement(
                        decode_data
                    )
                    df_copy.at[index, 'Cylinders'] = get_cylinder_count(
                        decode_data
                    )
                    df_copy.at[index, 'Engine Model'] = get_engine_model(
                        decode_data
                    )

            out_put_df = df_copy[(df_copy['Liters'] == displacement) &
                                 (df_copy['Cylinders'] == cylinders)
                                 ]

            return out_put_df

        elif make and model and displacement and cylinders:
            results = self.inventory[
                (self.inventory['Make'] == make) &
                (self.inventory['Model'] == model)
                ]

            df_copy = results.copy()

            api_message = (f'Sending {df_copy.shape[0]} '
                           f'items to NHTSA API.'
                           f'\nThis may take a few moments...')
            print(api_message)

            for index, row in df_copy.iterrows():
                vin = row['Vin']
                decode_data = vin_decode(vin)
                if decode_data:
                    df_copy.at[index, 'Liters'] = get_displacement(
                        decode_data
                    )
                    df_copy.at[index, 'Cylinders'] = get_cylinder_count(
                        decode_data
                    )
                    df_copy.at[index, 'Engine Model'] = get_engine_model(
                        decode_data
                    )

            out_put_df = df_copy[(df_copy['Liters'] == displacement) &
                                 (df_copy['Cylinders'] == cylinders)
                                 ]

            return out_put_df

        elif make and displacement and cylinders:
            results = self.inventory[self.inventory['Make'] == make]

            df_copy = results.copy()

            api_message = (f'Sending {df_copy.shape[0]} '
                           f'items to NHTSA API.'
                           f'\nThis may take a few moments...')
            print(api_message)

            for index, row in df_copy.iterrows():
                vin = row['Vin']
                decode_data = vin_decode(vin)
                if decode_data:
                    df_copy.at[index, 'Liters'] = get_displacement(
                        decode_data
                    )
                    df_copy.at[index, 'Cylinders'] = get_cylinder_count(
                        decode_data
                    )
                    df_copy.at[index, 'Engine Model'] = get_engine_model(
                        decode_data
                    )

            out_put_df = df_copy[(df_copy['Liters'] == displacement) &
                                 (df_copy['Cylinders'] == cylinders)
                                 ]

            return out_put_df

        elif year and make and model and cylinders:
            results = self.inventory[
                (self.inventory['Year'] == year) &
                (self.inventory['Make'] == make) &
                (self.inventory['Model'] == model)
                ]

            df_copy = results.copy()

            api_message = (f'Sending {df_copy.shape[0]} '
                           f'items to NHTSA API.'
                           f'\nThis may take a few moments...')
            print(api_message)

            for index, row in df_copy.iterrows():
                vin = row['Vin']
                decode_data = vin_decode(vin)
                if decode_data:
                    df_copy.at[index, 'Liters'] = get_displacement(
                        decode_data
                    )
                    df_copy.at[index, 'Cylinders'] = get_cylinder_count(
                        decode_data
                    )
                    df_copy.at[index, 'Engine Model'] = get_engine_model(
                        decode_data
                    )

            out_put_df = df_copy[df_copy['Cylinders'] == cylinders]

            return out_put_df

        elif year and make and model and displacement:
            results = self.inventory[
                (self.inventory['Year'] == year) &
                (self.inventory['Make'] == make) &
                (self.inventory['Model'] == model)
                ]

            df_copy = results.copy()

            api_message = (f'Sending {df_copy.shape[0]} '
                           f'items to NHTSA API.'
                           f'\nThis may take a few moments...')
            print(api_message)

            for index, row in df_copy.iterrows():
                vin = row['Vin']
                decode_data = vin_decode(vin)
                if decode_data:
                    df_copy.at[index, 'Liters'] = get_displacement(
                        decode_data
                    )
                    df_copy.at[index, 'Cylinders'] = get_cylinder_count(
                        decode_data
                    )
                    df_copy.at[index, 'Engine Model'] = get_engine_model(
                        decode_data
                    )

            out_put_df = df_copy[df_copy['Liters'] == displacement]

            return out_put_df

        elif make and model and cylinders:
            results = self.inventory[
                (self.inventory['Make'] == make) &
                (self.inventory['Model'] == model)
                ]

            df_copy = results.copy()

            api_message = (f'Sending {df_copy.shape[0]} '
                           f'items to NHTSA API.'
                           f'\nThis may take a few moments...')
            print(api_message)

            for index, row in df_copy.iterrows():
                vin = row['Vin']
                decode_data = vin_decode(vin)
                if decode_data:
                    df_copy.at[index, 'Liters'] = get_displacement(
                        decode_data
                    )
                    df_copy.at[index, 'Cylinders'] = get_cylinder_count(
                        decode_data
                    )
                    df_copy.at[index, 'Engine Model'] = get_engine_model(
                        decode_data
                    )

            out_put_df = df_copy[df_copy['Cylinders'] == cylinders]

            return out_put_df

        elif make and model and displacement:
            results = self.inventory[
                (self.inventory['Make'] == make) &
                (self.inventory['Model'] == model)
                ]

            df_copy = results.copy()

            api_message = (f'Sending {df_copy.shape[0]} '
                           f'items to NHTSA API.'
                           f'\nThis may take a few moments...')
            print(api_message)

            for index, row in df_copy.iterrows():
                vin = row['Vin']
                decode_data = vin_decode(vin)
                if decode_data:
                    df_copy.at[index, 'Liters'] = get_displacement(
                        decode_data
                    )
                    df_copy.at[index, 'Cylinders'] = get_cylinder_count(
                        decode_data
                    )
                    df_copy.at[index, 'Engine Model'] = get_engine_model(
                        decode_data
                    )

            out_put_df = df_copy[df_copy['Liters'] == displacement]

            return out_put_df

        elif make and cylinders:
            results = self.inventory[self.inventory['Make'] == make]

            df_copy = results.copy()

            api_message = (f'Sending {df_copy.shape[0]} '
                           f'items to NHTSA API.'
                           f'\nThis may take a few moments...')
            print(api_message)

            for index, row in df_copy.iterrows():
                vin = row['Vin']
                decode_data = vin_decode(vin)
                if decode_data:
                    df_copy.at[index, 'Liters'] = get_displacement(
                        decode_data
                    )
                    df_copy.at[index, 'Cylinders'] = get_cylinder_count(
                        decode_data
                    )
                    df_copy.at[index, 'Engine Model'] = get_engine_model(
                        decode_data
                    )

            out_put_df = df_copy[df_copy['Cylinders'] == cylinders]

            return out_put_df

        elif make and displacement:
            results = self.inventory[self.inventory['Make'] == make]

            df_copy = results.copy()

            api_message = (f'Sending {df_copy.shape[0]} '
                           f'items to NHTSA API.'
                           f'\nThis may take a few moments...')
            print(api_message)

            for index, row in df_copy.iterrows():
                vin = row['Vin']
                decode_data = vin_decode(vin)
                if decode_data:
                    df_copy.at[index, 'Liters'] = get_displacement(
                        decode_data
                    )
                    df_copy.at[index, 'Cylinders'] = get_cylinder_count(
                        decode_data
                    )
                    df_copy.at[index, 'Engine Model'] = get_engine_model(
                        decode_data
                    )

            out_put_df = df_copy[df_copy['Liters'] == displacement]

            return out_put_df

        elif year and make and model:
            results = self.inventory[
                (self.inventory['Year'] == year) &
                (self.inventory['Make'] == make) &
                (self.inventory['Model'] == model)
                ]
            return results

        elif year and make:
            results = self.inventory[
                (self.inventory['Year'] == year) &
                (self.inventory['Make'] == make)
                ]
            return results

        elif year and model:
            results = self.inventory[
                (self.inventory['Year'] == year) &
                (self.inventory['Model'] == model)
                ]
            return results

        elif make and model:
            results = self.inventory[
                (self.inventory['Make'] == make) &
                (self.inventory['Model'] == model)
                ]
            return results

        elif year:
            results = self.inventory[self.inventory['Year'] == year]
            return results

        elif make:
            results = self.inventory[self.inventory['Make'] == make]
            return results

        elif model:
            results = self.inventory[self.inventory['Model'] == model]
            return results

        else:
            return self.inventory

    def api_search_count(self, year=None, make=None, model=None):
        if make:
            if make.upper() == 'CHEVY':
                make = 'CHEVROLET'
            elif make.upper() == 'NISSAN' or make.upper() == 'DATSUN':
                make = 'DATSUN - NISSAN'
            else:
                make = make.upper()
        if model:
            model = model.upper()
        if year:
            year = int(year)

        if year and make and model:
            results = self.inventory[(self.inventory['Year'] == year) &
                                     (self.inventory['Make'] == make) &
                                     (self.inventory['Model'] == model)
                                     ]
            return results.shape[0]

        elif year and make:
            results = self.inventory[(self.inventory['Year'] == year) &
                                     (self.inventory['Make'] == make)
                                     ]
            return results.shape[0]
        elif year and model:
            results = self.inventory[(self.inventory['Year'] == year) &
                                     (self.inventory['Model'] == model)
                                     ]
            return results.shape[0]
        elif make and model:
            results = self.inventory[(self.inventory['Make'] == make) &
                                     (self.inventory['Model'] == model)
                                     ]
            return results.shape[0]
        elif year:
            results = self.inventory[self.inventory['Year'] == year]
            return results.shape[0]
        elif make:
            results = self.inventory[self.inventory['Make'] == make]
            return results.shape[0]
        elif model:
            results = self.inventory[self.inventory['Model'] == model]
            return results.shape[0]


