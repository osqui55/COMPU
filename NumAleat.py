from flask import Flask
from flask import render_template
from flask import request
from beebotte import *
from pymongo import MongoClient

app = Flask(__name__)




import urllib2
import re
from datetime import *
import Pract1
from beebotte import *
from pymongo import *
import schedule
import time

def runtime():
 print 'tu puta madre'
 #Se obtiene el primer numero aleatorio de la URL
 url = "http://www.numeroalazar.com.ar/"
 urltext = urllib2.urlopen(url).read()
 datos = re.findall("(100|[0-9]{1,2})[.]+[0-9]{2}",urltext)
 #Se coge unicamente el primero
 tam = len(datos)
 Nnum = 50 #cantidad de numeros por defecto
 if tam > Nnum:
  primero = tam - Nnum
 else:
  primero = 0
 Naleatorio = datos[primero]

 #Se obtiene la fecha  y hora del servidor de la aplicacion
 fechahora = str(datetime.today()).split(" ")
 fecha = fechahora[0].split('-')
 dia = fecha[2]
 mes = fecha[1]
 anno =fecha[0]
 horaTot = fechahora[1].split(".")
 hora = horaTot[0]

 #Se guarda en la BD local (MongoDB)
 client = MongoClient("localhost", 27017) #Se crea conexion
 db = client.BDinterna
 result = db.dataset.insert_one(
   {
    "num" : Naleatorio,
    "dia" : dia,
    "mes" : mes,
    "anno" : anno,
    "hora" : hora
   }
  )
 
 #Se guarda en la BD externa (Beebotte)
 bclient = BBT("acf58919629d0c03c6499ad25d366389", 
 "09b9f3e524c3d4b711f467feb68f78b9706ee54f760c590d4ecb72791a06d29d") #Se crea conexion
 bclient.write('BDexterna', 'num', float(Naleatorio))
 bclient.write('BDexterna', 'hora', hora)
 bclient.write('BDexterna', 'dia', float(dia))
 bclient.write('BDexterna', 'mes', float(mes))
 bclient.write('BDexterna', 'anno', float(anno))

 #Se comprueba si supera umbral (Modo actual)
 try:
  datos = pract1.memoria('leer', 0)
  umbActual = datos[0]
  umbValor = datos[1]
  if umbActual == 1:
   if Naleatorio > umbValor:
    print 'Envio a la web mensaje avisando de SUPERADO'
  else:
   print 'Modo historico'
 except:
  print 'No hay valores almacenados'
  
schedule.every(1).minutes.do(runtime)





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
umbSup = umbSup, UmbActualOK = UmbActualOK)
 
@app.route('/u', methods=['POST'])
def Valor_umbral():
 global UmbActualOK, umb, ult_valor, umbOK, umbSup, mediaOK, BD, BDusada, fechaFull, hora
 
#Se inicia la BD interna porque será más rapido
 Mclient = MongoClient('localhost', 27017)
 db = Mclient.BDinterna
 
 umbOK = 1
 mediaOK = 0
 umbSup = 0
 umb = float(request.form['umbral']) #Umbral introducido
 try:
  modo = request.form['Modo1']
 except:
  print "Se ha seleccionado el modo actual"
 try:
  modo = request.form['Modo2']
 except:
  print "Se ha seleccionado el modo historico"
  
 #Se comprueba el modo seleccionado
 if modo == 'Actual':
  UmbActualOK = 1
 else:
  UmbActualOK = 0
 
 #Si está en modo historico se comprueba la BD 
 if UmbActualOK == 0: 
  memoria('guardar',[UmbActualOK,0])  
  #Se saca la información
  cursor = db.dataset.find()
  for aux in cursor:
   if float(aux['num']) > umb:
    umbSup = 1
	#Se sacan la fecha y hora
    d = aux['dia']
    m = aux['mes']
    a = aux['anno']
    fechaFull = str(d) + '/' + str(m) + '/' + str(a)
    hora = aux['hora']
    break #Si se supera se deja de comprobar(1ª vez que se superó)
  
  #Carga la web con los datos correspondientes
  if umbSup == 1:
   return render_template('PagWeb1.html', mean = mediaOK, umbIN = umbOK, fecha = fechaFull,
   umbSup = umbSup, UmbActualOK = UmbActualOK, val_umbral = umb, hora = hora)
  else:
   return render_template('PagWeb1.html', mean = mediaOK, umbIN = umbOK, umbSup = umbSup, 
   UmbActualOK = UmbActualOK, val_umbral = umb)
 
 #Si está en modo actual se guarda el umbral y se comprobarán nuevos valores
 else:  
  memoria('guardar',[UmbActualOK,umb])
  #Carga la web con los datos correspondientes
  return render_template('PagWeb1.html', mean = mediaOK, umbIN = umbOK, 
  UmbActualOK = UmbActualOK, val_umbral = umb)  
 
@app.route('/m')
def Calcula_media():
 global UmbActualOK, umb, ult_valor, umbOK, umbSup, mediaOK, BD, BDusada
 mediaOK = 1
 UmbActualOK = 0
 umbOK = 0
 media = 0
 suma = 0.00
 
 cont = 0
 pepe = 0
 
#BD externa Beebotte (por defecto)
 if BD == 'Beebotte': 
  BDusada = 'Beebotte'
  BD = 'MongoDB'
  
 #Se sacan los valores
  bclient = BBT("acf58919629d0c03c6499ad25d366389", "09b9f3e524c3d4b711f467feb68f78b9706ee54f760c590d4ecb72791a06d29d")
  resource = Resource(bclient,'BDexterna','num') 
  valores = resource.read()
  
  print str(len(valores))
  
 #Se calcula la media
  for i in range(len(valores)):
   print valores[i]['data']
   suma += valores[i]['data']
  media = suma/float(i+1)
    
#BD interna MongoDB-pymongo
 else: 
  BDusada = 'MongoDB'
  BD = 'Beebotte'
  
 #Se sacan los valores
  client = MongoClient('localhost', 27017)
  db = client.BDinterna
  cursor = db.dataset.find() 
  for aux in cursor:
   print aux['num']
   suma += float(aux['num'])
   cont += 1
  media = suma/float(cont)
  
#Carga la web con los datos correspondientes
 return render_template('PagWeb1.html', mean = mediaOK, media = media, BD = BDusada, 
 umbIN = umbOK, UmbActualOK = UmbActualOK)
 
if __name__ == '__main__':
 app.run(host ='0.0.0.0')