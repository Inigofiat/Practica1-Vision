import cv2

VIDEO_RUTA_ENTRADA = "Video Práctica.mp4"
VIDEO_RUTA_SALIDA = "Video Práctica Salida.avi"
UMBRAL_DIFERENCIA = 10

frameActual = 0
puntos = []
selecciones = {}

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

def clic(event, x, y, flags, param):
    global puntos
    if event == cv2.EVENT_LBUTTONDOWN:
        puntos.append((x, y))
        print("Punto:", x, y)
        if len(puntos) == 4:
            if frameActual not in selecciones:
                selecciones[frameActual] = []
            selecciones[frameActual].append(puntos)
            print("Region guardada en el frame", frameActual)
            puntos = []

def dibujarPuntos(img, puntos):
    for p in puntos:
        cv2.circle(img, p, 4, (0, 0, 255), -1)        
    for k in range(1, len(puntos)):
        cv2.line(img, puntos[k - 1], puntos[k], (0, 255, 0), 2)   
    if len(puntos) == 4:
        cv2.line(img, puntos[3], puntos[0], (0, 255, 0), 2)       

def mostrarFrame(frames):
   
    vista = cv2.cvtColor(frames[frameActual], cv2.COLOR_BGR2RGB)
    vista = cv2.cvtColor(vista, cv2.COLOR_RGB2BGR)
    if frameActual in selecciones:
        for region in selecciones[frameActual]:
            dibujarPuntos(vista, region)
    dibujarPuntos(vista, puntos)
    cv2.putText(vista, "Frame " + str(frameActual), (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.imshow("Practica 1", vista)
 

def etiquetarVideo(frames):
   
    global frameActual, puntos
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
        elif tecla == ord("d") and frameActual < len(frames) - 1:
            frameActual = frameActual + 1
            puntos = []
        elif tecla == ord("a") and frameActual > 0:
            frameActual = frameActual - 1
            puntos = []
        elif tecla == ord("c"):
            selecciones[frameActual] = []
            puntos = []
    cv2.destroyWindow("Practica 1")
 
 
def guardarVideo(frames, ruta):
    videoWriter = cv2.VideoWriter(ruta, cv2.VideoWriter_fourcc('X', 'V', 'I', 'D'), fps, size)
    regionesActuales = []                          
    for i in range(len(frames)):
        if i in selecciones:                       
            regionesActuales = selecciones[i]      
        for region in regionesActuales:           
            dibujarPuntos(frames[i], region)
        videoWriter.write(frames[i])               
    videoWriter.release()
    print("Video guardado:", ruta)
 
 
frames = cargarVideo(VIDEO_RUTA_ENTRADA)
etiquetarVideo(frames)
guardarVideo(frames, VIDEO_RUTA_SALIDA)
 