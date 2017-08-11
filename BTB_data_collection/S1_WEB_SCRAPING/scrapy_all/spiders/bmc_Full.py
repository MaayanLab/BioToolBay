import scrapy
import re

#IMPORTANT CHOOSE HOW MANY PAGES BACK YOU WANT TO GO WHOLE JOURNAL IS 334 pages (25 articles per page) as of June 2017

class JournalSpider(scrapy.Spider):
    name="bmc_spiderF"
    journal="BMC Bioinformatics"
    start_urls = [
        'https://bmcbioinformatics.biomedcentral.com/articles?searchType=journalSearch&sort=PubDate&page=1',
    ]

 


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse, meta={'splash' : {'endpoint' : 'render.html', 'args' : { 'wait' : 8.5 }}})

    def parse(self, response):
        for article in response.css('article'):
            for link in article.css('.fulltexttitle::attr("href")').extract():
                next_article="https://bmcbioinformatics.biomedcentral.com"+ link
                yield scrapy.Request(next_article, self.parse_the_article,meta={'splash' : {'endpoint' : 'render.html', 'args' : { 'wait' : 8.5 }}})
        next_page=response.css('a[class="Pager Pager--next"]::attr(href)').extract_first()
        if next_page is not None:
            next_page="https://bmcbioinformatics.biomedcentral.com"+next_page
            yield scrapy.Request(next_page, callback=self.parse, meta={'splash' : {'endpoint' : 'render.html', 'args' : { 'wait' : 3.5 }}})



    def parse_the_article(self, response):
        article_abstract=response.css('.Abstract')
        article_whole=response.css('.ExternalRef')
        side_box=response.css('.SideBox')
        all_links_list=[]
        all_links=article_whole.css('a[href*="http"]::attr("href")').extract()
        list_of_links=[]
        for link in all_links:
            if len(link) < 80:
                if re.search('doi|pubmed|scholar|new-image|creativecommons', link):
                    pass
                else:
                    all_links_list.append(link)
        text_full=response.css('.FulltextWrapper ::text')

        yield {
            'link': response.url,#works
            'doi' : response.css('.ArticleDOI ::text').extract()[1],#works
            'abstract' : response.css('.Abstract p *::text').extract(),#works
            'altmetric_score': side_box.css('.list-stacked__item p::text').re('Altmetric Attention Score:\s+(\w+)'),#works
            'citations_link': side_box.css('.list-stacked__item a::attr("href")').extract_first(),#works
            'views':side_box.css('.list-stacked__item ::text').re('Article accesses:\s+(\w+)'),#works
            'citations_amount':side_box.css('.list-stacked__item ::text').re('Citations:\s+(\w+)'),#works 
            'title': response.css('.ArticleTitle ::text').extract(),#works
            'journal':  self.journal,#works
            'authors': response.css('.AuthorName ::text').extract(),#works
            'tag': response.css('.ArticleCategory::text').extract(),#works
            'topics': response.css('.Keyword::text').extract(),#works
            'link_to_tools': article_abstract.css('a[href*="http"]::attr("href")').extract(),#works
            'all_links': article_whole.css('a[href*="http"]::attr("href")').extract(),
            'references':response.css('.OccurrenceDOI a::attr("href")').extract(),
            'date':response.css('.HistoryOnlineDate ::text').extract()[1],
        }