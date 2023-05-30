MODEL_CO2 = {
    'models': ["co2_lite"],
    'vehicle': {'bicyle': 0, 'e-train': 0, 'truck-base': 1, 'trailer': 1.5},
    'fuel':  {'diesel': 74.0, 'gasoline': 73.3, 'crude-oil': 73.3, 'natural-gas': 55.8},
}

def co2_lite(dist, coef):
    """simplistic CO2 estimate for distance with vehicle coef"""
    return dist * coef

def co2(d):
    """CO2 estimate TBD"""
    return 0

