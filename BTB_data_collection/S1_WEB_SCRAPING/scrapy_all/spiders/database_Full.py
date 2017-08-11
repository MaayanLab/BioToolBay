import scrapy
import re


#IMPORTANT : remember to set the before_year (if you are interested in all articles published in 2013 and ealier before_year=2012)


class JournalSpider(scrapy.Spider):
    name="database_spiderF"
    start_urls = [
        'https://academic.oup.com/database/issue/volume/2009',
        'https://academic.oup.com/database/issue/volume/2010',
        'https://academic.oup.com/database/issue/volume/2011',
        'https://academic.oup.com/database/issue/volume/2012',
        'https://academic.oup.com/database/issue/volume/2013',
        'https://academic.oup.com/database/issue/volume/2014',
        'https://academic.oup.com/database/issue/volume/2015',
        'https://academic.oup.com/database/issue/volume/2016',
        'https://academic.oup.com/database/issue/volume/2017'
    ]


    journal="Database Oxford"

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse_the_issue, meta={'splash' : {'endpoint' : 'render.html', 'args' : { 'wait' : 5.5 }}})


    def parse_the_issue(self, response):
        for section in response.css('.section-container section'):
            for article in section.css('.al-article-items'):
                next_article="https://academic.oup.com"+article.css('a::attr("href")').extract_first()
                yield scrapy.Request(next_article, callback=self.parse_the_article, meta={'splash' : {'endpoint' : 'render.html', 'args' : { 'wait' : 3.5 }}})
   

    def parse_the_article(self,response):
        article_abstract=response.css('.abstract')
        article_whole=response.css('.widget-items')
        all_links_list=[]
        all_links=article_whole.css('a[href*="http"]::attr("href")').extract()
        images=response.css('img[alt*="Article has"]::attr(alt)').extract_first()
        link_altmetric=response.css('img[alt*="Article has"]::attr(src)').extract_first()
        references_class=response.css('.ref-list')
        for link in all_links:
            if len(link) < 80:
                if re.search('doi|pubmed|scholar|new-image|creativecommons|harvard', link):
                    pass
                else:
                    all_links_list.append(link)


        yield {
            'altmetric_score' :images,
            'altmetric_link': link_altmetric,
            'link': response.url,
            'doi' : response.css('.citation-doi a::attr(href)').extract_first(),
            'abstract' : response.css('.abstract ::text').extract(),
            'citations_link': response.css('.relatedArticleIn-content a::attr("href")').extract_first(),
            'views': response.css('.artmet-number::text').extract_first(),
            'citations_amount': response.css('.artmet-citations .artmet-number a::text').extract_first(),#works 
            'title': response.css('.widget-items h1 *::text').extract(),
            'journal':  self.journal,
            'authors': response.css('.linked-name ::text').extract(),
            'tag': response.css('.article-metadata-tocSections a::text').extract_first(),
            'topics': response.css('.related-topic-tag-list span::text').extract(),
            'link_to_tools': article_abstract.css('a[href*="http"]::attr("href")').extract(),
            'all_links': all_links_list,
            'references': [x.split('/')[-1] for x in references_class.css('.link-pub-id::attr(href)').extract()],
            'date':response.css('.citation-date ::text').extract_first(),
        }

    def parse_the_year(self, response):
        issues=response.xpath('//select[@id="IssuesList"]/option/@value').extract()
        for issue in issues:
            next_issue="https://academic.oup.com"+issue
            yield scrapy.Request(next_issue, callback=self.parse_the_issue, meta={'splash' : {'endpoint' : 'render.html', 'args' : { 'wait' : 5.5 }}})