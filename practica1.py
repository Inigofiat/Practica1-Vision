import cv2
import numpy as np

VIDEO_RUTA_ENTRADA = "Video Práctica.mp4"
VIDEO_RUTA_SALIDA = "Video Práctica Salida.avi"
UMBRAL_DIFERENCIA = 10

frameActual = 0
puntos = []
selecciones = {}
modoDibujo = "rectangulo"

# Variables para dibujar círculos manualmente
centroCirculo = None
radioCirculo = 0
arrastrando = False


def cargarVideo(ruta):
    global fps, size

    videoCapture = cv2.VideoCapture(ruta)
    fps = videoCapture.get(cv2.CAP_PROP_FPS)

    size = (
        int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)),
        int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    )

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
            total += cambio
            contador += 1

    return total / contador


def saltarFrames(frames, actual):
    for i in range(actual + 1, len(frames)):
        if diferenciaFrames(frames[actual], frames[i]) > UMBRAL_DIFERENCIA:
            return i

    return len(frames) - 1


def clic(event, x, y, flags, param):
    global puntos, centroCirculo, radioCirculo, arrastrando

    # MODO RECTÁNGULO
    if modoDibujo == "rectangulo":

        if event == cv2.EVENT_LBUTTONDOWN:
            puntos.append((x, y))
            print("Punto:", x, y)

            if len(puntos) == 4:
                if frameActual not in selecciones:
                    selecciones[frameActual] = []

                region = {
                    "tipo": "rectangulo",
                    "puntos": puntos.copy()
                }

                selecciones[frameActual].append(region)

                print("Rectángulo guardado en frame", frameActual)
                puntos = []

    # MODO CÍRCULO
    elif modoDibujo == "circulo":

        # Pulsar el botón: establecer el centro
        if event == cv2.EVENT_LBUTTONDOWN:
            centroCirculo = (x, y)
            radioCirculo = 0
            arrastrando = True

        # Mover el ratón mientras se mantiene pulsado
        elif event == cv2.EVENT_MOUSEMOVE and arrastrando:
            radioCirculo = int(
                np.hypot(
                    x - centroCirculo[0],
                    y - centroCirculo[1]
                )
            )

        # Soltar el botón: guardar el círculo
        elif event == cv2.EVENT_LBUTTONUP and arrastrando:
            radioCirculo = int(
                np.hypot(
                    x - centroCirculo[0],
                    y - centroCirculo[1]
                )
            )

            if radioCirculo > 0:
                if frameActual not in selecciones:
                    selecciones[frameActual] = []

                region = {
                    "tipo": "circulo",
                    "centro": centroCirculo,
                    "radio": radioCirculo
                }

                selecciones[frameActual].append(region)

                print("Círculo guardado en frame", frameActual)

            centroCirculo = None
            radioCirculo = 0
            arrastrando = False


def dibujarRegion(img, region):
    if region["tipo"] == "rectangulo":
        puntosRegion = region["puntos"]

        for p in puntosRegion:
            cv2.circle(img, p, 4, (0, 0, 255), -1)

        for k in range(1, len(puntosRegion)):
            cv2.line(
                img,
                puntosRegion[k - 1],
                puntosRegion[k],
                (0, 255, 0),
                2
            )

        cv2.line(
            img,
            puntosRegion[3],
            puntosRegion[0],
            (0, 255, 0),
            2
        )

    elif region["tipo"] == "circulo":
        cv2.circle(
            img,
            region["centro"],
            region["radio"],
            (255, 0, 0),
            2
        )


def mostrarFrame(frames):
    vista = frames[frameActual].copy()

    # Dibujar regiones guardadas
    if frameActual in selecciones:
        for region in selecciones[frameActual]:
            dibujarRegion(vista, region)

    # Mostrar el rectángulo mientras se seleccionan sus puntos
    if modoDibujo == "rectangulo":
        for p in puntos:
            cv2.circle(vista, p, 4, (0, 0, 255), -1)

        for k in range(1, len(puntos)):
            cv2.line(
                vista, puntos[k - 1], puntos[k],
                (0, 255, 0), 2
            )

        if len(puntos) == 4:
            cv2.line(
                vista, puntos[3], puntos[0],
                (0, 255, 0), 2
            )

    # Mostrar el círculo mientras se arrastra el ratón
    elif modoDibujo == "circulo" and arrastrando:
        cv2.circle(
            vista,
            centroCirculo,
            radioCirculo,
            (255, 0, 0),
            2
        )

        cv2.circle(
            vista,
            centroCirculo,
            3,
            (0, 0, 255),
            -1
        )

    cv2.putText(
        vista,
        "Frame: " + str(frameActual),
        (10, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    textoModo = (
        "Modo: RECTANGULO (1)"
        if modoDibujo == "rectangulo"
        else "Modo: CIRCULO (2) - Arrastra el raton"
    )

    cv2.putText(
        vista,
        textoModo,
        (10, 55),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 255),
        2
    )

    cv2.imshow("Practica 1", vista)


def etiquetarVideo(frames):
    global frameActual, puntos, modoDibujo
    global centroCirculo, radioCirculo, arrastrando

    cv2.namedWindow("Practica 1")
    cv2.setMouseCallback("Practica 1", clic)

    while True:
        mostrarFrame(frames)
        tecla = cv2.waitKey(20) & 0xFF

        if tecla == ord("q"):
            break

        # Activar modo rectángulo
        elif tecla == ord("1"):
            modoDibujo = "rectangulo"
            puntos = []
            centroCirculo = None
            radioCirculo = 0
            arrastrando = False

        # Activar modo círculo
        elif tecla == ord("2"):
            modoDibujo = "circulo"
            puntos = []
            centroCirculo = None
            radioCirculo = 0
            arrastrando = False

        # Saltar al siguiente cambio de escena
        elif tecla == ord("s") and frameActual < len(frames) - 1:
            frameActual = saltarFrames(frames, frameActual)
            puntos = []
            centroCirculo = None
            arrastrando = False

        # Avanzar un frame
        elif tecla == ord("d") and frameActual < len(frames) - 1:
            frameActual += 1
            puntos = []
            centroCirculo = None
            arrastrando = False

        # Retroceder un frame
        elif tecla == ord("a") and frameActual > 0:
            frameActual -= 1
            puntos = []
            centroCirculo = None
            arrastrando = False

        # Borrar regiones del frame actual
        elif tecla == ord("c"):
            selecciones[frameActual] = []
            puntos = []
            centroCirculo = None
            radioCirculo = 0
            arrastrando = False

    cv2.destroyWindow("Practica 1")


def guardarVideo(frames, ruta):
    videoWriter = cv2.VideoWriter(
        ruta,
        cv2.VideoWriter_fourcc('X', 'V', 'I', 'D'),
        fps,
        size
    )

    regionesActuales = []

    for i in range(len(frames)):
        if i in selecciones:
            regionesActuales = selecciones[i]

        # Copiar el frame para no modificar el original
        frameSalida = frames[i].copy()

        for region in regionesActuales:
            dibujarRegion(frameSalida, region)

        videoWriter.write(frameSalida)

    videoWriter.release()
    print("Video guardado:", ruta)


frames = cargarVideo(VIDEO_RUTA_ENTRADA)

if frames is not None:
    etiquetarVideo(frames)
    guardarVideo(frames, VIDEO_RUTA_SALIDA)