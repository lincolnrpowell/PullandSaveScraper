The ultimate goal of this application is to use web scraping and a VIN decode API or VIN python library to go through
the inventory of the Spokane and Mead Pull and Save locations to show if they have a vehicle in both of their
inventories with particular attributes.

In its current form you can search the inventory by year, make, and model. Also, engine by manufacturer. It will
return at the row at the yard the vehicle is in along with other useful data like the VIN.

HOW TO USE:
Run the main.py file to open the UI. Then click "File" and select "Update Inventory" to scrape the latest data from the
Pull and save websites. Then input your desired arguments into the Year, Make, Model, and/or Engine entry boxes to
search through the inventory. Note that the "Engine" parameter needs at least a "Make" parameter along with it to work.
Hit the "Clear" button to clear the search parameters and results display.

Updates:

4/12/24
At this point in the scraper it practically functions the same as the Pull and Save website does, inventory search wise.
The only thing this script does that the site doesn't is search both location inventory at once. Ideally future versions
of this script will allow you to search for specific engines in the inventory by VIN weather that be with an API or a
python library.

4/13/24
-Fixed venv issues
-Added requirements.txt
-Deleted the Inventory class and made it a stand-alone function (.make_file())

4/17/24
-Removed the .search_make, .search_model, and .search_year functions as they're made obsolete with the .search function
-Updated the 'How to use' and 'CombinedInventory' sections of the READ ME

4/18/24
-Added the .search_engine function using the NHTSA API to decode the vins for the engine displacement in liters

4/22/24
-Created a UI to input search parameters that will display the data to the console

4/25/24
-Added live updates to the text display while the "Update Inventory" function is running and the API is being called.
-Updated the UI