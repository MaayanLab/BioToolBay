import json, os
import pandas as pd
from flask import Flask, render_template, flash, request, url_for, redirect
#from content_management import Content
from flask_sqlalchemy import SQLAlchemy


from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


#ARTICLES_INFO=Content()

static_url_path = '/biotoolbay/Website/static' if os.path.exists('/biotoolbay/Website/static') else 'static'
#app = Flask(__name__, static_url_path=static_url_path)
app = Flask(__name__, static_folder=static_url_path)


#server
# Read data
connection_file = 'db_connection.json'
if os.path.exists(connection_file):
	with open(connection_file) as openfile:
		connectionDict = json.loads(openfile.read())
	os.environ['DB_USER'] = connectionDict['DB_USER']
	os.environ['DB_PASS'] = connectionDict['DB_PASS']
	os.environ['DB_HOST'] = connectionDict['DB_HOST']
	os.environ['DB_NAME'] = connectionDict['DB_NAME']


# Initialize database
uriString = 'mysql://' + os.environ['DB_USER'] + ':' + os.environ['DB_PASS'] + '@' + os.environ['DB_HOST'] + '/' + os.environ['DB_NAME']+'?charset=utf8'
app.config['SQLALCHEMY_DATABASE_URI'] = uriString
app.config['SQLALCHEMY_POOL_RECYCLE'] = 290
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
engine = SQLAlchemy(app).engine








entry_point = '/biotoolbay'

@app.route(entry_point, methods=["GET", "POST"])
def homepage():
	error=None
	try:
		if request.method=="POST":

			attempted_word = request.form["word_for_search"]
			if len(attempted_word) < 2 :
				error="Your query has to have at least 2 characters"
				return render_template("index.html", error=error, entry_point=entry_point)

			query1 = "SELECT * FROM articles LEFT JOIN tools ON tools.article_fk=articles.id LEFT JOIN metrics ON metrics.id= articles.id WHERE (LCASE(abstract) LIKE %(this_name)s OR LCASE(topics) LIKE %(this_name)s OR LCASE(authors) LIKE %(this_name)s) AND main=1 ORDER BY citations DESC"
			search_results = pd.read_sql(query1,con=engine, params={'this_name': '%'+ attempted_word +'%'})
			if len(search_results) == 0 :
				error="Whoops, the tool you are searching for is not in our database."
				return render_template("index.html", error=error, entry_point=entry_point)
			elif len(search_results)== 1:
				tool_name=search_results.name_tool.tolist()[0]
				return redirect(url_for('tool', chosen_tool=tool_name))
			else:
				return redirect(url_for('results', chosen_tool=attempted_word))
	except:
		return render_template("index.html")
	return render_template("index.html", entry_point=entry_point)




@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html", entry_point=entry_point)




@app.route(entry_point+'/tool/<chosen_tool>', methods=["GET", "POST"])
def tool(chosen_tool):
	

	tool_id=pd.read_sql_query("SELECT id FROM tools WHERE LCASE(name_tool) ='" +chosen_tool+"'", engine).id.tolist()
	if(len(tool_id)==0):
		return render_template("404.html")
	else:
		tool_main_info=pd.read_sql_query("SELECT * FROM tools LEFT JOIN articles ON tools.article_fk=articles.id LEFT JOIN journals ON articles.journal_fk= journals.id LEFT JOIN metrics ON metrics.id= articles.id LEFT JOIN altmetrics ON altmetrics.score= metrics.altmetric_fk WHERE LCASE(name_tool) ='" +chosen_tool+"'", engine)
		
		tool_main_name=tool_main_info.name_tool.tolist()[0]
		tool_main_abstract=tool_main_info.abstract.tolist()[0]
		tool_main_authors=tool_main_info.authors.tolist()[0]
		tool_main_title=tool_main_info.title.tolist()[0]
		tool_main_homepage=tool_main_info.homepage.tolist()[0]
		tool_main_date=tool_main_info.date.tolist()[0]
		tool_main_doi=tool_main_info.doi.tolist()[0]
		tool_main_link=tool_main_info.link.tolist()[0]
		tool_main_views=tool_main_info.views.tolist()[0]
		tool_main_citations=tool_main_info.citations.tolist()[0]
		tool_main_altmetric=tool_main_info.badge_link.tolist()[0]
		tool_main_journal=tool_main_info.name.tolist()[0]

		tool_id=str(tool_id[0])
		query_1="SELECT * FROM related_articles LEFT JOIN articles ON related_articles.related_article_fk=articles.id WHERE tool_id = {tool_id}".format(**locals())
		related_publications=pd.read_sql_query(query_1, engine)

		# get the similar tools to the chosen tool
		query_2 = "SELECT * FROM similar_tools LEFT JOIN tools ON similar_tools.similar_tool_fk = tools.id LEFT JOIN articles ON articles.id=tools.article_fk LEFT JOIN metrics ON metrics.id= articles.id WHERE main_tool = {tool_id} ORDER BY views DESC".format(**locals())
		similar_tools=pd.read_sql_query(query_2, engine)
		
		# get the keywords associated with the tool
		query_3="SELECT * FROM tagmap LEFT JOIN keywords ON tagmap.tag_fk = keywords.id  WHERE tool_fk = {tool_id}".format(**locals())
		words = pd.read_sql(query_3,con=engine).keyword.tolist()
	

