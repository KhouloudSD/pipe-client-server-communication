# Les importations necessaires

from fileinput import close
from platform import release
import socket, threading
import math

# Mutex pour assurer l'exlusion mutuelle
agence_mutex=threading.Lock()

#Liste des actions autorisée par le serveur pour le client
actions_autorisees=[]
actions_autorisees.append("consulterVol")
actions_autorisees.append("ConsulterTransaction")
actions_autorisees.append("ConsulterFacture")
actions_autorisees.append("Demander")
actions_autorisees.append("Annuler")
current_threads=[]
msgsize=1024
facture="factures.txt"
hist="histo.txt"
vols="vols.txt"


# Gestion des clients a travers les threads
class threadClients(threading.Thread):

    # Recuperer l'adresse et la socket du client connecté
    def __init__(self,clientAddress,clientsocket):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        print ("nouvelle connexion est ajoutée: ", clientAddress)

    # Recuperer l'action autorisé pour le client connecté afin de l'excéuter
    def run(self):
        print ("connexion d'aprés : ", clientAddress)
        self.csocket.send(bytes("hello",'utf-8'))
        rsp = ''
        while True:
            try:
                data = self.csocket.recv(3072)          
            except socket.error as e:
                print("socket disconnectee !")
                break
            rsp = data.decode()
            if rsp!="Salut":
                print("communication d'aprés client necéssite une action:",rsp.split(",")[0])
                keyword=rsp.split(",")[0]
                if keyword in actions_autorisees:
                    NotificationServeur(clientAddress,rsp,self.csocket)
                elif rsp=='exit':
                    break
                else:
                    msg=" n'est pas reconnu comme une action !"
                    self.csocket.send(bytes(msg,'UTF-8'))

        print("client dont l'adresse est : ", clientAddress , " est deconnete ..")   
# fin de la classe



# Notifier a chaque fois le serveur de l'action effectuer par le(s) client(s) afin
# de poursuivre le process fait par chaque client

def NotificationServeur(ip,message,csock):
    elements=message.split(",")
    if elements[0] == "consulterVol":
        msg=Consulter_vol(elements[1])
        csock.send(bytes(msg,'UTF-8'))
        
    if elements[0] == "ConsulterTransaction":
        msg=Consulter_Transaction_Compte(elements[1])

        csock.send(bytes(msg,'UTF-8'))
    if elements[0] =="ConsulterFacture":
        msg=Consulter_Facture_Agence(elements[1])
        csock.send(bytes(msg,'UTF-8'))  
    if elements[0] == "Demander":
        agence_mutex.acquire()
        fact=Demander(int(elements[1]),int(elements[2]),int(elements[3]))
        if(fact!=-1):
            
            msg="La reservation a été effectuée,Votre nouvelle facture {}\n ".format(fact)
            csock.send(bytes(msg,'UTF-8'))
        else:
            msg="Reservation invalide : vol n'existe pas ou nombre des places insuffisants!"
            csock.send(bytes(msg,'UTF-8'))
        agence_mutex.release()
    if elements[0] == "Annuler":
        agence_mutex.acquire()
        fact=Annuler(int(elements[1]),int(elements[2]),int(elements[3]))
        if(fact!=-1):
            msg=" L'annulation a été effectuée,Votre nouvelle facture {}\n ".format(fact)
            csock.send(bytes(msg,'UTF-8'))
            agence_mutex.release()
        else:
            msg=" L'annulation est invalide : vol n'existe pas \n "
            csock.send(bytes(msg,'UTF-8'))
            agence_mutex.release()
            



# Consulter les Details concernant un vol spécifique 
def Consulter_vol(ref):
        response=""
        vols =open("vols.txt",'r') 
        print("\nfonction consulter vols \n")    
        ligne_vols = vols.readlines()
        for i in ligne_vols:
            columns=i.split(',')
            if int(columns[0])==int(ref):
               vols.close()
               response+="vol:\nRef:{}   Destination:{}   Nombre Places:{}   Prix Place:{}\n".format(columns[0],columns[1],columns[2],columns[3])
               return response  
        
        response += "vol n'existe pas!" 
        return  response






# Suivre les transactions d'une reference bien précise 

def Consulter_Transaction_Compte(ref):
    response=""
    histo =open("histo.txt",'r') 
    hs_list_of_lines = histo.readlines()
    for i in hs_list_of_lines:
        columns=i.split(',')
        if int(columns[1])==int(ref):
            response+="Transaction:\nReference Vol:{}   Agence:{}   Transaction:{}   Valeur:{}      Resultat:{}\n".format(columns[0],columns[1],columns[2],columns[3],columns[4])
    histo.close()
    if response=="":
        response="Pas de transactions faite par votre agence"
    return response


# Parcourir le fichier Factures pour consulter le montant à payer

def Consulter_Facture_Agence(ref):
    facture =open("factures.txt",'r') 
    fs_list_of_lines = facture.readlines()
    for i in fs_list_of_lines:
        columns=i.split(',')
        if int(columns[0])==int(ref):
            return "la facture a payer est :"+columns[1]
    return "agence n'existe pas !"


# Verification de l'existance du vol au niveau du fichier vols

