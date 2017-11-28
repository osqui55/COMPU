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
 global umbOK,mediaOK
 umbOK = 0
 mediaOK = 0
 
 #Carga la web con los datos correspondientes
 return render_template('PagWeb1.html',umbIN=umbOK,historial=0,mean=mediaOK,graf=0)

 
@app.route('/u', methods=['POST'])
def Valor_umbral():
 global umbOK,UmbActualOK,umb,umbSup,fecha,hora,numeros,fechas,horas,mediaOK,media,BDusada
 try:
 #Se inicia la BD interna porque será más rapido
  Mclient = MongoClient('localhost', 27017)
  db = Mclient.BDinter
 
  umbOK = 1
  hist = 0
  umb = float(request.form['umbral']) #Umbral introducido
  try:
   print mediaOK #si está iniciada
  except:
   mediaOK = 0
   media = 0
   BDusada = ''
 
  #Se determina el modo
  try:
   modo = request.form['Modo1']
  except:
   try:
    modo = request.form['Modo2']
   except: #Historico por defecto
    modo = 'Historico'
  
  #Se comprueba el modo seleccionado
  if modo == 'Actual': #Si está en modo actual se guarda el umbral y se comprobarán nuevos valores
   UmbActualOK = 1
   memoria('guardar',[UmbActualOK,umb])
  
  else: #Si está en modo historico se comprueba la BD 
   UmbActualOK = 0 
   memoria('guardar',[UmbActualOK,0])  
  
  #Se saca la información
   try:
    umbSup = 1 
    #Se obtienen los valores que superan el umbral
    valores = db.dataset.find({'num':{'$gt':float(umb)}})
      
    #Se guardan todos los valores que superen el umbral ordenados
    valoresOrdenados = valores.sort('fecha',pymongo.DESCENDING)
    numeros = []
    fechas = []
    horas = [] 
    for aux in valoresOrdenados:
     numeros.append(aux.get('num'))
     fechahora = str(aux.get('fecha')).split(" ")
     fechas.append(fechahora[0]) #fecha aaaa-mm-dd
     horas.append(fechahora[1]) #hora hh:mm:ss
    
    #Se coge el último valor que superó el umbral
    Num = numeros[0]
    fecha = fechas[0] #fecha aaaa-mm-dd
    hora = horas[0] #hora hh:mm:ss
   except:
    umbSup = 0
  
  #Carga la web con los datos correspondientes
  return render_template('PagWeb1.html',umbIN=umbOK,UmbActualOK=UmbActualOK,val_umbral=umb,
  umbSup=umbSup,fecha=fecha,hora=hora,historial=0,mean=mediaOK,media=media,BD=BDusada,graf=0)
 
 #Si se carga directamente
 except:
  print 'alternativa'
  return render_template('PagWeb1.html',umbIN=0,historial=0,mean=0,graf=0)

  
@app.route('/h')
def HistorialUmbral():
 global umbOK,UmbActualOK,umb,umbSup,fecha,hora,hist,numeros,fechas,horas,mediaOK,media,BDusada
 try:
  try:
   if hist == 0:
    hist = 1 #Se muestra la tabla
   else:
    hist = 0 #No se muestra la tabla
  except:
   hist = 1
  
 #Carga la web con los datos correspondientes
  return render_template('PagWeb1.html',umbIN=umbOK,UmbActualOK=UmbActualOK,val_umbral=umb,umbSup=umbSup,fecha=fecha,
  hora=hora,historial=hist,numeros=numeros,fechas=fechas,horas=horas,mean=mediaOK,media=media,BD=BDusada,graf=0)
 
 #Si se carga directamente
 except:
  print 'alternativa'
  return render_template('PagWeb1.html',umbIN=0,historial=0,mean=0,graf=0)

  
@app.route('/m')
def Calcula_media():
 global umbOK,UmbActualOK,umb,umbSup,fecha,hora,mediaOK,media,BDusada
 try:
  mediaOK = 1
  media = 0
  suma = 0.00
  cont = 0
  try:
   print umbOK #si está iniciada
  except:
   umbOK = 0
   umb = 0
   umbSup = 0
   fecha = ''
   hora = ''
   print 'inicio'
 
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
   bclient = BBT("acf58919629d0c03c6499ad25d366389",
   "09b9f3e524c3d4b711f467feb68f78b9706ee54f760c590d4ecb72791a06d29d")
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
    suma += float(aux.get('num'))
    cont += 1
   media = round(float("{0:.2f}".format(suma/float(cont))),2) #redondeando a dos decimales
  
 #Carga la web con los datos correspondientes
  return render_template('PagWeb1.html',umbIN=umbOK,UmbActualOK=UmbActualOK,val_umbral=umb,
  umbSup=umbSup,fecha=fecha,hora=hora,historial=0,mean=mediaOK,media=media,BD=BDusada,graf=0)

 #Si se carga directamente
 except:
  print 'alternativa'
  return render_template('PagWeb1.html',umbIN=0,historial=0,mean=0,graf=0)

 
@app.route('/g',methods=['POST'])
def Grafica():
 global umbOK,UmbActualOK,umb,umbSup,fecha,hora,mediaOK,media,BDusada
 try:
  return render_template('PagWeb1.html',umbIN=umbOK,UmbActualOK=UmbActualOK,val_umbral=umb,
  umbSup=umbSup,fecha=fecha,hora=hora,historial=0,mean=mediaOK,media=media,BD=BDusada,graf=1)
 
 #Si se carga directamente
 except:
  print 'alternativa'
  return render_template('PagWeb1.html',umbIN=0,historial=0,mean=0,graf=1)
 
if __name__ == '__main__':
 app.run(host ='0.0.0.0')