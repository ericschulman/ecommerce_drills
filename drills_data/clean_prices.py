import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def calc_rank(prices):
    return prices['rank'] + (prices['rank'] == 0)*21

def calc_inven(prices):
    quants = {'AMZN':'quantity3','WMT':'quantity3', 'HD':'quantity1', 'LOW':'quantity1' }
    platforms  = ['AMZN','WMT','HD','LOW']
    inventory = prices['in_stock'].fillna(0)
    
    for plat in platforms:
        inventory[prices['platform']==plat] = prices[quants[plat]][prices['platform']==plat].fillna(0)
    
    inventory = (inventory == 0)*prices['in_stock'].fillna(0)*prices['max_qty'].fillna(0) + inventory

    return inventory
        
def calc_promo(prices):
    platforms = ['AMZN','WMT','HD','LOW']
    promo_dict = {'AMZN':'quantity4','WMT':'quantity2', 'HD':'quantity2', 'LOW':'quantity2' }
    promo = 1.*(prices['price'] <= prices['list_price'])
    promo = promo.fillna(0)
    for plat in platforms:
        plat_promo = np.array(prices[promo_dict[plat]][prices['platform']==plat].fillna(0))
        promo[prices['platform']==plat] = np.minimum(plat_promo + promo[prices['platform']==plat],1)
    return promo
    
def calc_ship(prices):
    ship = ( prices['arrives'] - prices['date'] )/1.0e3
    ship = ship.fillna(7)
    
    meanings = {'FREE Shipping on orders over $25':2, '—':2,
                'Free delivery':2,'Next-day delivery':1,
                'Same-day delivery':1, 'Available!':2,
               'Delivery available':7, 'EXPEDITED':2, 
                'ONE_DAY':1, 'STANDARD':7 }
    
    lookup = lambda x :  meanings[x] if x in meanings.keys() else 7
    
    ship_words =  prices['shipping'].apply(lookup)    
    ship = ship_words*(ship_words !=7) + ship*(ship_words == 7)
    return ship_words

def calc_purch(prices):
    pass

if __name__ == "__main__":
    prices = pd.read_csv("prices.csv")
    prices['calc_rank'] = calc_rank(prices)
    prices['calc_inven'] = calc_inven(prices)
    prices['calc_promo'] = calc_promo(prices)
    prices['calc_ship'] = calc_ship(prices)
    prices['calc_purch'] = calc_purch(prices)
    prices.to_csv(r'clean_prices.csv', index = False, header=True)
    
