import classfile

inventory = classfile.CombinedInventory("Spokane_inventory.csv", "Mead_inventory.csv")

# print(inventory.search_engine('volkswagen', 3.6))
print(inventory.search_engine('volkswagen', '3.2'))
