import pandas as pd
import json
import re
import string
journal_data=pd.read_json('ALL_DATA/DATABASE/JSON/database_09_17.json')
journal_data=journal_data[['title','link_to_tools','tag', 'views','citations_amount','altmetric_score', 'journal','authors','topics','abstract','date','citations_link','link','doi', 'references', 'all_links','altmetric_link']]
doi_pattern_ref=re.compile('http://dx.doi.org/')
doi_pattern=re.compile('https://doi.org/')
#delete multiple space character
space_pattern=re.compile('\s\s+')
#remove html tags
cleanr=re.compile('<.*?>')
#remove new line characters
cleann=re.compile('\n')
#remove not needed commas
comma=re.compile(',')
#format numbers
period_float=re.compile('(\..*)')
#year
year_pattern=re.compile('^20[0-9]{2}')




data_length=len(journal_data)
for i in range (data_length):
    if journal_data['doi'][i]!=None:
    # ABSTRACT: gets rid of additional new line charachters and html tags
        if len(journal_data['abstract'][i])==0:
            journal_data['abstract'][i]="NULL"
        else:
            abstract_list=[]
            abstract_words=journal_data['abstract'][i]
            for word in abstract_words: 
                abstract_list.append(word.strip())
#You need space character between elements of list because of html code in the abstracts 
            abstract_string=' '.join(abstract_list)
            cleantext=re.sub(cleanr, " ",abstract_string)
            cleantext2=re.sub(cleann, " ", cleantext)
            abstract_str=re.sub(space_pattern, ' ',cleantext2)
            journal_data['abstract'][i]=abstract_str
    #TITLE:
        if len(journal_data['title'][i])==0:
            journal_data['title'][i]="NULL"
        else:
            title_list=[]
            title_words=journal_data['title'][i]
            for word in title_words: 
                title_list.append(word.strip())
            title_string=''.join(title_list)
            journal_data['title'][i]=title_string
    #Authors
        if len(journal_data['authors'][i])==0:
            journal_data['authors'][i]="NULL"
        else:
            authors_list=[]
            authors_words=journal_data['authors'][i]
            for author in authors_words: 
                authors_list.append(author.strip())
            authors_string=', '.join(authors_list)
            journal_data['authors'][i]=authors_string
    #LINK TO TOOL
        tool_string=journal_data['link_to_tools'][i]
        tool_string=','.join(tool_string)
        journal_data['link_to_tools'][i]=tool_string
        if len(journal_data['link_to_tools'][i])==0:
            journal_data['link_to_tools'][i]="NULL"
    #TOPICS:
        if len(journal_data['topics'][i])==0:
            journal_data['topics'][i]="NULL"
        else:
            topics_list=[]
            topics=journal_data['topics'][i]
            for topic in topics: 
                topics_list.append(topic.strip())
            topic_string=','.join(topics_list)
            journal_data['topics'][i]=topic_string
    #ALL LINKS:
        all_links_list=[]
        all_links=journal_data['all_links'][i]
        for link in all_links:
            if re.search('adsabs|academic|harvard', link):
                pass
            else:
                all_links_list.append(link)
        all_links_string=','.join(all_links_list)
        journal_data['all_links'][i]=all_links_string
        if len(journal_data['all_links'][i])==0:
            journal_data['all_links'][i]="NULL"
    #REFERENCES:
        reference_list=[]
        reference_list=journal_data['references'][i] 
        reference_string=','.join(reference_list)
        journal_data['references'][i]=reference_string
        if len(journal_data['references'][i])==0:
            journal_data['references'][i]="NULL"
    # DATE:
        try:
            date_to_string=journal_data['date'][i]
            date_to_string='{:%Y-%m-%d}'.format(date_to_string)
            journal_data['date'][i]=date_to_string
        except:
            journal_data['date'][i]="NULL"
    #Almetric Score:
        try:
            altmetric_string=journal_data['altmetric_score'][i]
            if altmetric_string is None:
                journal_data['altmetric_score'][i]=0
            else:
                altmetric_score=journal_data['altmetric_score'][i]
                altmetric_score=[int(s) for s in altmetric_score.split() if s.isdigit()]
                journal_data['altmetric_score'][i]=altmetric_score[0]
        except TypeError:
            journal_data['altmetric_score'][i]=0

    # VIEWS:
        try:
            view_string=journal_data['views'][i]
            if view_string is None:
                journal_data['views'][i]=0
            else:
                view_string2=str(view_string)
                views=re.sub(comma, "",view_string2)
                journal_data['views'][i]=views
        except:
            journal_data['views'][i]=0
    # Citations:
        try:
            citations_string=journal_data['citations_amount'][i]
            if not citations_string:
                journal_data['citations_amount'][i]=0
            else:
                citations_string2=str(citations_string)
                citations=re.sub(period_float, "",citations_string2)
                citations=int(citations)
                journal_data['citations_amount'][i]=citations
        except:
            journal_data['citations_amount'][i]=0

    # TAG:
        if journal_data['tag'][i]!=None: 
            tag_string=journal_data['tag'][i]
            if len(journal_data['tag'][i])==0:
                journal_data['tag'][i]="NULL"
            journal_data['tag'][i]=journal_data['tag'][i].upper()
        else:
            journal_data['tag'][i]="NULL"
    #DOI
        try:
            result=re.sub(doi_pattern,'', journal_data["doi"][i])
            journal_data["doi"][i]=result
        except:
            journal_data["doi"][i]="NULL"
    #altmetric link
        if journal_data['altmetric_link'][i]!=None:
            pass
        else:
            journal_data['altmetric_link'][i]="NULL"


    else:
        journal_data["doi"][i]="NULL"



# MAKE SURE VIEWS, CITATIONS AND ALTMETRIC SCORE ARE NP INTS

journal_data=journal_data[journal_data.doi != "NULL"]
journal_data.to_csv("database_09_17_new.txt",sep='\t', encoding='utf-8')