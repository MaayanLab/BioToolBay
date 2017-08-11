import pandas as pd
import json
import re
import string
journal_data=pd.read_json('ALL_DATA/BMC/JSON/bmc_00_17.json')
journal_data=journal_data[['title','link_to_tools','tag', 'views','citations_amount','altmetric_score', 'journal','authors','topics','abstract','date','citations_link','link','doi', 'references', 'all_links']]
doi_pattern_ref=re.compile('http://dx.doi.org/')
space_pattern=re.compile('\s\s+')
cleanr=re.compile('<.*?>')
cleann=re.compile('\n')
comma=re.compile(',')

year_pattern=re.compile('^20[0-9]{2}')


#####Check the path and name of the file. Set the name of the output file at the end.



data_length=len(journal_data)
for i in range (data_length):
    if journal_data['doi'][i]!=None:
    # ABSTRACT:
        if len(journal_data['abstract'][i])==0:
            journal_data['abstract'][i]="NULL"
        else:
            abstract_list=[]
            abstract_words=journal_data['abstract'][i]
            for word in abstract_words: 
                abstract_list.append(word.strip())
            abstract_string=' '.join(abstract_list)
            cleantext=re.sub(cleanr, " ",abstract_string)
            cleantext2=re.sub(cleann, " ", cleantext)
            abstract_str=re.sub(space_pattern, '',cleantext2)
            journal_data['abstract'][i]=abstract_str
    #TITLE:
        if len(journal_data['title'][i])==0:
            journal_data['title'][i]="NULL"
        else:
            title_list=[]
            title_words=journal_data['title'][i]
            for word in title_words: 
                title_list.append(word.strip())
            title_string=' '.join(title_list)
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
            if re.search('adsabs|academic|pdf|creativecommons', link):
                pass
            else:
                all_links_list.append(link)
        all_links_string=','.join(all_links_list)
        journal_data['all_links'][i]=all_links_string
        if len(journal_data['all_links'][i])==0:
            journal_data['all_links'][i]="NULL"
    #REFERENCES:
        reference_list=[]
        for reference in journal_data['references'][i]: 
            result=re.sub(doi_pattern_ref,'',reference)
            reference_list.append(result)
        reference_string=reference_list
        reference_string=','.join(reference_string)
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
    #Altmetric Score:   
        altmetric_string=journal_data['altmetric_score'][i]
        altmetric_string=','.join(altmetric_string)
        journal_data['altmetric_score'][i]=altmetric_string
        if len(journal_data['altmetric_score'][i])==0:
            journal_data['altmetric_score'][i]=0
    # VIEWS:
        if len(journal_data['views'][i])==0:
            journal_data['views'][i]=0 
        else:
            try:
                if journal_data['views'][i]==["not"]:
                    journal_data['views'][i]=0
                else:    
                    view_string=journal_data['views'][i]
                    view_string=','.join(view_string)
                    views=view_string.translate(string.punctuation)
                    journal_data['views'][i]=views
            except:
                journal_data['views'][i]=0
    # Citations:
        if len(journal_data['citations_amount'][i])==0:
            journal_data['citations_amount'][i]=0 
        else:
            try:
                if journal_data['citations_amount'][i]==["not"]:
                    journal_data['citations_amount'][i]=0
                else:    
                    view_string=journal_data['citations_amount'][i]
                    view_string=','.join(view_string)
                    views=view_string.translate(string.punctuation)
                    journal_data['citations_amount'][i]=views
            except:
                journal_data['citations_amount'][i]=0

    # TAG:
        if len(journal_data['tag'][i])==0:
            journal_data['tag'][i]="NULL"
        tag_string=journal_data['tag'][i]
        tag_string=','.join(tag_string)
        journal_data['tag'][i]=tag_string
        journal_data['tag'][i]=journal_data['tag'][i].upper()

    else:
        journal_data["doi"][i]="NULL"

journal_data=journal_data[journal_data.doi != "NULL"]
journal_data.to_csv("bmc_00_17_new.txt",sep='\t', encoding='utf-8')