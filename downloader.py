import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.error import HTTPError
from urllib.request import urlopen
from clint.textui import progress

url_prin = "url de la pagina objetivo"

def getLstCursos():
    try:    
        # Obtengo HTML texto plano
        html = urlopen(url_prin)
        #print(html.read())
    except HTTPError as e:
        print(e)

    # Objeto para extraer contenido de HTML, defaultparser:lxml
    bsObj = BeautifulSoup(html.read(),features="lxml")

    # Almacenar en un array las URLs de todos los cursos
    lstCursos = []
    for lst in bsObj.findAll('a'):
        if lst.get("href").find("20")>=0:
            lstCursos.append(lst.get("href")) 

    # Muestra la lista
    for lst in lstCursos: 
        print(lst)
    
    return lstCursos

def getMajorQuality(string):
    apertura = 0
    es_url = 0
    list_urls = []
    url = ''
    for i in range(0,len(string)):
        if string[i] == '"':        
            if apertura == 0:
                apertura = 1            
                if string[i+1:i+6] == 'https':
                    es_url = 1
                else:
                    es_url = 0                        
            else:
                apertura = 0
                es_url = 0
                if url != '':
                    if "mp4" in url:                                         
                        list_urls.append(url)
                        # Obtiene la calidad del Vídeo
                        q = string[i+41:i+44]
                        list_urls.append(q)
                url = ''

        if apertura and es_url:
            if string[i] != '"':
                url = url + string[i]

    # Obtenemos el elemento con la mejor calidad
    i = 1
    mayor = 0
    url_mayor = ""
    while i < len(list_urls):
        if int(list_urls[i]) > mayor:
            mayor = int(list_urls[i])
            url_mayor = list_urls[i-1]
        i = i + 2
    #print("Mayor:",mayor)
    #print("Url mayor:",url_mayor)
    if "?source=1" in url_mayor:
        #url_mayor = url_mayor.replace('?source=1','')
        url_mayor = url_mayor[0:len(url_mayor)-9]
    return url_mayor



def descarga(url,name):
    try:
        r = requests.get(url,stream=True)
        with open(name,"wb") as pyVid:
            total_length = int(r.headers.get('content-length')) # en Bytes
            for ch in progress.bar(r.iter_content(chunk_size = 1024),expected_size=(total_length/1024)+1,label="Progreso ",width=60):
                if ch:
                    pyVid.write(ch)
                    pyVid.flush()
    except Exception as e:
        print("Falló la descarga:",str(e))
        return None

def main():
    # Obtiene lista de: Urls de cursos
    lstCursos = getLstCursos()
    
    # Obtener lista de listas de urls de cada curso
    allUrls = []
    # Recorre todos los cursos
    for url in lstCursos:
        html = urlopen(url)
        bsObj = BeautifulSoup(html.read(),features="lxml")
        urlsCurso = []
        # Recorre todos los videos de un curso
        for lst in bsObj.findAll('iframe'):
            urlVideo = lst.get("src")
            htmlVid = urlopen(urlVideo).read()
            urlVideoClean = getMajorQuality(str(htmlVid))
            urlsCurso.append(urlVideoClean)
        # Guardar la lista de Urls de videos
        allUrls.append(urlsCurso) 
    
    # Descargar videos
    count = 1
    for i in allUrls:
        print("------------------CURSO %d:------------------" % count)
        nroVid = 1
        for j in i:
            nameVid = "curso"+str(count)+"vid"+str(nroVid)+".mp4"
            print("Url video %d: %s"%(nroVid,j))
            try:
                statinfo = os.stat(nameVid)
                if statinfo.st_size <= 3072: # Si su tamanio es inferior a 3 Kbytes 
                    descarga(j,nameVid)
                else:
                    print("El video ya esta descargado!!!")    
            except FileNotFoundError as f:
                    descarga(j,nameVid)
                    
                        
            nroVid = nroVid + 1
        count = count +1
main()    