#It is possible to do the tools landing pages with only one template and an "if" statement
#I am passing all the parameters about tools only because I want to decide specify exactly the order of tools on the recommendation caurosel.
		if len(related_publications) == 0:
			return render_template("tool_0.html",entry_point=entry_point,keywords=words,tool_main_name=tool_main_name,tool_main_abstract=tool_main_abstract, tool_main_authors=tool_main_authors,
			tool_main_title=tool_main_title, tool_main_homepage=tool_main_homepage,tool_main_date=tool_main_date,tool_main_doi=tool_main_doi, tool_main_link=tool_main_link, tool_main_views=tool_main_views,
			tool_main_citations=tool_main_citations,tool_main_altmetric=tool_main_altmetric,tool_main_journal=tool_main_journal,
			 similar_tool_1_name=similar_tools["name_tool"][0],similar_tool_1_title=similar_tools["title"][0], similar_tool_1_views=similar_tools["views"][0], similar_tool_1_citations=similar_tools["citations"][0], similar_tool_1_similarity=similar_tools["similarity"][0],
			 similar_tool_2_name=similar_tools["name_tool"][1],similar_tool_2_title=similar_tools["title"][1], similar_tool_2_views=similar_tools["views"][1], similar_tool_2_citations=similar_tools["citations"][1], similar_tool_2_similarity=similar_tools["similarity"][1],
			 similar_tool_3_name=similar_tools["name_tool"][2],similar_tool_3_title=similar_tools["title"][2], similar_tool_3_views=similar_tools["views"][2], similar_tool_3_citations=similar_tools["citations"][2], similar_tool_3_similarity=similar_tools["similarity"][2],
			 similar_tool_4_name=similar_tools["name_tool"][3],similar_tool_4_title=similar_tools["title"][3], similar_tool_4_views=similar_tools["views"][3], similar_tool_4_citations=similar_tools["citations"][3], similar_tool_4_similarity=similar_tools["similarity"][3],
			 similar_tool_5_name=similar_tools["name_tool"][4],similar_tool_5_title=similar_tools["title"][4], similar_tool_5_views=similar_tools["views"][4], similar_tool_5_citations=similar_tools["citations"][4], similar_tool_5_similarity=similar_tools["similarity"][4], 
			 similar_tool_6_name=similar_tools["name_tool"][5],similar_tool_6_title=similar_tools["title"][5], similar_tool_6_views=similar_tools["views"][5], similar_tool_6_citations=similar_tools["citations"][5], similar_tool_6_similarity=similar_tools["similarity"][5],
			 similar_tool_7_name=similar_tools["name_tool"][6],similar_tool_7_title=similar_tools["title"][6], similar_tool_7_views=similar_tools["views"][6], similar_tool_7_citations=similar_tools["citations"][6], similar_tool_7_similarity=similar_tools["similarity"][6],
			 similar_tool_8_name=similar_tools["name_tool"][7],similar_tool_8_title=similar_tools["title"][7], similar_tool_8_views=similar_tools["views"][7], similar_tool_8_citations=similar_tools["citations"][7], similar_tool_8_similarity=similar_tools["similarity"][7],
			 similar_tool_9_name=similar_tools["name_tool"][8],similar_tool_9_title=similar_tools["title"][8], similar_tool_9_views=similar_tools["views"][8], similar_tool_9_citations=similar_tools["citations"][8], similar_tool_9_similarity=similar_tools["similarity"][8])

		elif len(related_publications) == 1:
			related_publications_title=related_publications.title.tolist()[0]
			related_publications_abstract=related_publications.abstract.tolist()[0]
			related_publications_link=related_publications.link.tolist()[0]
			return render_template("tool_1article.html",entry_point=entry_point,keywords=words,tool_main_name=tool_main_name,tool_main_abstract=tool_main_abstract, tool_main_authors=tool_main_authors,
				tool_main_title=tool_main_title, tool_main_homepage=tool_main_homepage,tool_main_date=tool_main_date,tool_main_doi=tool_main_doi, tool_main_link=tool_main_link, tool_main_views=tool_main_views,
				tool_main_citations=tool_main_citations,tool_main_altmetric=tool_main_altmetric,tool_main_journal=tool_main_journal,related_publications_title=related_publications_title,related_publications_abstract=related_publications_abstract,related_publications_link=related_publications_link,
				similar_tool_1_name=similar_tools["name_tool"][0],similar_tool_1_title=similar_tools["title"][0], similar_tool_1_views=similar_tools["views"][0], similar_tool_1_citations=similar_tools["citations"][0], similar_tool_1_similarity=similar_tools["similarity"][0],
				similar_tool_2_name=similar_tools["name_tool"][1],similar_tool_2_title=similar_tools["title"][1], similar_tool_2_views=similar_tools["views"][1], similar_tool_2_citations=similar_tools["citations"][1], similar_tool_2_similarity=similar_tools["similarity"][1],
				similar_tool_3_name=similar_tools["name_tool"][2],similar_tool_3_title=similar_tools["title"][2], similar_tool_3_views=similar_tools["views"][2], similar_tool_3_citations=similar_tools["citations"][2], similar_tool_3_similarity=similar_tools["similarity"][2],
				similar_tool_4_name=similar_tools["name_tool"][3],similar_tool_4_title=similar_tools["title"][3], similar_tool_4_views=similar_tools["views"][3], similar_tool_4_citations=similar_tools["citations"][3], similar_tool_4_similarity=similar_tools["similarity"][3],
				similar_tool_5_name=similar_tools["name_tool"][4],similar_tool_5_title=similar_tools["title"][4], similar_tool_5_views=similar_tools["views"][4], similar_tool_5_citations=similar_tools["citations"][4], similar_tool_5_similarity=similar_tools["similarity"][4], 
				similar_tool_6_name=similar_tools["name_tool"][5],similar_tool_6_title=similar_tools["title"][5], similar_tool_6_views=similar_tools["views"][5], similar_tool_6_citations=similar_tools["citations"][5], similar_tool_6_similarity=similar_tools["similarity"][5],
				similar_tool_7_name=similar_tools["name_tool"][6],similar_tool_7_title=similar_tools["title"][6], similar_tool_7_views=similar_tools["views"][6], similar_tool_7_citations=similar_tools["citations"][6], similar_tool_7_similarity=similar_tools["similarity"][6],
				similar_tool_8_name=similar_tools["name_tool"][7],similar_tool_8_title=similar_tools["title"][7], similar_tool_8_views=similar_tools["views"][7], similar_tool_8_citations=similar_tools["citations"][7], similar_tool_8_similarity=similar_tools["similarity"][7],
				similar_tool_9_name=similar_tools["name_tool"][8],similar_tool_9_title=similar_tools["title"][8], similar_tool_9_views=similar_tools["views"][8], similar_tool_9_citations=similar_tools["citations"][8], similar_tool_9_similarity=similar_tools["similarity"][8])

		else:
			related_publications_title1=related_publications.title.tolist()[0]
			related_publications_abstract1=related_publications.abstract.tolist()[0]
			related_publications_link1=related_publications.link.tolist()[0]
			related_publications_title2=related_publications.title.tolist()[1]
			related_publications_abstract2=related_publications.abstract.tolist()[1]
			related_publications_link2=related_publications.link.tolist()[1]
			return render_template("tool_2article.html", entry_point=entry_point,keywords=words,tool_main_name=tool_main_name,tool_main_abstract=tool_main_abstract, tool_main_authors=tool_main_authors,
				tool_main_title=tool_main_title, tool_main_homepage=tool_main_homepage,tool_main_date=tool_main_date,tool_main_doi=tool_main_doi, tool_main_link=tool_main_link, tool_main_views=tool_main_views,
				tool_main_citations=tool_main_citations,tool_main_altmetric=tool_main_altmetric,tool_main_journal=tool_main_journal,related_publications_title1=related_publications_title1,related_publications_abstract1=related_publications_abstract1,related_publications_link1=related_publications_link1,
				related_publications_title2=related_publications_title2,related_publications_abstract2=related_publications_abstract2,related_publications_link2=related_publications_link2,
				similar_tool_1_name=similar_tools["name_tool"][0],similar_tool_1_title=similar_tools["title"][0], similar_tool_1_views=similar_tools["views"][0], similar_tool_1_citations=similar_tools["citations"][0], similar_tool_1_similarity=similar_tools["similarity"][0],
				similar_tool_2_name=similar_tools["name_tool"][1],similar_tool_2_title=similar_tools["title"][1], similar_tool_2_views=similar_tools["views"][1], similar_tool_2_citations=similar_tools["citations"][1], similar_tool_2_similarity=similar_tools["similarity"][1],
				similar_tool_3_name=similar_tools["name_tool"][2],similar_tool_3_title=similar_tools["title"][2], similar_tool_3_views=similar_tools["views"][2], similar_tool_3_citations=similar_tools["citations"][2], similar_tool_3_similarity=similar_tools["similarity"][2],
				similar_tool_4_name=similar_tools["name_tool"][3],similar_tool_4_title=similar_tools["title"][3], similar_tool_4_views=similar_tools["views"][3], similar_tool_4_citations=similar_tools["citations"][3], similar_tool_4_similarity=similar_tools["similarity"][3],
				similar_tool_5_name=similar_tools["name_tool"][4],similar_tool_5_title=similar_tools["title"][4], similar_tool_5_views=similar_tools["views"][4], similar_tool_5_citations=similar_tools["citations"][4], similar_tool_5_similarity=similar_tools["similarity"][4], 
				similar_tool_6_name=similar_tools["name_tool"][5],similar_tool_6_title=similar_tools["title"][5], similar_tool_6_views=similar_tools["views"][5], similar_tool_6_citations=similar_tools["citations"][5], similar_tool_6_similarity=similar_tools["similarity"][5],
				similar_tool_7_name=similar_tools["name_tool"][6],similar_tool_7_title=similar_tools["title"][6], similar_tool_7_views=similar_tools["views"][6], similar_tool_7_citations=similar_tools["citations"][6], similar_tool_7_similarity=similar_tools["similarity"][6],
				similar_tool_8_name=similar_tools["name_tool"][7],similar_tool_8_title=similar_tools["title"][7], similar_tool_8_views=similar_tools["views"][7], similar_tool_8_citations=similar_tools["citations"][7], similar_tool_8_similarity=similar_tools["similarity"][7],
				similar_tool_9_name=similar_tools["name_tool"][8],similar_tool_9_title=similar_tools["title"][8], similar_tool_9_views=similar_tools["views"][8], similar_tool_9_citations=similar_tools["citations"][8], similar_tool_9_similarity=similar_tools["similarity"][8])








