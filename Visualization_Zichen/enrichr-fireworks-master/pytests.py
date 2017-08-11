

from bson.objectid import ObjectId
from pymongo import MongoClient
import scipy.stats as stats

user=['RRM2', 'UBE2C', 'PLK1', 'IDH2', 'CDC25C', 'ANLN', 'CCNA2', 'MELK', 'ESPL1', 'CKS2', 'MCM6', 'CENPO', 'TACC3', 'CDKN3', 'RTN4', 'DTYMK', 'CDCA3', 'TOP2A', 'CKS1B', 'CDCA8', 'HJURP', 'CENPA', 'LMNB2', 'PNP', 'RECQL4', 'PBK', 'NUSAP1']
genelistname={0:"Diseasesgeneset.txt"}
genesetdict={}
with open(genelistname[0],'r') as f:
    
    for line in f:
        spl=line.split()
        key=spl[0]
        li=[]
        for i in spl[1:]:
            li.append(i)
            genesetdict[key]=li
print(genesetdict['5'])
intersection=list(set(user)&set(genesetdict['5']))
intersection=len(intersection)
            
if intersection>0:
     print('we have a match')
user=len(user)
genelist=len(genesetdict['5'])
total=25000
            #use from https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.stats.fisher_exact.html
oddsratio, pvalue=stats.fisher_exact([[total,genelist],[user,intersection]])


print(pvalue)



#client=MongoClient("localhost",27017)
#db=client.test
#genelistname=Diseasesgenesets.txt
#with open(genelistname,'r') as f:
#    for line in f:
#        print(line)


#res=db.placeholder.insert_one({'hello':[1,2,3]})
#rid=res.inserted_id
#print(rid)

#data = {'data':['ABC','GHI','STU','TUV']} 
#class UserInput(object):
#    def __init__(self,data):
#        self.data=data
#        self.ridlist={}
#        self.resultdict={0:{'scores':[1,2,3,1,2,3],'topn':{'similar':[2,5]}},
#                         1:{'scores':[5,2,3,6,2,3],'topn':{'similar':[0,3]}},
#                         2:{'scores':[1,7,3,1,2,8],'topn':{'similar':[1,5]}}}
#    def save(self):
#        for (k,v) in self.resultdict.items():
#            res=db.placeholder.insert_one({
#                    'result':v,
#                    'data':self.data
#                    })
#            self.ridlist[k]=res.inserted_id
#                        
#        return str(self.ridlist)
#r=UserInput(data)
#print(r.save())    
#
##    def __init__(self,data):
##    		 #one element dict for upgenes given by user
##        self.data=data
##    		#self.result = None
##    		#self.type = None
##        self.ridlist = None
##        self.resultdict={0:{'scores':[1,2,3,1,2,3],'topn':{'similar':[2,5]}},
##                         1:{'scores':[5,2,3,6,2,3],'topn':{'similar':[0,3]}},
##                         2:{'scores':[1,7,3,1,2,8],'topn':{'similar':[1,5]}}}    
##    
##    
##    def save(self): #can still use this for the most part
##    		'''Save the UserInput as well as the EnrichmentResult to a document'''
##            #have to change self.result to self.resultdict
##        for (k,v) in self.resultdict.items()
##            res=db.placeholder.insert_one({
##                'result':v,
##                'data':self.data
##                })
##            self.ridlist[k]=res.inserted_id # <class 'bson.objectid.ObjectId'>
##
##        	
##        #self.ridlist = res.inserted_ids # <class 'bson.objectid.ObjectId'>
##        return str(self.ridlist)
#
##r=UserInput(data)
##print(r.save())