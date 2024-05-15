import classfile

inventory = classfile.CombinedInventory('Spokane_inventory.csv',
                                        'Mead_inventory.csv')

print(inventory.search(year='2004', make='subaru', model='legacy', displacement=3.0))
print(inventory.search(year='1995', make='subaru', model='impreza'))
print(inventory.search(year='2000', make='toyota'))
print(inventory.search(year=1999))
print(inventory.search(make='chevy'))
print(inventory.search(make='nissan'))
print(inventory.search(make='datsun'))
print(inventory.search(model='f150'))
print(inventory.search(model='golf'))
print(inventory.search(displacement=2.5))
print(inventory.search(cylinders=6))
print(inventory.search(model='impreza', displacement=2.2))
print(inventory.search(model='Legacy', cylinders=4))
print(inventory.search(year=1995, displacement=4.4))
print(inventory.search(make='mercedes', cylinders=6))
print(inventory.search(make='volkswagen', displacement=3.2))
print(inventory.search(make='bmw', displacement=2.5))
print(inventory.search())