@app.route(entry_point+'/search/', methods=["GET", "POST"])
def search():
 	return render_template("search.html", entry_point=entry_point)




@app.route(entry_point+'/t2n/')
def canvas():
	return render_template("t2n.html", entry_point=entry_point)


@app.route(entry_point+'/about/')
def about():
	return render_template("about.html", entry_point=entry_point)

	



@app.route(entry_point+'/results/<chosen_tool>', methods=["GET", "POST"])
def results(chosen_tool):
	query1 = "SELECT * FROM articles LEFT JOIN tools ON tools.article_fk=articles.id LEFT JOIN metrics ON metrics.id= articles.id WHERE (LCASE(abstract) LIKE %(this_name)s OR LCASE(topics) LIKE %(this_name)s OR LCASE(authors) LIKE %(this_name)s) AND main=1 ORDER BY citations DESC"
	tool_info = pd.read_sql(query1,con=engine, params={'this_name': '%'+ chosen_tool +'%'})
	length=len(tool_info)	
	return render_template("results.html", tool_info=tool_info, length=length, entry_point=entry_point, chosen_tool=chosen_tool)


@app.route(entry_point+'/results_advanced/', methods=["GET", "POST"])
def results_advanced():
	attempted_word = request.args.get("word_for_search")
	sort_selection=request.args.get("sort_selection")
	type_selection=request.args.get("type_selection")
	article_selection=request.args.get("article_part_selection")
	journal_selection=request.args.get("journal_selection")


