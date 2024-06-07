import socket
import threading
import os
import cv2
import json

numDivisiones = 8 #Nuestro numero de Batch's o partes

def obtener_archivos_de_imagen(carpeta_de_imagenes):
    #Obtiene una lista de archivos de imagen en una carpeta.
    imagenes = [img for img in os.listdir(carpeta_de_imagenes) if img.endswith(".jpg")]
    if not imagenes:
        print("No se encontraron imágenes en el directorio.")
        return []
    return imagenes

#Lo puse afuera para hacerlo mas facilmente manejable
carpeta_de_imagenes_global = r'H:\Mi unidad\Tarea5SD\ImagenesVideo' #Ruta del Google Drive donde estarian las imagenes
imagenes_global = obtener_archivos_de_imagen(carpeta_de_imagenes_global)
longitudPorDivision_global = int(len(imagenes_global)/numDivisiones)
residuoDivision_global = len(imagenes_global)%numDivisiones
#conjuntos_de_imagenes_global = {str(i): {'Estado': 'A', 'Imagenes': [os.path.join(carpeta_de_imagenes_global, img) for img in imagenes_global[i:i+longitudPorDivision_global]]} for i in range(0, len(imagenes_global), longitudPorDivision_global)}
conjuntos_de_imagenes_global = {str(i): {'Estado': 'A', 'Imagenes': [os.path.join(carpeta_de_imagenes_global, img) for img in imagenes_global[i:i+longitudPorDivision_global]]} for i in range(numDivisiones)}

""" 
#Lo comente porque me parecia mas facil hacer estas variables de forma global
#Version del Emiliano
def preparar_conjuntos_de_imagenes(carpeta_de_imagenes):
    #Prepara los conjuntos de imágenes a partir de archivos en la carpeta
    imagenes = obtener_archivos_de_imagen(carpeta_de_imagenes)
    longitudPorDivision = int(len(imagenes)/numDivisiones)
    residuoDivision = len(imagenes)%numDivisiones
    conjuntos_de_imagenes = {str(i): {'Estado': 'A', 'Imagenes': [os.path.join(carpeta_de_imagenes, img) for img in imagenes[i:i+longitudPorDivision]]} for i in range(0, len(imagenes), longitudPorDivision)}
    return conjuntos_de_imagenes
"""

def renderizar_video(carpeta_de_salida):
    global conjuntos_de_imagenes_global
    nombre_video = os.path.join(carpeta_de_salida, 'Video_Completo.mp4')
    print(f"La ruta del video completo es: '{nombre_video}'")
    print(f"La primer imagen es: {conjuntos_de_imagenes_global['0']['Imagenes'][0]}")
    primera_imagen_path = conjuntos_de_imagenes_global['0']['Imagenes'][0]
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
    print("Se va a empezar a juntar las partes del video en uno solo")
    # Combine all parts into the final video
    for i in range(numDivisiones):
        parte_video_nombre = os.path.join(carpeta_de_salida, f'video_{i}.mp4')
        
        # Open the part video
        cap = cv2.VideoCapture(parte_video_nombre)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            video.write(frame)
    
        cap.release()
    # Release the video writer object and close any open windows
    video.release()
    cv2.destroyAllWindows()
    print("Se termino de renderizar el video completo")
    # Remove temporary part videos
    for i in range(numDivisiones):
        parte_video_nombre = os.path.join(carpeta_de_salida, f'video_{i}.mp4')
        try:
            os.remove(parte_video_nombre)
        except PermissionError as e:
            print(f"Error borrando el video '{parte_video_nombre}': {e}")
    print("Se removieron los videos temporales")
    print(f"Video renderizado: {nombre_video}")
    return True

