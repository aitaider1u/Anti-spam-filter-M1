import numpy as np
import os
import math
import re
from decimal import Decimal
from classifier import Classifier   
from util import loadClassifier   

from util import input_number   
from util import input_string    


def lireMail(fichier, dictionnaire):
	""" 
	Lire un fichier et retourner un vecteur de booléens en fonctions du dictionnaire
	"""
	f = open(fichier, "r",encoding="ascii", errors="surrogateescape")
	mots =   re.split(r' |,|\'|\(|\)|\"|=|\+|`|@|&|%|^|~|#|\*|\||-|_|;|:|!|\?|\n|$|\[|\]|{|}|/',f.read()) #f.read().split(" ")  # re.split(r' |,|-|_|;|!|\n',f.read()) 

	x = [False] * len(dictionnaire) 
	dictionnaire =np.array(dictionnaire)
	# modifié ..............................
	for i in range(len(mots)):			
		index = np.where(dictionnaire == mots[i].upper())[0]
		if len(index) >0:
			x[index[0]] = True
	f.close()
	return x

def charge_dico(fichier):
	f = open(fichier, "r")
	mots = f.read().split("\n")
	print("Chargé " + str(len(mots)) + " mots dans le dictionnaire")
	f.close()
	motsPlusDe3lettre = [mot for mot in mots[:-1] if len(mot) >= 3]
	return motsPlusDe3lettre

def apprendBinomial(dossier, fichiers, dictionnaire):
	"""
	Fonction d'apprentissage d'une loi binomiale a partir des fichiers d'un dossier
	Retourne un vecteur b de paramètres 
	"""
	nb = len(fichiers)
	epsilon = 1
	
	occurencesMots = np.zeros(len(dictionnaire))
	for fichier in fichiers:
		mail = lireMail(dossier+"/"+fichier,dictionnaire)
		occurencesMots = occurencesMots + mail

	#Lissage des paramètres 
	b = ((occurencesMots + epsilon)/ (nb+2*epsilon ))
	return b  # vecteur de paramètres binomiaux


def prediction(x, Pspam, Pham, bspam, bham):
	"""
		Prédit si un mail représenté par un vecteur booléen x est un spam
		à partir du modèle de paramètres Pspam, Pham, bspam, bham.
		Retourne True ou False.
	"""
	#calcul de P(Y=SPAM | X=x)
	x = np.array(x) 
	A = (bspam ** x) # calcul intemediare 
	B = (1-bspam)**(1-x)   # calcul intemediare 
	C = A*B  # calcul intemediare 
	PYspamEtX= (Pham * np.prod(C))  #P(Y=spam, X=x)
	Z_spam = math.log(Pspam)+ np.sum(np.log(C))  

	#calcul de P(Y=Ham | X=x)
	A = (bham ** x) # calcul intemediare 
	B = (1-bham) ** (1-x)   # calcul intemediare 
	C = A*B
	PYhamEtX =(Pham * np.prod(C))  #P(Y=spam , X = x)
	Z_ham = math.log(Pham)+ np.sum(np.log(C))


	PX_x = PYspamEtX + PYhamEtX   # P(X=x) = P(X=x,Y=SPAM) + P(X=x,Y=HAM) =  P(Y=SPAM)  P( X=x | Y=SPAM ) +  P(Y=HAM)* P(X=x | Y=SPAM)

	#limiter l’influence de la précision de la machine sur le calcul
	if (Z_spam >= Z_ham):
		return (True,PYspamEtX/PX_x,PYhamEtX/PX_x)
	return (False,PYspamEtX/PX_x,PYhamEtX/PX_x) 
	
def test(dossier, isSpam, Pspam, Pham, bspam, bham,nbMailToTest):
	"""
		Test le classifieur de paramètres Pspam, Pham, bspam, bham 
		sur tous les fichiers d'un dossier étiquetés 
		comme SPAM si isSpam et HAM sinon
		Retourne le taux d'erreur 
	"""

	fichiers = os.listdir(dossier)
	nbErreur = 0 
	dictionnaire=  charge_dico("dictionnaire1000en.txt")
	cpt = 1 
	for fichier in fichiers[:nbMailToTest]:
		(res,PYspam_x,PYham_x) = prediction(lireMail(dossier+"/"+fichier,dictionnaire),Pspam, Pham, bspam, bham)
		string = ("SPAM" if isSpam else "HAM")+ " "+str(cpt) + " ("+ fichier +") : " + "P(Y=SPAM | X=x) = "+ '{:0.6e}'.format(Decimal(PYspam_x))  + ", P(Y=HAM | X=x) = "+ '{:0.6e}'.format(Decimal(PYham_x))+"\n"
		if (res+isSpam)%2 == 1:
			string = string +  "               => identifié comme un "+("SPAM" if (not isSpam) else "HAM")+" *** erreur ***"		
		else: 
			string = string +  "               => identifié comme un "+("SPAM" if (isSpam) else "HAM")	
		print(string)
		if (res+isSpam)%2 == 0:
			nbErreur = nbErreur+1
		cpt = cpt + 1 

	tauxErreur = nbErreur/nbMailToTest
	return 1-tauxErreur 