#Flags are needed for query
	flag_type=False
	flag_journal=False
	flag_part=False
	query_basic="SELECT * FROM articles LEFT JOIN tools ON tools.article_fk=articles.id LEFT JOIN metrics ON metrics.id= articles.id WHERE"


#First decision: WHOLE ARTICLE OR SPECIFIC PART
	if article_selection == "whole_article":
		query_basic=query_basic+" (LCASE(abstract) LIKE %(this_name)s OR LCASE(topics) LIKE %(this_name)s OR LCASE(authors) LIKE %(this_name)s OR LCASE(title) LIKE %(this_name)s)"
	else:
		flag_part=True
		if article_selection=="name_tool":
			query_basic=query_basic+" (LCASE(name_tool) LIKE %(this_name)s)"
		if article_selection=="title":
			query_basic=query_basic+" (LCASE(title) LIKE %(this_name)s)"				
		if article_selection=="abstract":
			query_basic=query_basic+" (LCASE(abstract) LIKE %(this_name)s)"
		if article_selection=="topics":
			query_basic=query_basic+" (LCASE(topics) LIKE %(this_name)s)"
		if article_selection=="authors":
			query_basic=query_basic+" (LCASE(authors) LIKE %(this_name)s)"

#Second decision: SPECIFIC TOOL TYPE OR NOT
	if type_selection == "all_types":
		query_basic=query_basic+ " AND (main=1)"
	else:
		flag_type=True
		query_basic=query_basic+ " AND (main=1 AND additional_info= %(type_info)s)"
