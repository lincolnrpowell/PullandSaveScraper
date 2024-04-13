import classfile

# THIS FILE SCRAPES BOTH PULL AND SAVE LOCATIONS TO SAVE THE INVENTORY DATA USING THE CLASS INVENTORY_INIT
# RUN THIS FILE FIRST THING BEFORE SEARCHING THROUGH THE DATA TO ENSURE DATA IS UP-TO-DATE


spokane = classfile.InventoryInit('Spokane',
                              "https://newautopart.net/includes/pullandsave/spokane/yard_locationslist.php")
mead = classfile.InventoryInit('Mead',
                           "https://newautopart.net/includes/pullandsave/mead/yard_locationslist.php")
