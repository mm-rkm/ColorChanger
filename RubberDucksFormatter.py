


class RubberDucksFormatter:
    def __init__(self, ducks):
        self.ducks = ducks

    def format_ducks(self):
        return [f"Duck Name: {duck['name']}, Color: {duck['color']}" for duck in self.ducks]

# Example usage
# import json
# ducks_json = '''
# {
#     "ducks": [
#         {
#             "name": "Ben",
#             "color": "Brown"
#         },
#         {
#             "name": "Younis",
#             "color": "Yellow"
#         }
#     ]
# }
# '''

# ducks_data = json.loads(ducks_json)['ducks']
# formatter = RubberDucksFormatter(ducks_data)
# print(formatter.format_ducks()) 