#Third decision: SPECIFIC JOURNAL OR NOT
	if journal_selection=="any_journal":
		pass
	else:
		flag_journal=True
		journal_key=int(journal_selection)
		query_basic=query_basic+" AND (journal_fk=%(journal_id)s)"
#Fourth decision: SORTING METHOD
	if sort_selection=="views":
		query_basic=query_basic+" ORDER BY views DESC"
	if sort_selection=="citations":
		query_basic=query_basic+" ORDER BY citations DESC"
	if sort_selection=="date":
		query_basic=query_basic+" ORDER BY date DESC"

# This does not work you need only as many arguments as needed:
# Always attempted word
	if (not flag_journal) and (not flag_type):

		tool_info = pd.read_sql(query_basic,con=engine, params={'this_name': '%'+ attempted_word +'%' })
	elif not flag_journal and flag_type:
		tool_info = pd.read_sql(query_basic,con=engine, params={'this_name': '%'+ attempted_word +'%','type_info': type_selection })
	elif flag_journal and not flag_type:
		tool_info = pd.read_sql(query_basic,con=engine, params={'this_name': '%'+ attempted_word +'%','journal_id': journal_key, })
	else:
		tool_info = pd.read_sql(query_basic,con=engine, params={'this_name': '%'+ attempted_word +'%','type_info': type_selection,'journal_id': journal_key, })


	if len(tool_info)==0:
		error="No matching results"
		return render_template("search.html", entry_point=entry_point, error=error)
	else:
		length=len(tool_info)
		return render_template("result_advanced.html", tool_info=tool_info, length=length, entry_point=entry_point,flag_type=flag_type, flag_journal=flag_journal, flag_part=flag_part, main_word=attempted_word, preference_type=type_selection, preference_journal=journal_selection, preference_part=article_selection)	




@app.route(entry_point+'/filtered_results/', methods=["GET", "POST"])
def filtered_results():

	main_word=request.args.get("main_word")
	attempted_word = request.args.get("additional_keyword")
	sort_selection=request.args.get("sort_selection")
	type_selection=request.args.get("type_selection")
	article_selection=request.args.get("article_part_selection")
	journal_selection=request.args.get("journal_selection")
	article_selection_keyword=request.args.get("article_part_selection_keyword")
	if main_word=="":
		main_word=" "

#Flags are needed for query
	flag_type=False
 	flag_journal=False
 	query_basic="SELECT * FROM articles LEFT JOIN tools ON tools.article_fk=articles.id LEFT JOIN metrics ON metrics.id= articles.id WHERE"
 	if attempted_word=="":
