import urllib2
import re
from datetime import *
from beebotte import *
from pymongo import *

#Se obtiene el primer numero aleatorio de la URL
url = "http://www.numeroalazar.com.ar/"
urltext = urllib2.urlopen(url).read()
datos = re.findall("[0-9]{1,2}[.]+[0-9]{1,2}",urltext)

tam = len(datos)
Nnum = 50 #cantidad de numeros por defecto
if tam > Nnum: #Hay mas numeros previos --> se quitan
 primero = tam - Nnum
else:
 primero = 0
Naleatorio = datos[primero] #Se coge unicamente el primero

#Se obtiene la fecha y hora del servidor de la aplicacion
fechahora = str(datetime.today()).split(".")
fechahora = fechahora[0] #fecha y hora sin ms hh:mm:ss

#Se guarda en la BD local (MongoDB)
Mclient = MongoClient("localhost", 27017) #Se crea conexion
db = Mclient.BDint
result = db.dataset.insert_one(
  {
   "num" : float(Naleatorio),
   "fecha" : fechahora,
  }
 )

#Se guarda en la BD externa (Beebotte)
Bclient = BBT("acf58919629d0c03c6499ad25d366389", 
"09b9f3e524c3d4b711f467feb68f78b9706ee54f760c590d4ecb72791a06d29d") #Se crea conexion
Bclient.write('BDext', 'num', float(Naleatorio))
Bclient.write('BDext', 'fecha', fechahora)