import json

# Load the JSON data from the file
with open('rubberducks.json', 'r') as file:
    rubber_ducks_data = json.load(file)

# Iterate over the ducks and print their names and colors
for duck in rubber_ducks_data['ducks']:
    print(duck['name'])
    print(duck['color'])