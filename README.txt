I got the idea for this project when I was doing an engine swap on my Subaru
and was constantly on the Pull and Save websites looking for Subarus with a
specific engine to get parts off of. I had to learn what number in the VIN
represented the engine I was looking for and manually scroll through every
Subaru in both yard inventories looking at each VIN to find the right engine.
By the time I finished the engine swap I got pretty good at this. But what if I
wanted a different engine from a different manufacturer? Like a Toyota 3.5L or
a Chevy 5.3L...I'd have to relearn the process each time! So that's  when I was
inspired to create this program. So I could find any engine in the  inventory
without having to manually scroll through each yard page and look at each VIN
to fid what I needed.

The ultimate goal of this application is to use web scraping and a VIN decode
API or VIN python library to go through the inventory of the Spokane and Mead
Pull and Save locations to show if they have a vehicle in both of their
inventories with particular attributes.

In its current form you can search the inventory by year, make, and model.
Also, engine by manufacturer. It will return at the row at the yard the vehicle
is in along with other useful data like the VIN.

HOW TO USE:
Run the main.py file to open the User Interface. Then click "File" and select
"Update Inventory" to scrape the latest data from the Pull and save websites.
Then input your desired arguments into the Year, Make, Model, and/or Engine
entry boxes to search through the inventory. Note that the "Engine" parameter
needs at least a "Make" parameter input along with it to work. Hit the "Clear"
button to delete the search parameters and results display.

To change the theme of the UI, goto View > Change theme and select between dark
theme and light theme.

Updates:

5/14/24
-GUI updated
-Added cylinder count as a search parameter
-Added Engine model as a result
*Theme change not working at the moment

5/2/24
-Updated the "How to use" instruction in the UI
-Added a display update if no inventory file path is found when searching

4/30/24
-Added a "View" menu to change the theme of the UI

4/25/24
-Added live updates to the text display while the "Update Inventory" function
is running and the API is being called.
-Updated the UI

4/22/24
-Created a UI to input search parameters that will display the data to the
console

4/18/24
-Added the .search_engine function using the NHTSA API to decode the vins for
the engine displacement in liters


4/17/24
-Removed the .search_make, .search_model, and .search_year functions as they're
made obsolete with the .search function
-Updated the 'How to use' and 'CombinedInventory' sections of the READ ME

4/13/24
-Fixed venv issues
-Added requirements.txt
-Deleted the Inventory class and made it a stand-alone function (.make_file())

4/12/24
At this point in the scraper it practically functions the same as the Pull and
Save website does, inventory search wise. The only thing this script does that
the site doesn't is search both location inventory at once. Ideally future
versions of this script will allow you to search for specific engines in the
inventory by VIN weather that be with an API or a python library.