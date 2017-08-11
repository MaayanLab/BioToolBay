import pandas as pd
import urllib2

#After runnig this script you will be left out only with tools with active homepages

all_articles_tools = pd.read_table('ALL_DATA/ALL_NEW_TOOLS/database_tools_09_17_new.txt', keep_default_na=False)
# Add new column to a dataframe for result of checking
all_articles_tools["active"]="NULL"


i=0
for i in range(len(all_articles_tools)):
    link=all_articles_tools["homepage"][i]
    try:
        r = urllib2.urlopen(link)
        if r.getcode() in (200, 401):
            print(i)
            print("works")
            all_articles_tools["active"][i]="TRUE"
        else:
            print("NOT")
    except:
        pass
    i=i+1



all_articles_tools=all_articles_tools[all_articles_tools.active != "NULL"]
all_articles_tools.to_csv("database_active_links_09_17_NEW.txt",sep='\t', encoding='utf-8')