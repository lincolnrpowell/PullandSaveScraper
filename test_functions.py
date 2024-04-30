import classfile

inventory = classfile.CombinedInventory('Spokane_inventory.csv',
                                        'Mead_inventory.csv')

print(inventory.search(year='2004', make='subaru', model='legacy', liters=3.0))
print(inventory.search(year='1995', make='subaru', model='impreza'))
print(inventory.search(year='2000', make='toyota'))
print(inventory.search(year=1999))
print(inventory.search(make='chevy'))
print(inventory.search(make='nissan'))
print(inventory.search(make='datsun'))
print(inventory.search(model='f150'))
print(inventory.search(model='golf'))
print(inventory.search(liters=2.5))
print(inventory.search(model='impreza', liters=2.2))
print(inventory.search(year=1995, liters=4.4))
print(inventory.search(make='volkswagen', liters=3.2))
print(inventory.search(make='bmw', liters=2.5))
print(inventory.search())
