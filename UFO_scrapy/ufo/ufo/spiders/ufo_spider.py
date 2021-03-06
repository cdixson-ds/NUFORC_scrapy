import scrapy
from datetime import datetime

"""
class ufoItem(scrapy.Item):
    city = scrapy.Field()
    state = scrapy.Field()
    shape = scrapy.Field()
    duration = scrapy.Field()
    summary = scrapy.Field()
    posted = scrapy.Field()
    #report = scrapy.Field
    pass
"""

#items = ufoItem()

class ufoSpider(scrapy.Spider):
    name = 'ufo'
    allowed_domains = ['www.nuforc.org']
    start_urls = ['http://www.nuforc.org/webreports/ndxpost.html']

    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'ufo_update.csv'
    }

    def __init__(self, start_date=None, stop_date=None, *args, **kwargs):
        self.start_date = \
            datetime.strptime(start_date, '%m/%d/%Y') \
            if start_date else None
        self.stop_date = \
            datetime.strptime(stop_date, '%m/%d/%Y') \
            if stop_date else None

        super(ufoSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        
        table_links = response.xpath('//tr/td/font/a')
        for tl in table_links:
            
           
            if not tl: continue

            link_date_selector = tl.xpath('./text()')
            
            if not link_date_selector: continue

            link_date = \
                datetime.strptime(link_date_selector.extract()[0], '%m/%d/%Y')
            
            if self.start_date and (link_date < self.start_date): continue

            if self.stop_date and (link_date >= self.stop_date): continue

            yield response.follow(tl, self.parse_date_index)

    def parse_date_index(self, response):

        #items = ufoItem()

        table_rows = response.xpath('//table/tbody/tr')
        
        for tr in table_rows:
            table_elements = tr.xpath('.//td')
            date_time_path = table_elements[0] \
                if len(table_elements) > 0 else None
            
            if not date_time_path: continue
            
            date_time = date_time_path.xpath('./font/a/text()').extract() \
                if date_time_path else None
            report_link = date_time_path.xpath('./font/a/@href').extract() \
                if date_time_path else None
            city = table_elements[1].xpath('./font/text()').extract() \
                if len(table_elements) > 1 else None
            state = table_elements[2].xpath('./font/text()').extract() \
                if len(table_elements) > 2 else None
            shape = table_elements[3].xpath('./font/text()').extract() \
                if len(table_elements) > 3 else None
            duration = table_elements[4].xpath('./font/text()').extract() \
                if len(table_elements) > 4 else None
            summary = table_elements[5].xpath('./font/text()').extract() \
                if len(table_elements) > 5 else None
            posted = table_elements[6].xpath('./font/text()').extract() \
                if len(table_elements) > 6 else None
            #report = table_elements[7].xpath('./font/text()').extract() \
                #if len(table_elements) > 7 else None
          

            yield response.follow(
                date_time_path.xpath("./font/a")[0],
                self.parse_report_table,
                meta={
                    "report_summary": {
                        "date_time": date_time[0] if date_time else None,
                        "report_link": 
                            "http://www.nuforc.org/webreports/{}".format(
                                report_link[0]) if report_link else None,
                        "city": city[0] if city else None,
                        "state": state[0] if state else None,
                        "shape": shape[0] if shape else None,
                        "duration": duration[0] if duration else None,
                        "summary": summary[0] if summary else None,
                        "posted": posted[0] if posted else None
                        #"report": report[0] if report else None
                    }
                }
            )

    def parse_report_table(self, response):

        report_table = response.xpath('//table/tbody/tr')

        report_stats = \
            " ".join(report_table[0].xpath('./td/font/text()').extract()) \
            if len(report_table) > 0 else None

        report_text = \
            " ".join(report_table[1].xpath('./td/font/text()').extract()) \
            if len(report_table) > 1 else None
        report_summary = response.meta["report_summary"]
    
        report = {
            "text": report_text,
            "stats": report_stats,
            **report_summary
        }

        yield report



#add before yeild.response
"""
  items['city'] = city
  items['state'] = state
  items['shape'] = shape
  items ['duration'] = duration
  items['summary'] = summary
  items['posted'] = posted
  items['report'] = report
    """