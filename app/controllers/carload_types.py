CARLOAD_TYPES = (
    {"ID": 1, "type": ["All Other Carloads", "All Other", "OTHER"]},
    {"ID": 2, "type": ["Chemicals", "Energy, Chemicals & Plastics"]},
    {"ID": 3, "type": ["Coal"]},
    {"ID": 4, "type": ["Coke"]},
    {
        "ID": 5,
        "type": [
            "Containers",
            "Container",
            "Intermodal Containers",
            "Intermodal Containers",
        ],
    },
    {
        "ID": 6,
        "type": [
            "Crushed Stone, Sand and Gravel",
            "Crushed Stone, Sand & Gravel",
            "Crushed Stone, Gravel & Sand",
            "Crushed Stone",
            "SAND/GRAVEL",
        ],
    },
    {
        "ID": 7,
        "type": [
            "Farm Products, Except Grain",
            "Farm Products (excl. Grain)",
            "Farm Products",
            "FARM (NO GRAIN)",
            "Fertilizer & Sulphur",
            "Farm Products Ex Grain",
        ],
    },
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
    {
        "ID": 11,
        "type": [
            "Iron and Steel Scrap",
            "Iron & Steel Scrap",
            "Iron & Steel Scrap",
            "Iron And Steel Scrap ",
            "IRON & STEEL SCRAP",
        ],
    },
    {
        "ID": 12,
        "type": [
            "Lumber and Wood Products",
            "Lumber & Wood Products",
            "Lumber & Wood Products except Furniture",
            "LUMBER/WOOD",
            "Lumber & Wood Products",
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
            "Metal Products",
        ],
    },
    {
        "ID": 15,
        "type": [
            "Motor Vehicles and Equipment",
            "Motor Vehicles and Parts",
            "Motor Vehicles & Equipment",
            "MOTOR VEHICLES",
            "Automotive",
        ],
    },
    {
        "ID": 16,
        "type": [
            "Nonmetallic Minerals",
            "Non Metalic Minerals",
            "NONMETALIC MINERALS",
            "Non Metallic Minerals",
            "Non-Metallic Minerals (incl. Phosphates)",
            "Potash",
        ],
    },
    {
        "ID": 17,
        "type": ["Petroleum Products", "Petroleum & Petroleum Products", "PETROLEUM"],
    },
    {
        "ID": 18,
        "type": [
            "Primary Forest Products",
            "FOREST PRODUCTS",
            "Forest Products",
        ],
    },
    {
        "ID": 19,
        "type": [
            "Pulp, Paper and Allied Products",
            "Pulp & Paper Products",
            "Pulp, Paper & Allied Products",
            "Pulp, Paper, & Allied Products",
            "PULP/PAPER",
            "Pulp & Paper Products",
        ],
    },
    {
        "ID": 20,
        "type": [
            "Stone, Clay and Glass Products",
            "Stone, Clay & Glass Products",
            "Stone, Clay & Glass Products",
            "Stone, Clay, Glass",
            "STONE/CLAY/GLASS",
        ],
    },
    {
        "ID": 21,
        "type": [
            "Trailer",
            "Intermodal Trailers",
            "Trailers",
            "Intermodal Trailers",
            "Trailers",
            "TRAILERS",
            "Intermodal",
        ],
    },
    {
        "ID": 22,
        "type": [
            "Waste and Scrap Materials",
            "Waste & Nonferrous Scrap",
            "Waste & Scrap Materials",
            "WASTE/SCRAP",
        ],
    },
)

ALL_PROD_TYPES = []
for names in [i["type"] for i in CARLOAD_TYPES]:
    ALL_PROD_TYPES += names


def find_carload_id(prod_name):
    for carload in CARLOAD_TYPES:
        for t in carload["type"]:
            if prod_name.lower() == t.lower():
                return carload["ID"]
