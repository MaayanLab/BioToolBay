from twisted.internet import reactor, defer
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging# should learn how to use it 
import pandas as pd
import json


journal_dataset='nar_data.json'
outfile_name="nar_links.txt"


def main():
#Step 1: Extract basic info about articles from website of the journal (HERE: Nucleid Acid Research)
	process=CrawlerProcess({'USER_AGENT':"Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36", "FEED_URI" : journal_dataset, "FEED_FORMAT" : "json"})
	process.crawl(JournalSpider)
	process.start() #the script will block here until the crawling is finished
#####After the process finish running there is a json file with: type, author, title, and link to the articles in the given journal (HERE: Nucleid Acid Research)

#Step 2: Get the links to the articles and save them in a separate file (needed for next step plus might be useful for something else)
	with open(journal_dataset, "r") as f:
		data=json.load(f)
		df=pd.DataFrame(data)
		df=df[['journal', 'type','link', 'title', 'author']]
		outfile=open(outfile_name, "w+")
		for link in df["link"]:
			print(link, file=outfile)

#Step 3: use another web spider to get more specific data about each of the articles: DOT, Abstract, Total View, Citation, Relevance




#IMPORTANT : remember to set the before_year (if you are interested in all articles published in 2013 and ealier before_year=2012)
before_year=2016

class JournalSpider(scrapy.Spider):
    name="nar_spiderPRO"
    filename=name+"_visited.txt"
    file=open(filename, 'w')
    journal="Nuclei Acid Research"


    def start_requests(self):
    	yield scrapy.Request('https://academic.oup.com/nar/issue', callback=self.parse)


    def parse(self, response):
        #Find avaiable years and store them in a dictionary of lists of avaiable years and their associated links
        dict_dates={
                'years' : response.xpath('//select[@id="YearsList"]/option/text()').extract(),
                'year_links' :response.xpath('//select[@id="YearsList"]/option/@value').extract(),
                }

        i=-1#for iteration of lists inside the dictionary, it is incremented to 0 before the first use
        for year in dict_dates['years']:
            i=i+1
            if int(year) > before_year :
                next_year="https://academic.oup.com"+dict_dates['year_links'][i]
                year_data="Visited year : {} \n".format(year)
                self.file.write(year_data)
                yield scrapy.Request(next_year, callback=self.parse_the_year)

    def parse_the_issue(self, response):
        for section in response.css('.section-container section'):
            tag=section.css('h4::text').extract_first()
            for article in section.css('.al-article-items'):
                yield {
                        'type': tag,
                        'author': article.css('.al-authors-list a::text').extract(),
                        'title': article.css('h5 a *::text').extract(),
                        'link': "https://academic.oup.com"+article.css('a::attr("href")').extract_first(),
                        'journal': self.journal,
                    }

    def parse_the_year(self, response):
        issues=response.xpath('//select[@id="IssuesList"]/option/@value').extract()
        for issue in issues:
            next_issue="https://academic.oup.com"+issue
            self.file.write(next_issue+'\n')
            yield scrapy.Request(next_issue, callback=self.parse_the_issue)




if __name__== "__main__": main()












