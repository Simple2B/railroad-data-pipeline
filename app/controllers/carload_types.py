CARLOAD_TYPES = (
    {'ID': 1, 'type': "All Other Carloads"},
    {'ID': 2, 'type': "Chemicals"},
    {'ID': 3, 'type': "Coal"},
    {'ID': 4, 'type': "Coke"},
    {'ID': 5, 'type': "Containers"},
    {'ID': 6, 'type': "Crushed Stone, Sand and Gravel"},
    {'ID': 7, 'type': "Farm Products, Except Grain"},
    {'ID': 8, 'type': "Food and Kindred Products"},
    {'ID': 9, 'type': "Grain"},
    {'ID': 10, 'type': "Grain Mill Products"},
    {'ID': 11, 'type': "Iron and Steel Scrap"},
    {'ID': 12, 'type': "Lumber and Wood Products"},
    {'ID': 13, 'type': "Metallic Ores"},
    {'ID': 14, 'type': "Metals and Products"},
    {'ID': 15, 'type': "Motor Vehicles and Equipment"},
    {'ID': 16, 'type': "Nonmetallic Minerals"},
    {'ID': 17, 'type': "Petroleum Products"},
    {'ID': 18, 'type': "Primary Forest Products"},
    {'ID': 19, 'type': "Pulp, Paper and Allied Products"},
    {'ID': 20, 'type': "Stone, Clay and Glass Products"},
    {'ID': 21, 'type': "Trailer"},
    {'ID': 22, 'type': "Waste and Scrap Materials"},
)


def find_carload_id(prod_name):
    for carload in CARLOAD_TYPES:
        if prod_name.lower() == carload['type'].lower():
            return carload['ID']
