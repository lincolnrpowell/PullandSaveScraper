"""
THIS FILE SCRAPES BOTH PULL AND SAVE LOCATIONS TO SAVE THE INVENTORY DATA USING THE CLASS INVENTORY_INIT
 RUN THIS FILE FIRST THING BEFORE SEARCHING THROUGH THE DATA TO ENSURE DATA IS UP-TO-DATE
"""
import classfile


classfile.make_file('Spokane',
                              "https://newautopart.net/includes/pullandsave/spokane/yard_locationslist.php")
classfile.make_file('Mead',
                           "https://newautopart.net/includes/pullandsave/mead/yard_locationslist.php")