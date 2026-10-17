import cv2, numpy

VIDEO_RUTA_ENTRADA = "Video Práctica.mp4"
VIDEO_RUTA_SALIDA = "Video Práctica Salida.avi"
VIDEO_RUTA_OCULTO = "Video Práctica Oculto.avi"

UMBRAL_DIFERENCIA = 10

frameActual = 0
puntos = []
selecciones = {}
numPuntos = 4

modoCirculo = False
centroCirculo = None
radioCirculo = 0
arrastrando = False

def cargarVideo (ruta):
    global fps, size
    videoCapture = cv2.VideoCapture(ruta)
    fps = videoCapture.get(cv2.CAP_PROP_FPS)
    size = (int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    lista = []
    success, frame = videoCapture.read()
    while success:
        lista.append(frame)
        success, frame = videoCapture.read()
    videoCapture.release()
    if len(lista) == 0:
        print("Error al abrir el video")
        return None
    return lista

def diferenciaFrames(frame1, frame2):
    gris1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gris2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    
    total = 0 
    contador = 0 
    for i in range(0, size[1], 10): 
        for j in range(0, size[0], 10): 
            cambio = abs(int(gris1[i, j]) - int(gris2[i, j])) 
            total = total + cambio 
            contador = contador + 1 
    return total / contador 

def saltarFrames(frames, actual):
    for i in range(actual + 1, len(frames)): 
        if diferenciaFrames(frames[actual], frames[i]) > UMBRAL_DIFERENCIA: 
            return i 
    return len(frames) - 1 

def regionesDelFrame(numFrame):
    for frame in range(numFrame, -1, -1):
        if frame in selecciones:
            return selecciones[frame]
    return []

def distancia(p1, p2):
    return int(((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5)
 
def dentroCirculo(region, x, y):
    cx, cy = region[0]
    return (x - cx) ** 2 + (y - cy) ** 2 <= distancia(region[0], region[1]) ** 2

def guardarRegion(region):
    if frameActual not in selecciones:
        selecciones[frameActual] = []
    selecciones[frameActual].append(region)
    
def clic(event, x, y, flags, param):
    global puntos, centroCirculo, radioCirculo, arrastrando
 
    # MODO CÍRCULO: pulsar = centro, arrastrar = radio, soltar = guardar
    if modoCirculo:
        if event == cv2.EVENT_LBUTTONDOWN:
            centroCirculo = (x, y)
            radioCirculo = 0
            arrastrando = True
        elif event == cv2.EVENT_MOUSEMOVE and arrastrando:
            radioCirculo = distancia(centroCirculo, (x, y))
        elif event == cv2.EVENT_LBUTTONUP and arrastrando:
            arrastrando = False
            if distancia(centroCirculo, (x, y)) > 0:
                guardarRegion([centroCirculo, (x, y)])
        return
 
    # RESTO DE FORMAS: un clic por punto
    if event == cv2.EVENT_LBUTTONDOWN:
        puntos.append((x, y))
        print("Punto:", x, y)
        if len(puntos) >= numPuntos:
            if numPuntos == 2 and len(puntos) == 2:
                x1, y1 = puntos[0]
                x2, y2 = puntos[1]
                puntos = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
            guardarRegion(puntos)
            puntos = []

def dibujarPuntos(img, puntos, color, cerrar):
    if cerrar and len(puntos) == 2:
        cv2.circle(img, puntos[0], distancia(puntos[0], puntos[1]), color, 2)
        cv2.circle(img, puntos[0], 4, (0, 0, 255), -1)
        return
    for p in puntos:
        cv2.circle(img, p, 4, (0, 0, 255), -1)        
    for k in range(1, len(puntos)):
        cv2.line(img, puntos[k - 1], puntos[k], color, 2)   
    if cerrar:
        ultimo = len(puntos) - 1
        cv2.line(img, puntos[ultimo], puntos[0], color, 2)      

def mostrarFrame(frames):
   
    vista = cv2.cvtColor(frames[frameActual], cv2.COLOR_BGR2RGB)
    vista = cv2.cvtColor(vista, cv2.COLOR_RGB2BGR)
    if frameActual in selecciones:
        for region in selecciones[frameActual]:
            dibujarPuntos(vista, region, (0, 255, 0), True)
    else:
        for region in regionesDelFrame(frameActual):
            dibujarPuntos(vista, region, (0, 255, 255), True)
    dibujarPuntos(vista, puntos, (0, 255, 0), False)
 
    if arrastrando:
        cv2.circle(vista, centroCirculo, radioCirculo, (0, 255, 0), 2)
        cv2.circle(vista, centroCirculo, 4, (0, 0, 255), -1)
 
    if modoCirculo:
        forma = "Circulo (arrastra el raton)"
    elif numPuntos == 2:
        forma = "Rectangulo"
    elif numPuntos == 3:
        forma = "Triangulo"
    elif numPuntos == 6:
        forma = "Hexagono"
    elif numPuntos == 5:
        forma = "Pentagono"
    else:
        forma = "Poligono 4 puntos"
    cv2.putText(vista, "Frame " + str(frameActual) + "  -  " + forma, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.imshow("Practica 1", vista)

def borrarUltimoPunto():
    global puntos
    if len(puntos) > 0:
        puntos.pop()
    elif frameActual in selecciones and len(selecciones[frameActual]) > 0:
        ultimaRegion = selecciones[frameActual].pop()
        if len(ultimaRegion) > 2 and numPuntos != 2 and not modoCirculo:
            puntos = ultimaRegion[:-1]
        if len(selecciones[frameActual]) == 0:
            del selecciones[frameActual]

def etiquetarVideo(frames):
   
    global frameActual, puntos, numPuntos, modoCirculo, arrastrando
    cv2.namedWindow("Practica 1")
    cv2.setMouseCallback("Practica 1", clic)
    while True:
        mostrarFrame(frames)
        tecla = cv2.waitKey(20)
        if tecla == ord("q"):
            break
        elif tecla == ord("s") and frameActual < len(frames) - 1:
            frameActual = saltarFrames(frames, frameActual)
            puntos = []
            arrastrando = False
        elif tecla == ord("d") and frameActual < len(frames) - 1:
            frameActual = frameActual + 1
            puntos = []
            arrastrando = False
        elif tecla == ord("a") and frameActual > 0:
            frameActual = frameActual - 1
            puntos = []
            arrastrando = False
        elif tecla == ord("c"):
            selecciones[frameActual] = []
            puntos = []
        elif tecla == ord("r"):
            numPuntos = 2
            modoCirculo = False
            puntos = []
        elif tecla == ord("t"):
            numPuntos = 3
            modoCirculo = False
            puntos = []
        elif tecla == ord("f"):
            numPuntos = 4
            modoCirculo = False
            puntos = []
        elif tecla == ord("p"):
            numPuntos = 5
            modoCirculo = False
            puntos = []
        elif tecla == ord("h"):
            numPuntos = 6
            modoCirculo = False
            puntos = []
        elif tecla == ord("o"):
            modoCirculo = True
            puntos = []
        elif tecla == ord("x"):
            if frameActual in selecciones and len(selecciones[frameActual]) > 0:
                selecciones[frameActual].pop()
                if len(selecciones[frameActual]) == 0:
                    del selecciones[frameActual]
        elif tecla == 26:  
            borrarUltimoPunto()
        
    cv2.destroyWindow("Practica 1")
 
def guardarVideo(frames, ruta):
    videoWriter = cv2.VideoWriter(ruta, cv2.VideoWriter_fourcc('X', 'V', 'I', 'D'), fps, size)
    regionesActuales = []                          
    for i in range(len(frames)):
        if i in selecciones:                       
            regionesActuales = selecciones[i]      
        for region in regionesActuales:           
            dibujarPuntos(frames[i], region, (0, 255, 0), True)
        videoWriter.write(frames[i])               
    videoWriter.release()
    print("Video guardado:", ruta)
    
def rectangulo(region):
    if len(region) == 2:
        cx, cy = region[0]
        r = distancia(region[0], region[1])
        return max(cx - r, 0), max(cy - r, 0), min(cx + r, size[0] - 1), min(cy + r, size[1] - 1)
    listaX =[]
    listaY =[]
    for p in region:
        listaX.append(p[0])
        listaY.append(p[1])
    return min(listaX), min(listaY), max(listaX), max(listaY)

def contarRegiones():
    total = 0
    for frame in selecciones:
       if len(selecciones[frame]) > total:
           total = len(selecciones[frame])
    return total
 
def tamanoRegion(numRegion):
    listaAltos = []
    listaAnchos = []
    for frame in selecciones:
        if len(selecciones[frame]) > numRegion:
            x0, y0, x1, y1 = rectangulo(selecciones[frame][numRegion])
            ancho = x1 - x0
            alto = y1 - y0
            listaAltos.append(alto)
            listaAnchos.append(ancho)
    return max(listaAnchos), max(listaAltos)
       
def guardarVideoRegiones(frames, numRegion):
    ruta = "Region - " + str(numRegion + 1) + ".avi"
    ancho, alto = tamanoRegion(numRegion)
    videoWriter = cv2.VideoWriter(ruta, cv2.VideoWriter_fourcc('X', 'V', 'I', 'D'), fps, (ancho, alto))
    
    regionesActuales = []
    for i in range(len(frames)):
        if i in selecciones:
            regionesActuales = selecciones[i]
        
        if len(regionesActuales) > numRegion:
            region = regionesActuales[numRegion]
            x0, y0, x1, y1 = rectangulo(region)
            
            img = numpy.zeros((alto, ancho), dtype=numpy.uint8)
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            
            anchoRecorte = x1 - x0
            altoRecorte = y1 - y0
            
            for fila in range(altoRecorte):
                for columna in range(anchoRecorte):
                    filaOriginal = y0 + fila
                    columnaOriginal = x0 + columna
                    # Círculo: solo copiamos los píxeles de dentro
                    if len(region) == 2 and not dentroCirculo(region, columnaOriginal, filaOriginal):
                        continue
                    pixel = frames[i][filaOriginal, columnaOriginal]   
                    img[fila, columna] = pixel
            videoWriter.write(img)
        
    videoWriter.release()
    print("Video guardado:", ruta)
    
def guardarTodasRegiones(frames):
    for numRegion in range(contarRegiones()):
        guardarVideoRegiones(frames, numRegion)

def guardarVideoOculto(frames, ruta):
    videoWriter = cv2.VideoWriter(ruta, cv2.VideoWriter_fourcc('X', 'V', 'I', 'D'), fps, size)
    regionesActuales = []
    for i in range(len(frames)):
        if i in selecciones:
            regionesActuales = selecciones[i]
        for region in regionesActuales:
            x0, y0, x1, y1 = rectangulo(region)
            for fila in range(y0, y1):
                for columna in range(x0, x1):
                    # Círculo: solo tapamos los píxeles de dentro
                    if len(region) == 2 and not dentroCirculo(region, columna, fila):
                        continue
                    frames[i][fila, columna] = (0, 0, 0)  
        videoWriter.write(frames[i])
    videoWriter.release()
    
def main():
    frames = cargarVideo(VIDEO_RUTA_ENTRADA)
    if frames is not None:
        etiquetarVideo(frames)
        guardarTodasRegiones(frames)
        guardarVideo(frames, VIDEO_RUTA_SALIDA)
        frames = cargarVideo(VIDEO_RUTA_ENTRADA)
        guardarVideoOculto(frames, VIDEO_RUTA_OCULTO)
main()