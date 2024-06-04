import socket
import threading
import numpy as np

# Lista para guardar los sockets de los clientes conectados
nodos = {}
#nodos[contador_nodos] = {
#   'Dir': addr,
#   'Sock': socket,
#   'Disponibilidad': 'D'
#}
#Variable que se usa en la funcion agregarNodo, es clave del diccionario nodos
contador_nodos = 0
#Almacena todas las palabras
dic = {}
lista1 = []
#almacena todos los batches
batches = {}
contadorBatch = 0
#almacena la clave y le asigna un valor
estado = {}
cargaDisponible = True
nodoDisponible = True

#Inicializamos el EMB
def Embajador():
    server_socket = socket.socket(
        socket.AF_INET,     # Especifica la familia direcciones, como la IPV4
        socket.SOCK_STREAM  # Este argumento especifica que se usará el 
                            # protocolo TCP (Transmission Control Protocol) 
                            # como medio de comunicación
    )
    server_socket.bind(('localhost', 8080))
    server_socket.listen(4)
    
    #Init se inializa en 0, porque dentro de de la funcion cargaDis en
    #caso de detectar nuevos nodos por primera vez, se ejecuta la funcion
    #bucarNodos.
    init = 0
    
    while cargaDis():
        # Nuevos Nodos
        if init == 0:
            busqueda_thread = threading.Thread(
                target = buscarNodos, 
                args   = (server_socket)
            )
            # Se inicia la ejecución del hilo con el método start()
            busqueda_thread.start()
            
            #Al hacer que init sea 1, evitamos que entre en este bloque de codigo, ya que
            #ya cumplio su funcion de inicializar la busqueda.
            init = 1

        #Si la funcion nodosDis es verdadera se ejecuta.
        if nodosDis():
            id = buscarNodosDis()
            
            if id != -1:
                nodos_thread = threading.Thread(
                    target = Circuit_Breaker, 
                    args   = (id)
                )
                # Se inicia la ejecución del hilo con el método start()
                nodos_thread.start()
        
        if cargaError():
            pass

def cargaDis(estado):
    #Si es el valor de A se encuentra en la lista regresa verdadero
    return True if "A" in list(estado.values()) else False

def buscarNodos(server_socket):
    while True:
        random_id = np.random.randint(1000, 9999)
        # Se acepta un nuevo socket con el método accept, el cual regresa
        # dos argumentos, el objeto socket del cliente y la dirección de
        # este
        client_socket, addr = server_socket.accept()
        print(f"Connection established with {addr}")
        # Se agrega el nuevo cliente a la lista de clientes
        
        agregarNodo(client_socket, addr)
        
        if not cargaDis():
            break

def nodosDis():
    for nodo in nodos:
        if nodos[nodo]['Disponibilidad'] == 'D':
            return True
    
    return False

def buscarNodosDis():
    for nodo in nodos:
        if nodos[nodo]['Disponibilidad'] == 'D':
            return nodo
    
    return -1

def Circuit_Breaker(nodo_id):

    if x:
        s0()
    elif:
        s1()
        

def s0():
    while ...

def s1():
    if x:
        s0()
    return

#Agregamos un nuevo nodo
def agregarNodo(socket, addr):
    nodos[contador_nodos] = {
            'Dir': addr,
            'Sock': socket,
            'Disponibilidad': 'D' #D: Disponible
        } #damos por hecho, al agregar un nuevo nodo este, esta disponible
    contador_nodos += 1

#Cambio el estado del nodo, de Disponible a ocupado, o algo similar, pero
#necesito agregar un otra variable que tenga encuenta los diferentes estados
#del nodo, ya que, la variable estado es usada para almacenar el estado de 
#los batchs de trabajo
def estatusNodo(id,estado):
    nodos[id]['Disponibilidad'] = estado

#en caso de haber algun error o desconeccion, pasamos el id, y lo borramos
#de nuestro diccionario nodos
def eliminarNodo(id):
    nodos.pop(id)

# Directiva main para iniciar el servidor
if __name__ == "__main__":
    # Se ejecuta el método del servidor
    Embajador()