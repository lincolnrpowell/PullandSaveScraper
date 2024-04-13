import classfile

inventory = classfile.CombinedInventory("Spokane_inventory.csv", "Mead_inventory.csv")

print(inventory.search('subaru'))