def manejar_cliente(conjuntos_de_imagenes, carpeta_de_salida, conn, addr, conexiones_activas, finalizacion_evento): #Embajador con intento para terminar el servidor
#def manejar_cliente(conjuntos_de_imagenes, carpeta_de_salida, conn, addr, conexiones_activas): #Embajador sin evento para terminar el servidor
    print(f"Nueva conexión: {addr}")
    while True:
        conjunto_disponible = s0(conjuntos_de_imagenes, conn, addr)
        if conjunto_disponible is not None:
            token = s1(conjuntos_de_imagenes, conn, addr, conjunto_disponible)
            if token is not None:
                if not s2(conjuntos_de_imagenes, carpeta_de_salida, conn, addr, conjunto_disponible, conexiones_activas):
                    break
        else:
            print("Se va a cerrar la conexion")
            #Debido a que el cliente tiene que decodificar un JSON, tube que convertir el mensaje de si hay o no cargas en un JSON tambien
            datos = {
                "mensaje": "No hay cargas disponibles"
            }
            mensaje_json = json.dumps(datos)
            conn.send(mensaje_json.encode('utf-8'))
            break
    print("Se salio del while de las conexiones")
    conn.close()
    conexiones_activas.remove(conn)
    print("Se va a meter al if a revisar si todos los conjuntos tienen estados 'D'")
    print(f"Las conexiones activas son: '{conexiones_activas}'.")
    #print(f"Las conexiones activas son: '{conexiones_activas}', y los valores dentro del diccionario son: '{conjunto_disponible.values()}'")
    print(f"Mientras que las llaves dentro del diccionario 'conjuntos_de_imagenes' son: '{conjuntos_de_imagenes.keys()}'")
    print(f"Mientras que las llaves dentro del diccionario son: '{conjuntos_de_imagenes.keys()}'")
    print(f"Mientras que las llaves dentro del diccionario[0] son: '{conjuntos_de_imagenes['0'].keys()}'")
    #print(f"Mientras que los valores dentro del diccionario[0] son: '{conjuntos_de_imagenes['0'].values()}'")
    print(f"Mientras que el valor dentro del diccionario[0]['Estado'] es: '{conjuntos_de_imagenes['0']['Estado']}'")
    print(f"Mientras que los valores dentro del diccionario 'conjunto_disponible' son: '{conjunto_disponible}'")
    #if len(conexiones_activas) == 0 and all(conjunto['Estado'] == 'C' for conjunto in conjuntos_de_imagenes.values()):
    if len(conexiones_activas) == 0 and conjunto_disponible == None:
        print("Se va a meter a renderizar el video completo")
        renderizado_completo = renderizar_video(carpeta_de_salida)
        if renderizado_completo == True:
            print("Se metio al if de renderizado_completo")
            finalizacion_evento.set()

def s0(conjuntos_de_imagenes, conn, addr):
    print(f"S0: Buscando nodos disponibles para {addr}")
    for id_conjunto, info_conjunto in conjuntos_de_imagenes.items():
        if info_conjunto['Estado'] == 'A':
            return id_conjunto
    print("No hay nodos disponibles.")
    return None

def s1(conjuntos_de_imagenes, conn, addr, id_conjunto):
    print(f"S1: Nodo disponible encontrado para {addr}. El ID del conjunto es: {id_conjunto}")
    conjuntos_de_imagenes[id_conjunto]['Estado'] = 'B'
    return f"token_{id_conjunto}"

"""
#Version del Emiliano
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
"""
#def s2(conjuntos_de_imagenes, carpeta_de_salida, conn, addr, id_conjunto, token, conexiones_activas):
def s2(conjuntos_de_imagenes, carpeta_de_salida, conn, addr, id_conjunto, conexiones_activas):
    print(f"S2: Generando renderización para {addr}. ID de conjunto: {id_conjunto}")
    rutas_de_imagenes = conjuntos_de_imagenes[id_conjunto]['Imagenes']
    nombre_video = os.path.join(carpeta_de_salida, f"video_{id_conjunto}.mp4")
    #inicio_rango = int(id_conjunto) * len(rutas_de_imagenes)
    #final_rango = inicio_rango + len(rutas_de_imagenes)
    if int(id_conjunto)==0:
        print("Esta es la 1ra Carga")
        inicio_rango = 0
        final_rango = inicio_rango + len(rutas_de_imagenes)
        print(f"Las cargas van de la imagen '{inicio_rango}' hasta la imagen '{final_rango}'")
    elif int(id_conjunto)==numDivisiones-1:
        print("Esta es la ultima carga")
        inicio_rango = int(id_conjunto) * longitudPorDivision_global + 1
        final_rango = (inicio_rango) + len(rutas_de_imagenes) + residuoDivision_global
        print(f"Las cargas van de la imagen '{inicio_rango}' hasta la imagen '{final_rango}'")
    else:
        inicio_rango = int(id_conjunto) * longitudPorDivision_global + 1
        final_rango = (inicio_rango-1) + len(rutas_de_imagenes)
        print(f"Las cargas van de la imagen '{inicio_rango}' hasta la imagen '{final_rango}'")
    """#print(f"El id del conjunto es: '{}'")
    conn.send("Hay cargas disponibles".encode('utf-8'))
    print("Se envio la disponibilidad de las cargas al nodo")
    conn.send(id_conjunto.encode('utf-8'))
    print(f"Se envio el ID del conjunto: '{id_conjunto}'")
    conn.send(str(inicio_rango).encode('utf-8'))
    print(f"Se envio el inicio del rango: '{inicio_rango}'")
    conn.send(str(final_rango).encode('utf-8'))
    print(f"Se envio el final del rango: '{final_rango}'")"""
    # Crear un diccionario con todos los datos
    datos = {
        "mensaje": "Hay cargas disponibles",
        "id_conjunto": id_conjunto,
        "inicio_rango": inicio_rango,
        "final_rango": final_rango
    }
    # Convertir el diccionario a JSON
    mensaje_json = json.dumps(datos)
    # Enviar el JSON al cliente
    conn.send(mensaje_json.encode('utf-8'))
    print(f"Se enviaron los datos: {datos}")

    termino = bool(conn.recv(1024).decode('utf-8'))
    if termino == True:
        conjuntos_de_imagenes[id_conjunto]['Estado'] = 'C'
        #conn.close()
        print(f"Video recibido y guardado como: {nombre_video}")
        #manejar_cliente(conjuntos_de_imagenes, carpeta_de_salida, conn, addr, conexiones_activas)
        return True
    else:
        #conn.close()
        print(f"El video no fue recibido")
        conn.send("Error".encode('utf-8'))
        return False

