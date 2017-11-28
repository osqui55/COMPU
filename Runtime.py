import urllib2
import re
from datetime import *
import NumAleat
from beebotte import *
from pymongo import *

#Se obtiene el primer numero aleatorio de la URL
url = "http://www.numeroalazar.com.ar/"
urltext = urllib2.urlopen(url).read()
datos = re.findall("[0-9]{1,2}[.]+[0-9]{1,2}",urltext)
#Hay mas numeros previos a los numeros aleatorios generados por la web
tam = len(datos)
Nnum = 50 #cantidad de numeros por defecto
#Se coge unicamente el primero
if tam > Nnum:
 primero = tam - Nnum
else:
 primero = 0
Naleatorio = datos[primero]

#Se obtiene la fecha  y hora del servidor de la aplicacion
fechahora = str(datetime.today()).split(".")
fechahora = fechahora[0] #fecha y hora sin ms hh:mm:ss

#Se guarda en la BD local (MongoDB)
Mclient = MongoClient("localhost", 27017) #Se crea conexion
db = Mclient.BDinter
result = db.dataset.insert_one(
  {
   "num" : float(Naleatorio),
   "fecha" : fechahora,
  }
 )

#Se guarda en la BD externa (Beebotte)
Bclient = BBT("acf58919629d0c03c6499ad25d366389", 
"09b9f3e524c3d4b711f467feb68f78b9706ee54f760c590d4ecb72791a06d29d") #Se crea conexion
Bclient.write('BDexterna', 'num', float(Naleatorio))
Bclient.write('BDexterna', 'fecha', fechahora)

#Se comprueba si supera umbral (Modo actual)
try:
 datos = pract1.memoria('leer', 0)
 umbActual = datos[0]
 if umbActual == 1:
  umbValor = datos[1]
  if Naleatorio > umbValor:
   umbActual = 0
   print 'Envio a la web mensaje avisando de SUPERADO'
   #return render_template('PagWeb1.html', mean = 0, umbIN = 0, UmbActualOK = 0, graf = 0)
 else:
  print 'Modo historico'
except:
 print 'No hay valores almacenados'