import socket
import threading
import time as t
import json
import cv2
import os

image_folder = r'C:\Users\[NombreUsuarioWindows]\Documents\CAM_FRONT' #Ruta donde estarían las imagenes
temporal_output_folder = r'C:\Users\[NombreUsuarioWindows]\Documents\Video Renderizado' #Ruta temporal de las partes del video

mensajes = {
    "CargasDisponibles" : '',
    "MensajeChequeoServidor" : ""
}

def renderizar_parte_video():
    global image_folder,temporal_output_folder #Por si Python no agarra las variables de las rutas
    #Esto es del codigo del profe para captar donde estan las imagenes y sacar sus caracteristicas
    images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
    frame = cv2.imread(os.path.join(image_folder, images[1]))
    height, width, layers = frame.shape
    bandera_renderizado_terminado = False #Bandera que le dira al servidor si ya termino de renderizarse la parte del video
    print("El programa comenzó a recibir paquetes.")
    #Primero recibimos si el servidor tiene cargas o partes disponibles para ser renderizadas
    try:
        message = server_socket.recv(1024).decode(encoding='utf-8')
        mensajes["CargasDisponibles"] = message
    except Exception as e:
        print(f"Error recibiendo las cargas disponibles: '{e}'")
        mensajes["CargasDisponibles"] = False
    #Si hay cargas dispnibles, se mete al while
    while mensajes["CargasDisponibles"]==True:
        print("El servidor tiene una carga disponible")
        try:
            numeroParte = server_socket.recv(1024) # Recibir el numero de la parte que se va a renderizar
            try:
                InicioRangoImagenes = server_socket.recv(1024) # Recibir el primer numero del rango de imagenes que se van a renderizar
                try:
                    FinalRangoImagenes = server_socket.recv(1024) # Recibir el ultimo numero del rango de imagenes que se van a renderizar
                    imagenes = images[InicioRangoImagenes:FinalRangoImagenes] #Definimos el rango de imagenes que se van a renderizar
                    print(f"Las cargas van de la imagen '{InicioRangoImagenes}' hasta la imagen '{FinalRangoImagenes}'")
                    # Se crean variables para poner el nombre del video e inicializarlo
                    parte_video_nombre = os.path.join(temporal_output_folder, f'parte_{numeroParte}.mp4')
                    parte_video_writer = cv2.VideoWriter(parte_video_nombre, cv2.VideoWriter_fourcc(*'mp4v'), 16, (width, height))
                    # Se renderiza cada frame o imagen dentro del video temporal
                    for image in imagenes:
                        frame = cv2.imread(os.path.join(image_folder, image))
                        parte_video_writer.write(frame)
                    parte_video_writer.release() #Como ya se termino de renderizar, soltamos la parte del video temporal
                    bandera_renderizado_terminado = True #Vamos a decirle al servidor que ya acabo
                    #Circuit breaker (Aun falta implementarlo)
                    """if(message == "Server: Ya Terminaste con el indice que te envie?"):
                        print(f"{message}")
                        print("Va a encriptar la bandera de terminado")
                        banderaAcaboJSON = json.dumps(bandera_renderizado_terminado)
                        try:
                            server_socket.send(banderaAcaboJSON.encode())  # Enviamos la bandera
                            print("Se envio la bandera 'bandera_renderizado_terminado' al servidor")
                        except Exception as e:
                            print(f"Error enviando bandera 'bandera_renderizado_terminado': '{e}'")
                            break"""
                except Exception as e:
                    print(f"Error recibiendo la parte final del rango de imagenes a renderizar: '{e}'")
                    break
            except Exception as e:
                print(f"Error recibiendo la parte inicial del rango de imagenes a renderizar: '{e}'")
                break
        except Exception as e:
            print(f"Error recibiendo el numero de la parte que se va a renderizar: '{e}'")
            break
        #Se notifica al cliente que ya esta terminando su ciclo
        print("Ya terminaste con tu parte para renderizar del video.")
        print("Se verificará si hay mas partes por renderizar.")
        try:
            message = server_socket.recv(1024).decode(encoding='utf-8')
            mensajes["CargasDisponibles"] = message
        except Exception as e:
            print(f"Error recibiendo las cargas disponibles: '{e}'")
            mensajes["CargasDisponibles"] = False
            #break
    print("No hay mas partes del video por renderizar por lo que se cerrará el nodo.")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.connect(('127.0.0.1', 5000)) #Local
#client_socket.connect(('192.168.137.1', 5000)) #Direccion del profe

nodo_renderizado = threading.Thread(target=renderizar_parte_video)
nodo_renderizado.start()
