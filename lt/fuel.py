FUEL = {
    'url': "https://raw.githubusercontent.com/czanalytics/multimodal-shipping/main/dat/fuel_price/",
    'files': ["fuel-price-23-05-15.csv", "fuel-price-23-05-22.csv"],
    'models': ["price_latest", "price_trend", "price_ai"],
}

def fuel_conf():
    return FUEL

def price_latest(p):
    """Price estimate assuming no change"""
    change = 0
    pe  =  p[-1] +  change 
    return pe

def price_trend(p):
    """Simple trend following estimate"""
    change = p[-1] - p[-2]
    pe = p[-1] + change
    return pe

def price_ai(p, args):
    """Advanced price prediction, TBD"""
    change = 0  # f(args)
    latest = p[-1] # smooth(latest)    
    pe = latest + change
    return  pe