def testClassifieur(dossier, isSpam,classifier,nbMailToTest):
	"""
		Test le classifieur de paramètres Pspam, Pham, bspam, bham 
		sur tous les fichiers d'un dossier étiquetés 
		comme SPAM si isSpam et HAM sinon
		Retourne le taux d'erreur 
	"""

	fichiers = os.listdir(dossier)
	nbErreur = 0 
	dictionnaire=  charge_dico("dictionnaire1000en.txt")
	cpt = 1 
	for fichier in fichiers[:nbMailToTest]:
		(res,PYspam_x,PYham_x) = prediction(lireMail(dossier+"/"+fichier,dictionnaire),classifier.get_PSpam(), classifier.get_PHam(),classifier.get_bSpam(),classifier.get_bHam())
		string = ("SPAM" if isSpam else "HAM")+ " "+str(cpt) + " ("+ fichier +") : " + "P(Y=SPAM | X=x) = "+ '{:0.6e}'.format(Decimal(PYspam_x))  + ", P(Y=HAM | X=x) = "+ '{:0.6e}'.format(Decimal(PYham_x))+"\n"
		if (res+isSpam)%2 == 1:
			string = string +  "               => identifié comme un "+("SPAM" if (not isSpam) else "HAM")+" *** erreur ***"		
		else: 
			string = string +  "               => identifié comme un "+("SPAM" if (isSpam) else "HAM")	
		print(string)
		if (res+isSpam)%2 == 0:
			nbErreur = nbErreur+1
		cpt = cpt + 1 

	tauxErreur = nbErreur/nbMailToTest
	return 1-tauxErreur 






############ programme principal ############

# Chargement du dictionnaire:
dictionnaire = charge_dico("dictionnaire1000en.txt")
print(dictionnaire)



dossier_spams = "spam/baseapp/spam"
dossier_hams = "spam/baseapp/ham"

fichiersspams = os.listdir(dossier_spams)
fichiershams =  os.listdir(dossier_hams) 


print("\nChoisir la vesion : \n"+ "  --> 1 : Creer un nouveau Classifieur \033[93m (Saisir 1) \033[0m \n" + "  --> 2 : Charger un ancien classifieur\033[93m (Saisir 2) \033[0m")
version  = input_number(1,2,"Entez votre choix : ")
ClassifierName = "Myclassifier"
classifieur = None


if version == 1:
	print()
	mSpam  = input_number(1,500,"Vous voulez faire un apprentissage sur combien de spam (entre 1 et "+str(len(fichiersspams))+") ?  : ")
	mHam   = input_number(1,2500,"Vous voulez faire un apprentissage sur combien de ham  (entre 1 et "+str(len(fichiershams))+") ?  : ")
	# Apprentissage des bspam et bham:
	print("apprentissage de bspam...")
	bspam = apprendBinomial(dossier_spams, fichiersspams[:mSpam], dictionnaire)
	print("apprentissage de bham...")
	bham = apprendBinomial(dossier_hams, fichiershams[:mHam], dictionnaire)
	print("\033[92mApprentissage fini\033[0m\n")

	# Calcul des probabilités a priori Pspam et Pham:
	Pspam = mSpam/(mSpam+mHam) 
	Pham =  mHam/(mSpam+mHam)

	# Calcul des erreurs avec la fonction test():
	nbSpamToTest = input_number(1,500,"Vous voulez faire un Test  sur combien de spam (entre 1 et "+str(500)+") ?  : ")
	nbHamToTest = input_number(1,500, "Vous voulez faire un Test sur combien de spam (entre 1 et "+str(500)+")  ?  : " )
	erreurSpam =test("spam/baseTest/spam",True,Pspam,Pham,bspam,bham,nbSpamToTest)
	erreurHam = test("spam/baseTest/ham",False,Pspam,Pham,bspam,bham,nbHamToTest)

	print("Erreur de test sur "+ str(nbSpamToTest) + " SPAM      : " +str(round(erreurSpam, 4)*100) +"%")
	print("Erreur de test sur "+ str(nbHamToTest) + " HAM       : " +str(round(erreurHam, 4)*100) +"%")
	print("Erreur de test globale sur "+str(nbSpamToTest+nbHamToTest)+" mails   : " +str((round(erreurSpam, 4)*100+round(erreurHam, 4)*100)/2) +"%")

	#creer l'objet classifier
	classifieur = Classifier(bspam,bham,mSpam,mHam)
	classifierName = input_string("\n---------------------\nVeuillez entrer un nom de fichier pour enregister le classifieur : ","myClassifier");
	classifieur.name = classifierName
	classifieur.save()
	print("\033[92mClassifieur enregisté avec succées\033[0m\n")

