import classfile

inventory = classfile.CombinedInventory("Spokane_inventory.csv", "Mead_inventory.csv")

print(inventory.search(make='subaru'))
print(inventory.search_engine('subaru', '3.0'))

