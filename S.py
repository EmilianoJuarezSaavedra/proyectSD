import socket
import threading
import os
import cv2

def obtener_archivos_de_imagen(carpeta_de_imagenes):
    """Obtiene una lista de archivos de imagen en una carpeta."""
    imagenes = [img for img in os.listdir(carpeta_de_imagenes) if img.endswith(".jpg")]
    if not imagenes:
        print("No se encontraron imágenes en el directorio.")
        return []
    return imagenes

def preparar_conjuntos_de_imagenes(carpeta_de_imagenes):
    #Prepara los conjuntos de imágenes a partir de archivos en la carpeta
    imagenes = obtener_archivos_de_imagen(carpeta_de_imagenes)
    conjuntos_de_imagenes = {str(i): {'Estado': 'A', 'Imagenes': [os.path.join(carpeta_de_imagenes, img) for img in imagenes[i:i+10]]} for i in range(0, len(imagenes), 10)}
    return conjuntos_de_imagenes

def renderizar_video(image_folder, rutas_de_imagenes, nombre_video):
    """Renderiza un video a partir de una lista de imágenes."""
    if not rutas_de_imagenes:
        print("No hay rutas de imágenes proporcionadas.")
        return False

    # Lee la primera imagen para obtener sus dimensiones
    primera_imagen_path = rutas_de_imagenes[0]
    frame = cv2.imread(primera_imagen_path)
    if frame is None:
        print(f"Error al leer la primera imagen: {primera_imagen_path}")
        return False
    altura, ancho, capas = frame.shape

    # Inicializa el objeto de escritura de video
    video = cv2.VideoWriter(nombre_video, cv2.VideoWriter_fourcc(*'mp4v'), 16, (ancho, altura))
    if not video.isOpened():
        print(f"Error al crear el archivo de video: {nombre_video}")
        return False

    print("Se va a renderizar el video")
    for imagen_path in rutas_de_imagenes:
        print(f"Procesando imagen: {imagen_path}")
        frame = cv2.imread(imagen_path)
        if frame is None:
            print(f"Error al leer la imagen: {imagen_path}, saltando esta imagen.")
            continue
        video.write(frame)

    # Libera el objeto de escritura de video y cierra cualquier ventana abierta
    video.release()
    cv2.destroyAllWindows()
    print(f"Video renderizado: {nombre_video}")
    return True

def manejar_cliente(conjuntos_de_imagenes, carpeta_de_salida, conn, addr):
    print(f"Nueva conexión: {addr}")
    conjunto_disponible = s0(conjuntos_de_imagenes, conn, addr)
    if conjunto_disponible is not None:
        token = s1(conjuntos_de_imagenes, conn, addr, conjunto_disponible)
        if token is not None:
            s2(conjuntos_de_imagenes, carpeta_de_salida, conn, addr, conjunto_disponible, token)
    else:
        conn.close()

def s0(conjuntos_de_imagenes, conn, addr):
    print(f"S0: Buscando nodos disponibles para {addr}")
    for id_conjunto, info_conjunto in conjuntos_de_imagenes.items():
        if info_conjunto['Estado'] == 'A':
            return id_conjunto
    print("No hay nodos disponibles.")
    return None

def s1(conjuntos_de_imagenes, conn, addr, id_conjunto):
    print(f"S1: Nodo disponible encontrado para {addr}. ID de conjunto: {id_conjunto}")
    conjuntos_de_imagenes[id_conjunto]['Estado'] = 'B'
    return f"token_{id_conjunto}"

def s2(conjuntos_de_imagenes, carpeta_de_salida, conn, addr, id_conjunto, token):
    print(f"S2: Generando renderización para {addr}. ID de conjunto: {id_conjunto}")
    rutas_de_imagenes = conjuntos_de_imagenes[id_conjunto]['Imagenes']
    nombre_video = os.path.join(carpeta_de_salida, f"video_{id_conjunto}.mp4")
    exito = renderizar_video(carpeta_de_imagenes, rutas_de_imagenes, nombre_video)
    if exito:
        s3(conjuntos_de_imagenes, conn, addr, id_conjunto, nombre_video)
    else:
        print(f"Error en renderización para {addr}. Reintentando...")
        conjuntos_de_imagenes[id_conjunto]['Estado'] = 'A'
        manejar_cliente(conjuntos_de_imagenes, carpeta_de_salida, conn, addr)

def s3(conjuntos_de_imagenes, conn, addr, id_conjunto, nombre_video):
    print(f"S3: Enviando video a {addr}. ID de conjunto: {id_conjunto}")
    with open(nombre_video, 'rb') as f:
        datos_video = f.read()
    conn.sendall(str(len(datos_video)).encode('utf-8').rjust(10))
    conn.sendall(datos_video)
    conjuntos_de_imagenes[id_conjunto]['Estado'] = 'D'
    conn.close()

def iniciar_servidor(carpeta_de_imagenes, carpeta_de_salida, host='localhost', puerto=5555):
    conjuntos_de_imagenes = preparar_conjuntos_de_imagenes(carpeta_de_imagenes)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, puerto))
        s.listen()
        print(f"Servidor escuchando en {host}:{puerto}")

        while True:
            conn, addr = s.accept()
            threading.Thread(target=manejar_cliente, args=(conjuntos_de_imagenes, carpeta_de_salida, conn, addr)).start()

if __name__ == "__main__":
    carpeta_de_imagenes = r'C:\Users\emi13\ClaeSD\CAM_FRONT'
    carpeta_de_salida = r'C:\Users\emi13\ClaeSD'
    iniciar_servidor(carpeta_de_imagenes, carpeta_de_salida)

