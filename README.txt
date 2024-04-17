The ultimate goal of this application is to use web scraping and a VIN decode API to go through the inventory of the
Spokane and Mead Pull and Save locations to show if they have a vehicle in both of their inventories with particular
attributes.

HOW TO USE:
Ensure the packages from the 'requirements.txt' file have been installed. Then r]un the "Scraper.py" file to update the
inventory in the data_cache folder and to localize the data. Then go to main.py, make sure the
classfile.CombineInventory class is set to a variable (i.e. 'inventory') and use the .search() function from the
CombinedInventory class in a print statement to search through the data (i.e. print(inventory.search())

CombinedInventory functions:

.search()
This function can be run with up to three arguments(make, model, year) or none at all. If run without any arguments it
will return the entire inventory of both yard locations. The function has a default argument of 'None' for year, make
and model. The 'make' and 'model' arguments must be of the string type. The year argument can be either an integer
or string.

Updates:

4/12/24
At this point in the scraper it practically functions the same as the Pull and Save website does, inventory search wise.
The only thing this script does that the site doesn't is search both location inventory at once. Ideally future versions
of this script will allow you to search for specific engines in the inventory by VIN weather that be with an API or a
python library.

4/13/24
-Fixed venv issues
-Added requirements.txt
-Deleted the Inventory class and made it a stand_alone function (.make_file())

4/17/24
-Removed the .search_make, .search_model, and .search_year functions as they're made obsolete with the .search function
-Updated the 'How to use' and 'CombinedInventory' sections of the READ ME