# #First decision: WHOLE ARTICLE OR SPECIFIC PART	
		if article_selection == "whole_article":
			query_basic=query_basic+" (LCASE(abstract) LIKE %(this_name)s OR LCASE(topics) LIKE %(this_name)s OR LCASE(authors) LIKE %(this_name)s OR LCASE(title) LIKE %(this_name)s)"
		else:
			if article_selection=="name_tool":
				query_basic=query_basic+" (LCASE(name_tool) LIKE %(this_name)s)"
			if article_selection=="title":
				query_basic=query_basic+" (LCASE(title) LIKE %(this_name)s)"				
			if article_selection=="abstract":
				query_basic=query_basic+" (LCASE(abstract) LIKE %(this_name)s)"
			if article_selection=="topics":
				query_basic=query_basic+" (LCASE(topics) LIKE %(this_name)s)"
			if article_selection=="authors":
				query_basic=query_basic+" (LCASE(authors) LIKE %(this_name)s)"

	# #Second decision: SPECIFIC TOOL TYPE OR NOT
		if type_selection == "all_types":
			query_basic=query_basic+ " AND (main=1)"
		else:
			flag_type=True
			query_basic=query_basic+ " AND (main=1 AND additional_info= %(type_info)s)"
	# #Third decision: SPECIFIC JOURNAL OR NOT
		if journal_selection=="any_journal":
			pass
		else:
			flag_journal=True
			journal_key=int(journal_selection)
			query_basic=query_basic+" AND (journal_fk=%(journal_id)s)"
	# #Fourth decision: SORTING METHOD
		if sort_selection=="views":
			query_basic=query_basic+" ORDER BY views DESC"
		if sort_selection=="citations":
			query_basic=query_basic+" ORDER BY citations DESC"
		if sort_selection=="date":
			query_basic=query_basic+" ORDER BY date DESC"
	 # This does not work you need only as many arguments as needed:
	 # Always attempted word
		if (not flag_journal) and (not flag_type):
			tool_info = pd.read_sql(query_basic,con=engine, params={'this_name': '%'+ main_word +'%' })
		elif not flag_journal and flag_type:
			tool_info = pd.read_sql(query_basic,con=engine, params={'this_name': '%'+ main_word +'%','type_info': type_selection })
		elif flag_journal and not flag_type:
			tool_info = pd.read_sql(query_basic,con=engine, params={'this_name': '%'+ main_word +'%','journal_id': journal_key, })
		else:
			tool_info = pd.read_sql(query_basic,con=engine, params={'this_name': '%'+ main_word +'%','type_info': type_selection,'journal_id': journal_key, })

		if len(tool_info)==0:
			error="No matching results"
			return render_template("search.html", entry_point=entry_point, error=error)
		else:
			length=len(tool_info)
			return render_template("filtered.html", tool_info=tool_info,entry_point=entry_point, length=length)

	else:
		flag_type=False
		flag_journal=False
		query_basic="SELECT * FROM articles LEFT JOIN tools ON tools.article_fk=articles.id LEFT JOIN metrics ON metrics.id= articles.id WHERE"
		if article_selection == "whole_article":
			query_basic=query_basic+" (LCASE(abstract) LIKE %(this_name)s OR LCASE(topics) LIKE %(this_name)s OR LCASE(authors) LIKE %(this_name)s OR LCASE(title) LIKE %(this_name)s)"
		else:
			if article_selection=="name_tool":
				query_basic=query_basic+" (LCASE(name_tool) LIKE %(this_name)s)"
			if article_selection=="title":
				query_basic=query_basic+" (LCASE(title) LIKE %(this_name)s)"				
			if article_selection=="abstract":
				query_basic=query_basic+" (LCASE(abstract) LIKE %(this_name)s)"
			if article_selection=="topics":
				query_basic=query_basic+" (LCASE(topics) LIKE %(this_name)s)"
			if article_selection=="authors":
				query_basic=query_basic+" (LCASE(authors) LIKE %(this_name)s)"
		if article_selection_keyword == "whole_article":
			query_basic=query_basic+" AND (LCASE(abstract) LIKE %(new_name)s OR LCASE(topics) LIKE %(new_name)s OR LCASE(authors) LIKE %(new_name)s OR LCASE(title) LIKE %(new_name)s)"
		else:
			if article_selection_keyword=="name_tool":
				query_basic=query_basic+" AND (LCASE(name_tool) LIKE %(new_name)s)"
			if article_selection_keyword=="title":
				query_basic=query_basic+" AND (LCASE(title) LIKE %(new_name)s)"				
			if article_selection_keyword=="abstract":
				query_basic=query_basic+" AND (LCASE(abstract) LIKE %(new_name)s)"
			if article_selection_keyword=="topics":
				query_basic=query_basic+" AND (LCASE(topics) LIKE %(new_name)s)"
			if article_selection_keyword=="authors":
					query_basic=query_basic+" AND (LCASE(authors) LIKE %(new_name)s)"
			if type_selection == "all_types":
				query_basic=query_basic+ " AND (main=1)"
			else:
				flag_type=True
				query_basic=query_basic+ " AND (main=1 AND additional_info= %(type_info)s)"
		#Third decision: SPECIFIC JOURNAL OR NOT
			if journal_selection=="any_journal":
				pass
			else:
				flag_journal=True
				journal_key=int(journal_selection)
				query_basic=query_basic+" AND (journal_fk=%(journal_id)s)"
		#Fourth decision: SORTING METHOD
			if sort_selection=="views":
				query_basic=query_basic+" ORDER BY views DESC"
			if sort_selection=="citations":
				query_basic=query_basic+" ORDER BY citations DESC"
			if sort_selection=="date":
				query_basic=query_basic+" ORDER BY date DESC"

		# This does not work you need only as many arguments as needed:
		# Always attempted word
			if (not flag_journal) and (not flag_type):
				tool_info = pd.read_sql(query_basic,con=engine, params={'this_name': '%'+ main_word +'%', 'new_name': '%'+ attempted_word +'%' })
			elif not flag_journal and flag_type:
				tool_info = pd.read_sql(query_basic,con=engine, params={'this_name': '%'+ main_word +'%','new_name': '%'+ attempted_word +'%','type_info': type_selection })
			elif flag_journal and not flag_type:
				tool_info = pd.read_sql(query_basic,con=engine, params={'this_name': '%'+ main_word +'%','new_name': '%'+ attempted_word +'%','journal_id': journal_key, })
			else:
				tool_info = pd.read_sql(query_basic,con=engine, params={'this_name': '%'+ main_word +'%','new_name': '%'+ attempted_word +'%','type_info': type_selection,'journal_id': journal_key, })
			
			if len(tool_info)==0:
				error="No matching results"
				return render_template("search.html", entry_point=entry_point, error=error)
			else:
				length=len(tool_info)
				return render_template("filtered.html", tool_info=tool_info,entry_point=entry_point, length=length)
				if len(tool_info)==0:
					error="No matching results"
					return render_template("search.html", entry_point=entry_point, error=error)