"""
def s3(conjuntos_de_imagenes, conn, addr, id_conjunto, nombre_video):
    print(f"S3: Enviando video a {addr}. ID de conjunto: {id_conjunto}")
    with open(nombre_video, 'rb') as f:
        datos_video = f.read()
    conn.sendall(str(len(datos_video)).encode('utf-8').rjust(10))
    conn.sendall(datos_video)
    conjuntos_de_imagenes[id_conjunto]['Estado'] = 'D'
    conn.close()
"""

def iniciar_servidor(carpeta_de_imagenes, carpeta_de_salida, host='localhost', puerto=5555):
    #conjuntos_de_imagenes = preparar_conjuntos_de_imagenes(carpeta_de_imagenes)
    conexiones_activas = set()
    global conjuntos_de_imagenes_global 
    conjuntos_de_imagenes = conjuntos_de_imagenes_global #Como creo que vamos a usarla de diferentes formas lo capto de uno original
    finalizacion_evento = threading.Event() #Esto se supone que es para poder terminar el programa
    #print(f"Estas son las llaves del diccionario: '{conjuntos_de_imagenes.keys()}'")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, puerto))
        s.listen()
        print(f"Servidor escuchando en {host}:{puerto}")

        #while True:
        while not finalizacion_evento.is_set():
            conn, addr = s.accept()
            conexiones_activas.add(conn)
            #threading.Thread(target=manejar_cliente, args=(conjuntos_de_imagenes, carpeta_de_salida, conn, addr, conexiones_activas)).start()
            threading.Thread(target=manejar_cliente, args=(conjuntos_de_imagenes, carpeta_de_salida, conn, addr, conexiones_activas, finalizacion_evento)).start()
        print("El servidor ha terminado correctamente.") #Se deberia imprimir cuando finalice el servidor

if __name__ == "__main__":
    #carpeta_de_imagenes = r'C:\Users\emi13\ClaeSD\CAM_FRONT' #Ruta predeterminada de las imagenes
    #carpeta_de_salida = r'C:\Users\emi13\ClaeSD' #Ruta del video renderizado predeterminada
    #carpeta_de_imagenes = r'C:\Users\[UsuarioWindows]\Documents\CAM_FRONT' #Ruta local donde estarian las imagenes
    #carpeta_de_salida = r'C:\Users\[UsuarioWindows]\Documents\Video Renderizado' #Ruta local donde se almacenaria el video y sus partes temporales
    carpeta_de_imagenes = r'H:\Mi unidad\Tarea5SD\ImagenesVideo' #Ruta del Google Drive donde estarian las imagenes
    carpeta_de_salida = r'H:\Mi unidad\Tarea5SD\Video' #Ruta del Google Drive donde se almacenaria el video y sus partes temporales
    iniciar_servidor(carpeta_de_imagenes, carpeta_de_salida)