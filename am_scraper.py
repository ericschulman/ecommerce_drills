from gen_scraper import *
import selenium

class AmazonScraper(GenericScraper):
        
    def __init__(self, *args, **kwargs):
        kwargs['url'] = 'https://www.amazon.com/'
        kwargs['platform'] ='AMZN'
        super(AmazonScraper, self).__init__(*args, **kwargs)
        
        

    def search_url(self, keywords, page,  sort='salesrank'):
        final_query = self.format_query(keywords)
        url =  self.base_url + 's?k=%s&s=%s&page=%s'%(final_query,sort,page)
        return url

    def prod_url(self, prod_id):
        return  self.base_url + 'dp/'+prod_id

    def set_location(self,driver,retry=10):
        #self.driver.set_window_size(550, 692)
        if driver.page_source.find(self.location) > 0:
                print('sweet victory')
                return
        try:
            driver.get(self.base_url)
            element = driver.find_element(By.CSS_SELECTOR, ".nav-logo-link > .nav-logo-base")
            actions = ActionChains(driver)
            actions.move_to_element(element).perform()
            driver.find_element(By.ID, "glow-ingress-line1").click()
            driver.find_element(By.ID, "GLUXZipUpdateInput").click()
            driver.find_element(By.ID, "GLUXZipUpdateInput").send_keys(self.location)
            driver.find_element(By.CSS_SELECTOR, "#GLUXZipUpdate .a-button-input").click()
            driver.find_element(By.ID, "a-autoid-3-announce").click()
            print(driver.page_source.find(self.location) > 0)
        except Exception as e:
            print(e)
            self.set_location(driver,retry=retry-1)




    def add_ids(self, num_ids, lookup = False, keywords= None, retry0=3, search_rank0=1, page0=1, asin_list0=[]):
        asin_list = asin_list0[:]
        page = page0
        search_rank = search_rank0
        retry = retry0

        if keywords is None:
            keywords = [self.query]

        max_page = 2 if lookup else 10
        while page < max_page and search_rank <= num_ids:
            url = self.search_url(keywords, page, sort='') if lookup else self.search_url(keywords, page)
            
            rawtext = self.get_page(url)
            tree = html.fromstring(rawtext)
            search_box = tree.xpath("//*[@class='s-result-list s-search-results sg-row']") 
            
            if len(search_box) <= 0: #no results
                if retry >0:
                    return self.add_ids(num_ids, lookup = lookup, keywords= keywords, retry0=retry-1,search_rank0=search_rank, page0=page, asin_list0=asin_list)
                else:
                    return asin_list

            search_results = search_box[0]

            imgs = search_results.xpath("//img[@class='s-image']")
            index = 0
            while index < len(search_results) and  search_rank <= num_ids:
                if ('class' in dict(search_results[index].attrib).keys() 
                        and 'data-asin' in dict(search_results[index].attrib).keys()):
                    
                    found_product = not lookup

                    asin = search_results[index].attrib['data-asin']

                    if len(asin) != 10:

                        result_text = str(etree.tostring(search_results[index])) #more reliable way to get ASIN
                        result_text = result_text[result_text.find('dp/')+3:]
                        result_text = result_text[:result_text.find('/')]
                        asin = result_text

                    if len(asin) != 10: #ASINs are 10 charcters?
                        index = index+1
                        continue

                    is_ad =  int('AdHolder' in search_results[index].attrib['class'])

                    #if we are looking up, see if it's the right product
                    if not is_ad and not found_product:
                        in_name = False
                        title = str(etree.tostring(imgs[index]))

                        manuf,model = keywords[0], keywords[0]
                        if len(keywords) >1:
                            manuf,model= keywords[0],keywords[1]

                        in_name = model is not None and title.find(model) >= 0 # and title.find(manuf) >= 0
                        if in_name:
                            #how is the one relevant result not here???
                            found_product = True #skip and increment search rank
                        if not in_name:
                            search_rank = search_rank +1
                        
                    #general case when not looking up a product
                    if found_product:
                        if asin not in self.data.keys():
                            self.create_id(asin)
                            self.data[asin]['query'] = url
                            self.data[asin]['rank'] = 0 if (lookup or is_ad) else search_rank
                            self.data[asin]['ads'] = 1 if is_ad else 0
                            self.data[asin]['page'] = page

                        incr = 0 if is_ad else 1
                        search_rank = search_rank + incr
                        asin_list.append(asin)


                index = index +1
                
            page = page +1
        return asin_list


    def amazon_table(self, tree,key):
        table =  tree.xpath("//*[@id='%s']"%key)
        if table == []:
            return None
        table = table[0]
        table = pd.read_html(etree.tostring(table , encoding='utf8', method='html'))[0]
        table = table.applymap(lambda s: s.replace('\\n','').replace('\\t','').replace('  ', '')) #clean things up
        table = table.set_index(0)
        return table
    

    def get_num_sellers(self, tree):
        listings = self.search_xpath(tree,"New & Used")
        if listings !=[]:
            listings = str(etree.tostring(listings[0]))
            ind1, ind2 = listings.find('('),listings.find(')')
            return int(listings[ind1+1:ind2])
        return None

    def get_price(self,tree):
        price = tree.xpath("//*[@id='base-product-price']")
        if price != []:
           return float(price[0].attrib['data-base-product-price'][1:])
        if price == []:
            price = tree.xpath("//*[@id='priceblock_ourprice']")
            if price != []:
                return float(price[0].text[1:])
        if price == []:    
            price = tree.xpath("//*[@id='priceblock_saleprice']")
            if price != []:
                return float(price[0].text[1:])
        return None
        

    def get_data(self, asin, retry=3):

        url =  self.prod_url(asin)
        rawtext = self.get_page(url)
        tree = html.fromstring(rawtext)

        ####### most important info first


        #manufactuer
        manuf = tree.xpath("//*[@id='bylineInfo']")
        if manuf != []:
            self.data[asin]['manufacturer'] = manuf[0].text
        
        #model number
        table1 =  self.amazon_table(tree,'productDetails_techSpec_section_1')
        if  table1 is not None and ' Part Number' in list(table1.index):
            model = table1.loc[' Part Number'][1]
            self.data[asin]['model'] = model[1:]
            
        elif table1 is not None and ' Item model number' in list(table1.index):
            model = table1.loc[' Item model number'][1]
            self.data[asin]['model'] = model[1:]


        #'product':None,
        product = tree.xpath("//*[@id='productTitle']")
        if product !=[]:
            product = product[0].text
            product = product.replace('\\n','').replace('  ', '')
            self.data[asin]['product'] = product
        
        #sale price
        list_price = tree.xpath("//*[@class='priceBlockStrikePriceString a-text-strike']")
        if list_price != []:
            self.data[asin]['list_price'] = float(list_price[0].text[2:])
            
        #price
        self.data[asin]['price'] = self.get_price(tree)
        
        #'in_stock' 
        stock = tree.xpath("//*[@id='availability']")
        if stock != []:
            stock = str(etree.tostring(stock[0]))
            self.data[asin]['in_stock']= int(stock.find('In Stock.') >= 0 )
      
        #'seller' 
        seller = tree.xpath("//*[@id='comparison_sold_by_row']")
        if seller != []:
            self.data[asin]['seller'] = seller[0][1][0].text
        
        #'listings'
        self.data[asin]['quantity1']= self.get_num_sellers(tree)

        #rank in page


        #only x left in stock


        #shipping description


        #shipping cost
    

        #'arrives'
        arrives =  self.search_xpath(tree,'Two-Day Shipping')
        if arrives != []:
            date = datetime.datetime.now() + datetime.timedelta(days=1)
            self.data[asin]['arrives'] = self.to_epoch_time(date)
        
        #'rating'
        ratings = tree.xpath("//*[@id='acrPopover']")
        if ratings !=[]:
            self.data[asin]['rating'] = float(ratings[0].attrib['title'][:3])
        
        #'reviews'
        reviews = tree.xpath("//*[@id='acrCustomerReviewText']")
        if reviews !=[]:
            reviews = reviews[0].text
            reviews = reviews[:reviews.find(' ')]
            reviews = reviews.replace(',','')
            self.data[asin]['reviews'] = int(reviews)
                
        #'weight'
        table2 = self.amazon_table(tree,'productDetails_detailBullets_sections1')
        if table2 is not None and ' Shipping Weight' in list(table2.index):
            weight = table2.loc[' Shipping Weight'][1][1:]
            weight = weight[:weight.find(' ')]
            self.data[asin]['weight'] = float(weight)

        if table2 is not None and ' Best Sellers Rank' in list(table2.index):
            rank = table2.loc[' Best Sellers Rank'].loc[1]
            rank = rank[rank.find('#'):]
            rank = rank[1:rank.find(' ')]
            rank = int(rank.replace(',',''))
            self.data[asin]['quantity2'] = rank
            
        #'max_qty'
        dropdowns = tree.xpath("//*[@class='a-dropdown-container']")
        if dropdowns != []:
            for drop in dropdowns:
                if 'for' in drop[0].attrib and drop[0].attrib['for'] == 'quantity':
                    self.data[asin]['max_qty'] = len(drop[1])
        
        return self.data[asin]


    def lookup_upc(self, prod_id):

        data = self.data[prod_id]
        brand = data['manufacturer']
        item  = data['model']
        #TODO: write data that i'm getting outside of this...
        #TODO: make this part of the generic class
        url = 'https://www.upcitemdb.com/upc/%s %s'%(brand,item)
        url = url.replace(' ', '%20')
        rawtext = self.get_page(url)
        tree = html.fromstring(rawtext)
        link_cand = tree.xpath("//*[@class='rImage']")
        #TODO: go for top 3 items instead
        if len(link_cand)  == 0 :
            return None
        self.data[prod_id]['upc'] = link_cand[0][0].text
        return link_cand[0][0].text



    def lookup_id_upc(self, upc):
        #TODO: save some of this data since i have it
        #TODO: make an extra query to amazon using the product names?
        url = 'https://www.upcitemdb.com/upc/' + upc
        rawtext = self.get_page(url)
        tree = html.fromstring(rawtext)
        table = tree.xpath("//*[@class='detail-list']")
        if len(table) == 0:
            return None
        table = table[0]
        table = pd.read_html(etree.tostring(table, encoding='utf8', method='html'))[0]
        table = table.set_index(0)
        if  'Amazon ASIN:' in (table.index):
            asin = table.loc['Amazon ASIN:'][1]
            self.create_id(asin)
            self.data[asin]['upc'] = upc
            return asin
        return None


if __name__ == '__main__':

    scrap = AmazonScraper('db/')
    #print(scrap.lookup_id(('BLACK+DECKER','LDX220C')))
    #print(scrap.lookup_id(('BLACK+DECKER','BCD702C2BWM')))
    #print(scrap.lookup_id(('Hyper Tough','AQ75023G')))
    #print(scrap.lookup_id(('Hyper Tough','AQ75023G')))
    #print(scrap.lookup_id(('Hyper Tough','AQ75023G')))
    print( len(scrap.add_ids(10) ) )
    scrap.end_scrape()
    #print(len(scrap.data))
    scrap.write_data()
    #scrap.write_data()