@app.route(entry_point+'/filtered_results_main/', methods=["GET", "POST"])
def filtered_results_main():
#You started your seach on the main page, you have at least one word-that word is search for everywhere
	attempted_word = request.args.get("word_for_search")

	sort_selection=request.args.get("sort_selection")

	type_selection=request.args.get("type_selection")

	article_selection=request.args.get("article_part_selection")

	journal_selection=request.args.get("journal_selection")

	main_word=request.args.get("main_word")

	if main_word=="":
		main_word=" "
	if (attempted_word ==""):
#Flags are needed for query
		flag_type=False
		flag_journal=False
# Look for the main word everywhere and then appedn user's options
		query_basic="SELECT * FROM articles LEFT JOIN tools ON tools.article_fk=articles.id LEFT JOIN metrics ON metrics.id= articles.id WHERE"
		query_basic=query_basic+" (LCASE(abstract) LIKE %(this_name)s OR LCASE(topics) LIKE %(this_name)s OR LCASE(authors) LIKE %(this_name)s OR LCASE(title) LIKE %(this_name)s)"


	#Second decision: SPECIFIC TOOL TYPE OR NOT
		if type_selection == "all_types":
			query_basic=query_basic+ " AND (main=1)"
		else:
			flag_type=True
			query_basic=query_basic+ " AND (main=1 AND additional_info= %(type_info)s)"
	#Third decision: SPECIFIC JOURNAL OR NOT
		if journal_selection=="any_journal":
			pass
		else:
			flag_journal=True
			journal_key=int(journal_selection)
			query_basic=query_basic+" AND (journal_fk=%(journal_id)s)"
	#Fourth decision: SORTING METHOD
		if sort_selection=="views":
			query_basic=query_basic+" ORDER BY views DESC"
		if sort_selection=="citations":
			query_basic=query_basic+" ORDER BY citations DESC"
		if sort_selection=="date":
			query_basic=query_basic+" ORDER BY date DESC"

	# This does not work you need only as many arguments as needed:
	# Always attempted word
		if (not flag_journal) and (not flag_type):

			tool_info = pd.read_sql(query_basic,con=engine, params={'this_name': '%'+ main_word +'%' })
		elif not flag_journal and flag_type:
			tool_info = pd.read_sql(query_basic,con=engine, params={'this_name': '%'+ main_word +'%','type_info': type_selection })
		elif flag_journal and not flag_type:
			tool_info = pd.read_sql(query_basic,con=engine, params={'this_name': '%'+ main_word +'%','journal_id': journal_key, })
		else:
			tool_info = pd.read_sql(query_basic,con=engine, params={'this_name': '%'+ main_word +'%','type_info': type_selection,'journal_id': journal_key, })


		if len(tool_info)==0:
			error="No matching results"
			return render_template("search.html", entry_point=entry_point, error=error)
		else:
			length=len(tool_info)
			return render_template("filtered.html", tool_info=tool_info,entry_point=entry_point,  length=length)
	else:
