The ultimate goal of this application is to use web scraping and a VIN decode API to go through the inventory of the
Spokane and Mead Pull and Save locations to show if they have a vehicle in both of their inventories with particular
attributes.

HOW TO USE:
Run the "Scraper.py" file to update the inventory in the data_cache folder to localize the data. Then go to main.py and
use the functions under the CombinedInventory class to search through the data.

CombinedInventory functions:

.search()
This function can be run with up to three arguments(make, model, year) or none at all. If run without any arguments it
will return the entire inventory of both yard locations. The function has a default argument of 'None' for each year,
make, and model. The 'make' and 'model' arguments must be of the string type. The year argument can be either an integer
or string.

.search_year(year)
This function takes one argument of an integer or string of a year and returns every vehicle of the given year.

.search_make('make')
This function takes one string argument of a vehicle make/manufacturer and returns every vehicle of that make.

.search_model('model')
This function takes one string argument of a vehicle model and returns every model of that vehicle.


Updates:

4/12/24
At this point in the scraper it practically functions the same as the Pull and Save website does, inventory search wise.
The only thing this script does that the site doesn't is search both location inventory at once. Ideally future versions
of this script will allow you to search for specific engines in the inventory by VIN weather that be with an API or a
python library.