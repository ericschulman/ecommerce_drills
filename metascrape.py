from gen_scraper import *
from wal_scraper import *
from am_scraper import *


class MetaScraper():

    def __init__(self, scrapers,size,query):
        self.scrapers = scrapers
        self.query = query
        self.size = size

    def run_scrape(self):

        for i, scraper in enumerate(self.scrapers):
            #get a list of product ids from each website
            scraper.set_query(self.query)
            prod_ids = scraper.add_ids(self.size )
            #print(prod_ids)
            #figure our their upc code
            products = []
            for prod_id in prod_ids:
                product_lookup = scraper.lookup_product(prod_id)
                if product_lookup is not None:
                    products.append(product_lookup)
                    
            #search for the code on the other websites
            other_scrapers = scrapers[:i] + scrapers[i+1:]
            for j, other_scraper in enumerate(other_scrapers):

                other_scraper_ids = []
                for product in products:
                    if product is not None:
                        print(product, other_scraper.platform, scraper.platform)
                        print(other_scraper.lookup_id(product))
                        print('<----->')


    def write_data(self):
        for scraper in self.scrapers:
            scraper.write_data()



if __name__ == '__main__':
    db = 'db/'
    scrapers = [AmazonScraper(db),WalmartScraper(db)]
    ms  = MetaScraper(scrapers,3,'drills')
    ms.run_scrape()
    ms.write_data()