# Second option-ADDITIONAL WORD TO QUERY
		flag_type=False
		flag_journal=False
		query_basic="SELECT * FROM articles LEFT JOIN tools ON tools.article_fk=articles.id LEFT JOIN metrics ON metrics.id= articles.id WHERE"
		query_basic=query_basic+" (LCASE(abstract) LIKE %(this_name)s OR LCASE(topics) LIKE %(this_name)s OR LCASE(authors) LIKE %(this_name)s OR LCASE(title) LIKE %(this_name)s)"
		if article_selection == "whole_article":
			query_basic=query_basic+" AND (LCASE(abstract) LIKE %(new_name)s OR LCASE(topics) LIKE %(new_name)s OR LCASE(authors) LIKE %(new_name)s OR LCASE(title) LIKE %(new_name)s)"
		else:
			if article_selection=="name_tool":
				query_basic=query_basic+" AND (LCASE(name_tool) LIKE %(new_name)s)"
			if article_selection=="title":
				query_basic=query_basic+" AND (LCASE(title) LIKE %(new_name)s)"				
			if article_selection=="abstract":
				query_basic=query_basic+" AND (LCASE(abstract) LIKE %(new_name)s)"
			if article_selection=="topics":
				query_basic=query_basic+" AND (LCASE(topics) LIKE %(new_name)s)"
			if article_selection=="authors":
				query_basic=query_basic+" AND (LCASE(authors) LIKE %(new_name)s)"
		#Second decision: SPECIFIC TOOL TYPE OR NOT
		if type_selection == "all_types":
			query_basic=query_basic+ " AND (main=1)"
		else:
			flag_type=True
			query_basic=query_basic+ " AND (main=1 AND additional_info= %(type_info)s)"
	#Third decision: SPECIFIC JOURNAL OR NOT
		if journal_selection=="any_journal":
			pass
		else:
			flag_journal=True
			journal_key=int(journal_selection)
			query_basic=query_basic+" AND (journal_fk=%(journal_id)s)"
	#Fourth decision: SORTING METHOD
		if sort_selection=="views":
			query_basic=query_basic+" ORDER BY views DESC"
		if sort_selection=="citations":
			query_basic=query_basic+" ORDER BY citations DESC"
		if sort_selection=="date":
			query_basic=query_basic+" ORDER BY date DESC"

	# This does not work you need only as many arguments as needed:
	# Always attempted word
		if (not flag_journal) and (not flag_type):

			tool_info = pd.read_sql(query_basic,con=engine, params={'this_name': '%'+ main_word +'%', 'new_name': '%'+ attempted_word +'%' })
		elif not flag_journal and flag_type:
			tool_info = pd.read_sql(query_basic,con=engine, params={'this_name': '%'+ main_word +'%','new_name': '%'+ attempted_word +'%','type_info': type_selection })
		elif flag_journal and not flag_type:
			tool_info = pd.read_sql(query_basic,con=engine, params={'this_name': '%'+ main_word +'%','new_name': '%'+ attempted_word +'%','journal_id': journal_key, })
		else:
			tool_info = pd.read_sql(query_basic,con=engine, params={'this_name': '%'+ main_word +'%','new_name': '%'+ attempted_word +'%','type_info': type_selection,'journal_id': journal_key, })
		
		if len(tool_info)==0:
			error="No matching results"
			return render_template("search.html", entry_point=entry_point, error=error)
		else:
			length=len(tool_info)
			return render_template("filtered.html", tool_info=tool_info,entry_point=entry_point, length=length)	

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)



