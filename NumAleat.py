from flask import Flask
from flask import render_template
from flask import request
from beebotte import *
import pymongo
from pymongo import MongoClient

app = Flask(__name__)

#Función para guardar un valor
def memoria(opcion,valor):
 global value
 if opcion == 'guardar':
  value = valor
  return 'OK'
 elif opcion == 'leer':
  return value
 else:
  return 'NOK'

@app.route('/')
def Inicio():
 global UmbActualOK, umb, ult_valor, umbOK, umbSup, mediaOK, BD, BDusada
 ult_valor = 0
 UmbActualOK = 0
 memoria('guardar',[UmbActualOK,0])
 mediaOK = 0
 umbOK = 0
 umbSup = 0
 BD = 'Beebotte'
 
#Carga la web con los datos correspondientes
 return render_template('PagWeb1.html', mean = mediaOK, umbIN = umbOK,
umbSup = umbSup, UmbActualOK = UmbActualOK, graf = 0)
 
@app.route('/u', methods=['POST'])
def Valor_umbral():
 global UmbActualOK, umb, ult_valor, umbOK, umbSup, mediaOK, BD, BDusada, fecha, hora
 
#Se inicia la BD interna porque será más rapido
 Mclient = MongoClient('localhost', 27017)
 db = Mclient.BDinter
 
 umbOK = 1
 mediaOK = 0
 umbSup = 0
 umb = float(request.form['umbral']) #Umbral introducido
 try:
  modo = request.form['Modo1']
 except:
  modo = request.form['Modo2']
  # print "Se ha seleccionado el modo actual"
 # try:
  # modo = request.form['Modo2']
 # except:
  # print "Se ha seleccionado el modo historico"
  
 #Se comprueba el modo seleccionado
 if modo == 'Actual':
  UmbActualOK = 1
 else:
  UmbActualOK = 0
 
 #Si está en modo historico se comprueba la BD 
 if UmbActualOK == 0: 
  memoria('guardar',[UmbActualOK,0])  
  #Se saca la información
  try:
   valores = db.dataset.find({'num':{'$gt':float(umb)}})
   umbSup = 1
   ultVal = valores.sort('fecha',pymongo.DESCENDING)[0] #Se coge el último valor
   Num = ultVal['num']
   #Se obtiene la fecha  y hora del servidor de la aplicacion
   fechahora = str(ultVal['fecha']).split(" ")
   fecha = fechahora[0] #fecha aaaa-mm-dd
   horaTot = fechahora[1].split(".")
   hora = horaTot[0] #hora sin ms hh:mm:ss
  except:
   umbSup = 0
  
  #Carga la web con los datos correspondientes
  if umbSup == 1:
   return render_template('PagWeb1.html', mean = mediaOK, umbIN = umbOK, fecha = fecha,
   umbSup = umbSup, UmbActualOK = UmbActualOK, val_umbral = umb, hora = hora, graf = 0)
  else:
   return render_template('PagWeb1.html', mean = mediaOK, umbIN = umbOK, umbSup = umbSup, 
   UmbActualOK = UmbActualOK, val_umbral = umb, graf = 0)
 
 #Si está en modo actual se guarda el umbral y se comprobarán nuevos valores
 else:  
  memoria('guardar',[UmbActualOK,umb])
  #Carga la web con los datos correspondientes
  return render_template('PagWeb1.html', mean = mediaOK, umbIN = umbOK, 
  UmbActualOK = UmbActualOK, val_umbral = umb, graf = 0)  
 
@app.route('/m')
def Calcula_media():
 global umb, mediaOK, BD, BDusada, cont
 mediaOK = 1
 media = 0
 suma = 0.00
 cont = 0
 
 #Si no se ha iniciado la variable BD
 try:
  len(BD)
 except:
  BD = 'Beebotte'
  
#BD externa Beebotte (por defecto)
 if BD == 'Beebotte': 
  BDusada = 'Beebotte'
  BD = 'MongoDB'
  
 #Se sacan los valores
  bclient = BBT("acf58919629d0c03c6499ad25d366389", "09b9f3e524c3d4b711f467feb68f78b9706ee54f760c590d4ecb72791a06d29d")
  resource = Resource(bclient,'BDexterna','num') 
  valores = resource.read()
  
 #Se calcula la media
  for i in range(len(valores)):
   suma += valores[i]['data']
  media = round(float("{0:.2f}".format(suma/float(i+1))),2) #redondeando a dos decimales
 
#BD interna MongoDB-pymongo
 else: 
  BDusada = 'MongoDB'
  BD = 'Beebotte'
  
 #Se sacan los valores
  client = MongoClient('localhost', 27017)
  db = client.BDinter
  cursor = db.dataset.find() 
  for aux in cursor: 
   suma += float(aux['num'])
   cont += 1
  media = round(float("{0:.2f}".format(suma/float(cont))),2) #redondeando a dos decimales
  
#Carga la web con los datos correspondientes
 return render_template('PagWeb1.html', mean = mediaOK, media = media, BD = BDusada, 
 umbIN = 0, graf = 0)
 
@app.route('/g',methods=['POST'])
def Grafica():
 grafica = 1
 return render_template('PagWeb1.html', mean = 0, umbIN = 0, graf = grafica)

if __name__ == '__main__':
 app.run(host ='0.0.0.0')