import scrapy
import re
#IMPORTANT : remember to set the before_year (if you are interested in all articles published in 2013 and ealier before_year=2012)

before_year=2016


class JournalSpider(scrapy.Spider):
    name="bio_spiderS"
    journal="Bioinformatics Oxford"
    start_urls = [

        'https://academic.oup.com/bioinformatics/article/28/1/69/220214/Gene-Ontology-driven-inference-of-protein-protein',
        'https://academic.oup.com/bioinformatics/article/33/12/1765/2971441/pETM-a-penalized-Exponential-Tilt-Model-for',
        'https://academic.oup.com/bioinformatics/article/28/17/2231/245421/BAIUCAS-a-novel-BLAST-based-algorithm-for-the',
        'https://academic.oup.com/bioinformatics/article/24/1/34/205610/Estimation-of-an-in-vivo-fitness-landscape'
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse, meta={'splash' : {'endpoint' : 'render.html', 'args' : { 'wait' : 3.5 }}})


    def parse(self, response):
        article_abstract=response.css('.abstract')
        article_whole=response.css('.widget-items')
        all_links_list=[]
        all_links=article_whole.css('a[href*="http"]::attr("href")').extract()
        images=response.css('img[alt*="Article has"]::attr(alt)').extract_first()
        link_altmetric=response.css('img[alt*="Article has"]::attr(src)').extract_first()
        references_class=response.css('.ref-list')
        for link in all_links:
            if len(link) < 60:
                if re.search('doi|pubmed|scholar', link):
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