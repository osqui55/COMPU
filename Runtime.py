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
print 'Se ha obtenido el numero '+Naleatorio+' a las '+hora+' del '+dia+'/'+mes+'/'+anno

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
 
#Comprobacion de almacenamiento en MongoDB
cursor = db.dataset.find()
for aux in cursor: 
 valores = aux['num']
 d = aux['dia']
 m = aux['mes']
 a = aux['anno']
 h = aux['hora']
print d+'/'+m+'/'+a+' a las '+hora+' se introdujo el numero '+valores


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