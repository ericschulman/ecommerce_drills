# Background

This repository analyzes scraped data about Amazon, Home Depot, Lowe's, and Walmart's price competition in digital markets. The data involves power drills. 

For more background information on this market see the following articles:
* [article 1](https://www.emarketer.com/content/digital-investments-pay-off-for-walmart-in-ecommerce-race)
* [article 2](https://techcrunch.com/2018/07/13/amazons-share-of-the-us-e-commerce-market-is-now-49-or-5-of-all-retail-spend/)
* [article 3](https://www.emarketer.com/Chart/Top-10-US-Companies-Ranked-by-Retail-Ecommerce-Sales-Share-2018-of-US-retail-ecommerce-sales/220521)
* [article 4](https://www.statista.com/statistics/276846/reach-of-top-online-retail-categories-worldwide/)


# Data

The main datasets file is `prices.csv` located in the `data` folder. There is also `entry.csv` which has brick and mortar locations for Lowe's and Home Depot. For more information on the entry dataset see [this kaggle page](https://www.kaggle.com/datasets/erichschulman/home-improvement-stores). The `.sql` files in this folder can be used when `prices.csv` is loaded into a `sql` database. The `ipython` notebooks in this repository correspond to the dataset that they use. For example, the notebooks that start with `price` use the `prices.csv` dataset. The ones that start with `entry` use the `entry.csv` dataset.

## Variable definitions for data 

### Raw data from the scraper.

The raw scraped data in in `prices.csv`. Because my data comes directly from the retailers It is possible to differentiate when the manufacturer or the retailer orders the price cut. I collected the following information using the scraper: 

* prices, whether or not there was a sale (trade promotion)
* shipping prices, shipping times, delivery methods
* its rank in the search results (sorted by best seller). Also information about ads.  Ads 1 means that it was sponsered, 0 means it wasn't promoted
* inventory - There are up to 3 flexible columns that are used to record information available about quantity on the website. These variables have different meanings across the various retailers.
	1. Amazon
	* quantity 1 - number of sellers
	* quantity 2 - rank in amazon department
	* quantity 3 - limited stock (number left)
	2. Walmart
	* quantity 1- quantity in store
	* quantity 2 - should have a special offer
	* quantity 3 - urgent quantity
	3. Home Depot
	* quantity 1 - in store stock 
	* quantity 2 - limited quantity (number left)
	4. Lowe's
	* quantity 1 - stock in store
	* quantity 2 - price below retail (so, number is not shared)
* store locations.
* whether or not the product is in stock.
* The date variable is in epoch time. This is the date that the page was visited and the data was scraped.
* the actual weight of the product as a proxy for size.

## Cleaned data
The main file for preprocessing is `clean_prices.py`. This creates more consistent `inventory` information for each of the sellers.
* `calc_rank` makes rank more interpretable.
* `calc_inven` tries to make inventory comparable accross sellers.
* `calc_ship` tries to convert shipping information into a price and date.


## Panel data

Within `clean_prices.py`, the function `create_panel` tries to create a balanced panel with the observations. The units of the panel are week, and the product sold on a specific platform. The main variables in the panel are:

`['weight', 'reviews', 'rating', 'calc_rank', 'calc_inven', 'calc_promo', 'calc_ship']`





