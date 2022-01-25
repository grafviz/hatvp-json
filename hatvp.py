import xml,json,xmltodict
from datetime import date
from modif_nested_diff import diff, patch
import sys
#from deepdiff import DeepDiff

#a partir du fichier "declarations.xml", produit les fichiers json declas,declas-diff,dernieres-declas

xmlfilename=sys.argv[1] if len(sys.argv)>1 else 'declarations.xml'

verbosis=False

today = str(date.today())
print( xmlfilename,today)

#save=False


def verbose(*args,**kwargs):
    if verbosis:
        print(*args,**kwargs)

def printjs(s):
    verbose(json.dumps(s, indent=4, sort_keys=True, ensure_ascii=False))




with open(xmlfilename, "r+") as xmlFile:
   obj = xmltodict.parse(xmlFile.read(), encoding='utf-8')['declarations']['declaration']
#obj=obj['declarations']['declaration'][0]
#s=obj["activCollaborateursDto"]['items']['items'][0]['commentaire']
#verbose(type(obj),s,type(s))
#printjs(obj)

def compare(d1,d2):
    #compare dates
    #verbose(d1,'>',d2,'?')
	d1=d1.split('/')
	d2=d2.split('/')
	return True if d1[2]>d2[2] else (True if d1[1]>d2[1] else True if d1[0]>d2[0] else False)

result={}#>declas.json
last_result={}#>derniers_declas.json

#special=['nom','nomSociete','descriptionMandat','employeur','employeurConjoint','etablissement']

for i in obj:
	nom=i['general']['declarant']['nom']+', '+i['general']['declarant']['prenom']
	date_elts=i['dateDepot'].split(' ')[0].split('/')+[i['dateDepot'].split(' ')[1]]
	key=nom+' - '+date_elts[2]+'-'+date_elts[1]+'-'+date_elts[0]+'-'+date_elts[3]
	print(key)
	clean_entry={}
	for k in i:
		printjs(i[k])
		if 'neant' in i[k]:
			#verbose('neant',i[k]['neant'])
			if i[k]['neant']=='false' and  'items' in i[k] and i[k]['items']!=None:
				#verbose('ok?',i[k]['items'])
				clean_entry[k]=i[k]['items']['items']
				if len(i[k].keys())>2:
					input('error, unusual file')
		else:
			clean_entry[k]=i[k]

		print('----')
	result[key]=clean_entry
	if nom in last_result:
		print('Dépôt existant')
		if compare(i['dateDepot'],last_result[nom]['dateDepot']):
			print('Dépôt plus récent')
			last_result[nom]=clean_entry
		else:
			print('Dépôt plus ancien')
	else:
		last_result[nom]=clean_entry




# result={}
# for i in obj:
# 	nom=i['general']['declarant']['prenom']+' '+i['general']['declarant']['nom']
# 	result[nom]=i
with open("declarations-"+today+".json", "w+") as jsonFile:
		jsonFile.seek(0)
		json.dump(result, jsonFile, indent = 4, separators = (',', ':'), sort_keys=True)
		jsonFile.truncate()

with open("dernieres-declarations-"+today+".json", "w+") as jsonFile:
		jsonFile.seek(0)
		json.dump(last_result, jsonFile, indent = 4, separators = (',', ':'), sort_keys=True)
		jsonFile.truncate()


print("Différences avec déclarations précédentes")
results={}
previous_name=''
prev_decla={}
for key in result.keys():
    print(key)
    name=key.split(' - ')[0]
    decla=result[key]
    if name==previous_name:#compute diff
        print("compute diff...")
        date=key.split(' - ')[1]
        difference=diff(prev_decla,decla,U=False)
        verbose("différence",printjs(difference))
        results[key+' - MODIF']=difference
    else:
    	results[key]=decla
    prev_decla=decla
    previous_name=name


with open("declarations-diffs-"+today+".json", "w+") as jsonFile:
		jsonFile.seek(0)
		json.dump(results, jsonFile, indent = 4, separators = (',', ':'), sort_keys=True)
		jsonFile.truncate()
