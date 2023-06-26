
def price_est(d, price_km=2, price_min=100, err=0.1):
    """
    Simplistic transportation price estimate
    price, p [EUR] =  straight_line(distance, d [km], price/km [EUR/km], price_min [EUR])
    """
    p = price_km * d + price_min
    p_lo = p - p * err
    p_hi = p + p * err

    return p, p_lo, p_hi

def eta_est(d, v=100, err=0.1):
    """
    Simplistic transportation time estimate
    time, t [h] = distance, d [km] / speed, v [km/h]
    """
    t = d / v
    t_lo = t - t * err
    t_hi = t + t * err
    return t, t_lo, t_hi

def co_est(d, c=100, err=0.2):
    """
    Simplistic transportation CO2 exhaust estimate
    CO2 [g] =  distance, d [km] * CO2, c [g/km]
    """
    co = d * c
    co_lo = co - co * err
    co_hi = co + co * err
    return co, co_lo, co_hi

