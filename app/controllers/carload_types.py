CARLOAD_TYPES = (
    {"ID": 1, "type": ["All Other Carloads", "All Other", "OTHER"]},
    {"ID": 2, "type": ["Chemicals", "Energy, Chemicals & Plastics"]},
    {"ID": 3, "type": ["Coal"]},
    {"ID": 4, "type": ["Coke"]},
    {"ID": 5, "type": ["Containers", "Container"]},
    {
        "ID": 6,
        "type": ["Crushed Stone, Sand and Gravel", "Crushed Stone, Sand & Gravel"],
    },
    {"ID": 7, "type": ["Farm Products, Except Grain", "Farm Products (excl. Grain)"]},
    {
        "ID": 8,
        "type": [
            "Food and Kindred Products",
            "Food Products",
            "Food & Kindred Products",
            "FOOD",
        ],
    },
    {"ID": 9, "type": ["Grain"]},
    {"ID": 10, "type": ["Grain Mill Products", "GRAIN MILL"]},
    {"ID": 11, "type": ["Iron and Steel Scrap", "Iron & Steel Scrap"]},
    {
        "ID": 12,
        "type": [
            "Lumber and Wood Products",
            "Lumber & Wood Products",
            "Lumber & Wood Products except Furniture",
            "LUMBER/WOOD",
            "FOREST PRODUCTS",
            "Forest Products",
        ],
    },
    {"ID": 13, "type": ["Metallic Ores", "Metalic Ores"]},
    {
        "ID": 14,
        "type": [
            "Metals and Products",
            "Primary Metal Products",
            "Metals & Products",
            "METALS",
            "Metals, Minerals & Consumer Products",
        ],
    },
    {
        "ID": 15,
        "type": [
            "Motor Vehicles and Equipment",
            "Motor Vehicles and Parts",
            "Motor Vehicles & Equipment",
        ],
    },
    {
        "ID": 16,
        "type": [
            "Nonmetallic Minerals",
            "Non Metalic Minerals",
            "NONMETALIC MINERALS",
            "Non Metallic Minerals",
        ],
    },
    {
        "ID": 17,
        "type": ["Petroleum Products", "Petroleum & Petroleum Products", "PETROLEUM"],
    },
    {"ID": 18, "type": ["Primary Forest Products"]},
    {
        "ID": 19,
        "type": [
            "Pulp, Paper and Allied Products",
            "Pulp & Paper Products",
            "Pulp, Paper & Allied Products",
            "Pulp, Paper, & Allied Products",
            "PULP/PAPER",
        ],
    },
    {"ID": 20, "type": ["Stone, Clay and Glass Products"]},
    {"ID": 21, "type": ["Trailer", "Trailers"]},
    {"ID": 22, "type": ["Waste and Scrap Materials", "Waste & Nonferrous Scrap"]},
)


def find_carload_id(prod_name):
    for carload in CARLOAD_TYPES:
        for t in carload["type"]:
            if prod_name.lower() == t.lower():
                return carload["ID"]