elif version == 2 :
	classifieur = loadClassifier()
	print("\033[92mClassifieur chargé avec succées\033[0m\n")


stopLoop = False
while(not stopLoop):
	print()
	print("1 : Apprendre de nouveau Spam  	\033[93m (Saisir 1) \033[0m")
	print("2 : Apprendre de nouveau Ham   	\033[93m (Saisir 2) \033[0m")
	print("3 : Tester le Classifieur      	\033[93m (Saisir 3) \033[0m")
	print("4 : Sauvegarder le Classifie   	\033[93m (Saisir 4) \033[0m")
	print("5 : Quitter                      \033[93m (Saisir 5) \033[0m")
	action = input_number(1,5,"      -->  Saisir votre choix  :  ")

	if (action == 1):
		if(classifieur.nbSpam  >=  len(fichiersspams)):
			print(str(classifieur.nbSpam)+"/"+str(len(fichiersspams))+" Spam ont été appris"+' \033[31mIl reste plus de spam a apprendre dans la base.\033[0m')
		else:
			nbSpamToTest =  input_number(1,len(fichiersspams)-classifieur.nbSpam," Saisir Le nombre de nouveau Spam a apprendre \033[93m (Il reste "+str(len(fichiersspams)-classifieur.nbSpam)+ " dans la base d'apprentissage) \033[0m: ")
			for i in range(nbSpamToTest):
				if(classifieur.nbSpam >=  len(fichiersspams)):
					break
				mail = lireMail(dossier_spams+"/"+fichiersspams[classifieur.nbSpam],dictionnaire)
				classifieur.online_learning_spam(mail)
			print("\033[92mApprentissage online fini \033[0m\n")

	elif(action == 2):
		if(classifieur.nbHam  >=  len(fichiershams)):
			print(str(classifieur.nbHam)+"/"+str(len(fichiershams))+" Ham ont été appris"+' \033[31mIl reste plus de spam a apprendre dans la base.\033[0m')
		else:
			nbHamToTest =  input_number(1,len(fichiershams)-classifieur.nbHam," Saisir Le nombre de nouveau Ham a apprendre \033[93m (Il reste "+str(len(fichiershams)-classifieur.nbHam)+ "dans la base d'apprentissage) \033[0m: ")
			for i in range(nbHamToTest):
				if(classifieur.nbHam >=  len(fichiershams)):
					break
				mail = lireMail(dossier_hams+"/"+fichiershams[classifieur.nbHam],dictionnaire)
				classifieur.online_learning_ham(mail)
			print("\033[92mApprentissage online fini \033[0m\n")

	elif(action == 3):
		# Calcul des erreurs avec la fonction test():
		nbSpamToTest = input_number(1,500,"Vous voulez faire un Test  sur combien de spam (entre 1 et "+str(500)+") ?  : ")
		nbHamToTest = input_number(1,500, "Vous voulez faire un Test sur combien de spam (entre 1 et "+str(500)+")  ?  : " )
		erreurSpam =testClassifieur("spam/baseTest/spam",True,classifieur,nbSpamToTest)
		erreurHam = testClassifieur("spam/baseTest/ham",False,classifieur,nbHamToTest)
		print("Erreur de test sur "+str(nbSpamToTest)+" SPAM      : " +str(round(erreurSpam, 4)*100) +"%")
		print("Erreur de test sur "+str(nbHamToTest)+" HAM       : " +str(round(erreurHam, 4)*100) +"%")
		print("Erreur de test globale sur "+str(nbSpamToTest+nbHamToTest)+" mails   : " +str((round(erreurSpam, 4)*100+round(erreurHam, 4)*100)/2) +"%")

	elif(action == 4):
		classifieur.save()
		print("\033[92mClassifieur "+ classifieur.name+" enregisté avec succées\033[0m\n")
	elif(action == 5):
		classifieur.save()
		stopLoop = True
		



