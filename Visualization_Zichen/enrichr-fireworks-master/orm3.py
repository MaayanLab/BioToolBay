# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 08:30:58 2017

@author: Charlotte
"""

import os
import json, requests
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from fisher import pvalue
from bson.objectid import ObjectId
from pymongo import MongoClient
from decimal import Decimal

client=MongoClient('mongodb://146.203.54.131:27017/')
#client=MongoClient('localhost',27017)
db=client.test

def load_graph(cyjs_filename,meta_df): 
	json_data=json.load(open('notebooks/%s' %cyjs_filename, 'rb'))
	json_data=json_data['elements']['nodes']
    
	scl=MinMaxScaler((-10,10))
    
	coords=np.array([
            [rec['position']['x'] for rec in json_data],
            [rec['position']['y'] for rec in json_data]
            ]).T
	coords=scl.fit_transform(coords)
    
	df = pd.DataFrame({
		'sig_id': map(int,[rec['data']['name'] for rec in json_data]),
		'x': coords[:, 0],
		'y': coords[:, 1],
		}).set_index('sig_id')
	df['z'] = 0
	df = df.merge(meta_df, how='left',left_index=True,right_index=True)
	#df['neglogp'] = -np.log10(df['pvalue']+1e-4)
    
	df = df.sort_index()
	return df

##object was a result id
class EnrichmentResult(object):
	"""EnrichmentResult: object for documents in the userResults collection"""
	projection = {'_id':0}
	default_score = 0.

	def __init__(self, rid,testtype,graph):
		'''To retrieve a result using _id'''
		self.rid = ObjectId(rid)
		doc = db.placeholder6.find_one({'_id': self.rid}, self.projection)
		self.data = doc['data']
		self.result = doc[testtype][str(graph)]
		self.topn=self.result['topn']

	def bind_to_graph(self, df):
		'''Bind the enrichment results to the graph df'''
		df_ = df.copy()
		df_['score'] = self.result['score']
		return df_
	def get_genes(self):
		datadf=pd.DataFrame(self.data, index=range(len(self.data)))		
		return datadf
	def get_topn(self,df):
		df_=df.copy()
		topndf=pd.DataFrame()
		df_['score']=self.result['score']
		df_=df_.drop('x',1)
		df_=df_.drop('y',1)
		df_=df_.drop('z',1)
		df_=df_.drop('geneset2',1)
		#df_.index = np.arange(1, len(df_) + 1)
#		self.topn=[i.encode('UTF8') for i in self.topn]
#		self.topn=map(int,self.topn)
#		self.topn=[i+1 for i in self.topn]
#		df_=df_.iloc[self.topn]
		df_=df_.loc[df_.score<.05]
		df_=df_.loc[df_.score>0]
#		df_=df_.sort_values(['score'],ascending=True)
		values=df_['library'].unique().tolist()
		for i in values:			
			df2=df_.loc[df_.library==i]
			df2=df2.sort_values(['score'])
			if(len(df2.index)>3):
				df2=df2[:3]
			if(len(df2.index)>0):
				df2['score']=df2['score'].apply(lambda x:"{0:.4E}".format(Decimal(x)))
				#df2.score.replace("{0:.4E}".format(Decimal(df2['score'])))
				topndf=topndf.append(df2)
				
		cols=topndf.columns.tolist()			
##		cols=cols[-2:-1]+cols[:-1]+cols[-1:]
		topndf=topndf[cols]	
		return topndf    
       

class EnrichmentResultOffline(object):
    def __init__(self,res,graph):
		self.result=res['result'].loc(graph)
    
    def bind_to_graph(self,df):
		df_=df.copy()
		df_['score'] = self.result
		return df_        



class UserInput(object):
	"""The base class for GeneSets and Signature"""

	default_score = 0. # default enrichment score for an irrelevant signature

	def __init__(self, data):
		self.data = data  #one element dict for upgenes given by user
		self.fisherresult = {}
		self.rid = None
		self.fisherresultdict={}
		self.otherresult={}
		self.otherresultdict={}
#
	def enrich(self,genesetlist):
		for i in range(len(genesetlist)):
			fisherresponse=Fisher(self.data)
			fisherresponse=fisherresponse.fishertest(genesetlist[i])
          #fisherresponse is now a list, create own sigid col
			result=pd.DataFrame({'score':fisherresponse})
			result['score']=result['score']
			result['sig_id']=range(1,len(fisherresponse)+1)
			result2=result.loc[result.score<.05] 
			print(result2)
			result2=result2.sort_values(['score'],ascending=True)
          # change topn value to include everything with p value smaller than .05  
			topn=result2 #.iloc[:100]
			topn['sig_id']=topn['sig_id'].astype(str)
			#topn=dict(zip(str(topn['sig_id']),topn['score']))
			#topn=topn.values.tolist()
#			result=result.sort_values(['sig_id'])


			self.fisherresult={
				'score':result['score'].tolist(),
				'topn':topn['sig_id'].tolist()
				}
			self.fisherresultdict[str(i)]=self.fisherresult
		return self.fisherresultdict
	def enrichother(self,genesetlist):
		for i in range(len(genesetlist)):
			otherresponse=Other(self.data)
			otherresponse=otherresponse.othertest(genesetlist[i])
			result=pd.DataFrame({'score':otherresponse})
			result['score']=(result['score'])
			result['sig_id']=range(1,len(otherresponse)+1)
			result2=result.sort_values(['score'],ascending=True)
			topn=result2.iloc[:100]
			topn['sig_id']=topn['sig_id'].astype(str)
            
			self.otherresult={
				'score':result['score'].tolist(),
				'topn':topn['sig_id'].tolist()
				}
			self.otherresultdict[str(i)]=self.otherresult
		return self.otherresultdict
			
        

    
	def save(self):
        # change so that 
		res=db.placeholder6.insert_one({
			'fishertest':self.fisherresultdict,
			'othertest':self.otherresultdict,
			'data':self.data
			})
		self.rid=res.inserted_id
		return str(self.rid)
	
	def saveoffline(self):
		return self.resultdict

#
#	def bind_enrichment_to_graph(self, net):
#		'''Bind the enrichment results to the graph df'''
#		df['scores'] = self.result['scores']
#		return df


class Fisher(object):
    def __init__(self,data):
        self.data=set(data)
    
    def fishertest(self,genesets):
        #learn how to use the empty, set size list!        
        #pvalues = [None] * len(self.geneset)
        pvalues=[]
        for k in genesets: #for each gene set
                #use from http://blog.nextgenetics.net/?e=16
            intersection=len(self.data&set(k))
            user=len(self.data)
            # k is the inner list, each element of the list a gene
            genelist=len(k)
            total=25000
#   #use from  https://pypi.python.org/pypi/fisher/
            if intersection==0:
                p=1
            else:
                p=pvalue(total,genelist,user,intersection)
                p=p.right_tail
                #oddsratio, pvalue=stats.fisher_exact([[total,genelist],[user,intersection]])
            pvalues.append(p)
              
        return pvalues 
class Other(object):
	def __init__(self,data):
		self.data=set(data)
	def othertest(self,genesets):
		pvalues=[]
		for k in genesets:
			#find pvalues here
			p=1.0
			pvalues.append(p)
		return pvalues

class GeneSets(UserInput):
	"""docstring for GeneSets"""
	def __init__(self, up_genes):
		data = up_genes
		UserInput.__init__(self, data)
		self.type = 'geneSet'
	def json_data(self):
		'''Return an object to be encoded to json format'''
		return self.data
    
#genelistnames={1:'TFgeneset.txt',2:'CellTypegeneset.txt',3:'Ontologygeneset.txt',0:'Diseasesgeneset.txt'}
#genesetlist={}
##each key in genesetlist corresponds to a list(of all genesets) of lists(of genes)
#for (k,v) in genelistnames.items():
#    genesetlist[k]=[]
#    with open(v,'r') as f:
#        for line in f:
#            spl=line.split()
#            li=[]
#            for i in spl[1:]:
#                li.append(i)
#            genesetlist[k].append(li)
#            
#data=['suh']
#why=GeneSets(data)
#why2=why.enrich(genesetlist)
#print(why2) 
