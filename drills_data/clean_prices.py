import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import copy

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

def add_clean_columns(prices):
    cleaned_columns = ['calc_rank', 'calc_inven', 'calc_promo', 'calc_ship']
    for column in cleaned_columns:
        prices[column] = globals()[column](prices) 

def remove_outliers(prices):
    outliers = ['weight', 'reviews', 'rating', 'calc_rank', 'calc_inven', 'calc_promo', 'calc_ship']
    clean_prices = prices.copy()
    for column in outliers:
        quantile_25 = np.nanquantile(prices[column], 0.25)
        quantile_75 = np.nanquantile(prices[column], 0.75)
        low_idx = quantile_25 - 1.5 * (quantile_75 - quantile_25)
        high_idx = quantile_75 + 1.5 * (quantile_75 - quantile_25)
        ranges = [low_idx, high_idx]
        clean_prices = clean_prices[~clean_prices[column].isna()]
        clean_prices = clean_prices[~clean_prices[column].isin(ranges)]
    return clean_prices

if __name__ == "__main__":
    prices = pd.read_csv("prices.csv")
    add_clean_columns(prices)                          # add cleaned columns to the dataframe
    clean_prices = remove_outliers(prices)             # trim data 
    clean_prices.to_csv(r'clean_prices.csv', index = False, header=True)