def Verification_Vol_Existence(ref):
    vols=open("vols.txt","r")
    ligne_vol = vols.readlines()
    for i in range(len(ligne_vol)):
        columns=ligne_vol[i].split(',')
        if int(columns[0])==ref:
            return True
    return False


# Annuler un vol 
#il faut noter que chaque annulation sera effectuée mais avec une pénalité de valeur 10% du prix de place.


def Annuler(ref,nb,ag):
    if(Verification_Vol_Existence(ref)):
        facture=open("factures.txt","r") 
        ligne_facture=facture.readlines()
        facture.close()
        vols=open("vols.txt","r")
        ligne_vols=vols.readlines()
        vols.close()
        histo=open(hist,"a")

        for i in range(len(ligne_vols)):
            columns_vol = ligne_vols[i].split(',')
            if(int(columns_vol[0]) == ref):  # this is ref vol
                    columns_vol[2] = int(columns_vol[2]) + nb
                    print(columns_vol[3])
                    ligne_vols[i] = "{},{},{},{}".format(columns_vol[0], columns_vol[1], columns_vol[2], columns_vol[3])
                    histo.write("{},{},Annulation,{},succes\n".format(ref, ag, columns_vol[2]))
            # MAJ facture
                    nouv_facture=0
                    for j in range(len(ligne_facture)):
                        columns_facture = ligne_facture[j].split(',')
                        if(int(columns_facture[0]) == ag):

                            nouv_facture = float(columns_facture[1]) - nb * int(columns_vol[3]) +  0.1* nb * int(columns_vol[3])
                            ligne_facture[j]= "{},{}\n".format(ag,nouv_facture)
                            open("factures.txt",'w').close()
                            try:
                               facture = open("factures.txt", 'w')
                            except IOError:
                               print("Error: could not open file 'factures.txt'")
                            for k in ligne_facture:
                                facture.write(k)     
                    
        facture.close()        
        histo.close()
        open("vols.txt", 'w').close()
        vols = open("vols.txt", "w")

        for i in ligne_vols:
            vols.write(i)   
        vols.close() 
        print("nouv fact:",nouv_facture)
        return nouv_facture
    else:
        
        print("vol n'exite pas")
        return -1   



# Demander la réservation d'un vol en verifiant l'existance du refernce du vol  et le nombre des places  est suffisants

def Demander(ref,nb,ag):
    if(Verification_Vol_Existence(ref)):
        facture=open("factures.txt","r") 
        nouv_facture=0
        # aaaaaaaaaaaaaaaaaaaaaaa
        ligne_facture=facture.readlines()
        facture.close()
        vols=open("vols.txt","r")
        ligne_vols=vols.readlines()
        vols.close()
        histo=open(hist,"a")
        deja_vol = False
        for i in range(len(ligne_vols)):
            columns_vol = ligne_vols[i].split(',')
            if(int(columns_vol[0]) == ref):  # this is ref vol
                deja_vol = True
                if int(columns_vol[2]) >= nb:
                    columns_vol[2] = int(columns_vol[2]) - nb
                    print(columns_vol[3])
                    ligne_vols[i] = "{},{},{},{}".format(columns_vol[0], columns_vol[1], columns_vol[2], columns_vol[3])
                    histo.write("{},{},Demande,{},succes\n".format(ref, ag, columns_vol[2]))
            # MAJ fichiers aaaaaaaaaaaaaaaaaaaa
                    deja_agence = False 
                    
                    for j in range(len(ligne_facture)):
                        columns_facture = ligne_facture[j].split(',')
                        if(int(columns_facture[0]) == ag):
                            deja_agence = True 		
                            nouv_facture = float(columns_facture[1]) + nb * int(columns_vol[3])
                            ligne_facture[j]= "{},{}\n".format(ag,nouv_facture)
                            open("factures.txt",'w').close()
                            try:
                               facture = open("factures.txt", 'w')
                            except IOError:
                               print("Error: could not open file 'factures.txt'")
                            for k in ligne_facture:
                                facture.write(k)     
                    if(deja_agence ==False):
                        print("append")
                        facture = open("factures.txt", 'a')
                        facture.write("{},{}\n".format(ag, nb * int(columns_vol[3])))
                else:
                    histo.write("{},{},Demande,{},impossible\n".format(ref, ag, nb))
                    print("Impossible de réserver : nombre des places insuffisants")

            
        facture.close()        
        histo.close()
        open("vols.txt", 'w').close()
        vols = open("vols.txt", "w")

        for i in ligne_vols:
            vols.write(i)   
        vols.close() 
        print("nouv fact:",nouv_facture)
        return nouv_facture
    else:
        
        print("vol n'exite pas")
        return -1   




# IP address of me
LOCALHOST = "192.168.40.1"
# Port number to listen on
PORT = 8081

# Create a socket object
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to the IP address and port
server.bind((LOCALHOST, PORT))

# Listen for incoming connections
server.listen()

print("Serveur disponible")
print("En attente pour les requtes des clients..")
while True:
    # Boucle principale
    server.listen(1)
    clientsock, clientAddress = server.accept()
    # retourner le couple (socket,addresse)
    newthread = threadClients(clientAddress, clientsock)
    newthread.start()
    current_threads.append(newthread)
    
   