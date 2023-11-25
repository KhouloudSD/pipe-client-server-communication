# les importations
import os
import socket

clear = lambda: os.system('clear')


#les actions autorisées par le serveur pour chaque client

# 1- ----
def consulterVol(client):
  clear()
  print("Entrez la reference du vol à consulter :",end="")
  ref=input()

  client.sendall(bytes("consulterVol,{}".format(ref),'UTF-8'))  

# 2-
def consulterTransaction(client):
  clear()
  client.sendall(bytes("ConsulterTransaction,{}".format(REF_AGENCE),'UTF-8'))  

# 3-
def consulterFacture(client):
  clear()
  client.sendall(bytes("ConsulterFacture,{}".format(REF_AGENCE),'UTF-8'))  

# une des actions effectue par le client : transaction qui présente l'ajout et la retrait d'argent du compte 
# en faisant les mise a jour necessaires 

def transactionAgence():
  clear()
  print("1- reserver un vol ")
  print("2- annuler la réservation")
  print("3- quitter")
  rsp=input()
  while(int(rsp) not in [1,2,3]):
    print("Votre choix est invalide , essayez de nouveau [1,2,3] !")
    rsp=input()
  msg=""
  if int(rsp)==1:
    print("entrez la reference du vol")
    ref=input()
    print("entrez le nombre de places demandées")
    nb=input()
    msg="Demander,{},{},{}".format(ref,nb,REF_AGENCE)
    client.sendall(bytes(msg,'UTF-8'))  

  if int(rsp)==2:
    print("entrez la reference du vol")
    ref=input()
    print("entrez le nombre de places a annuléés")
    nb=input()
    msg="Annuler,{},{},{}".format(ref,nb,REF_AGENCE)
    client.sendall(bytes(msg,'UTF-8'))  

  if int(rsp)==3:
    actionClient(client)


# actions effectuees pour un client 

def actionClient(client):
  clear()
  response=0
  print("1- Consulter un vol")
  print("2- Consulter l’historique des transactions")
  print("3- consulter la facture à payer")
  print("4- etablir une trasaction")
  print("choix d'action :",end="")
  response=input()
  while int(response)not in [1,2,3,4]:
    print("Votre choix est invalide , essayez de nouveau [1,2,3,4] !")
    response=input()
  if(int(response) ==1):
    consulterVol(client)
  if(int(response) ==2):
    consulterTransaction(client)
  if(int(response) ==3):
    consulterFacture(client)
  if(int(response) ==4):
    transactionAgence()




REF_AGENCE =2

# IP address of the receiving VM
LOCALHOST = "192.168.40.1"

# Port number to send data to on the receiving VM
PORT = 8081

# Message to send
message = "Hello, world!"

# Create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client.connect((LOCALHOST, PORT))

client.sendall(bytes("Salut",'UTF-8'))
in_data =  client.recv(30720)
while True:

  actionClient(client) 
  in_data =  client.recv(5072)
  if(in_data.decode()!="Salut"):
    clear()
    print("From Server :" ,in_data.decode())
    input("Press Enter to continue...")
  
  if(in_data.decode()=="exit"):

    break
client.close()