import requests  ## es el cartero donde enviamos mensajes a través de internet 
import json ## traductor pq blockchain entiende JSON pero no codigo 
import os ## 
import psycopg2 
import time 

# Tu punto de acceso a la blockchain. Reemplaza esto con tu URL HTTP de Alchemy.
## dirección exacta del servidor 


ALCHEMY_URL = os.getenv("ALCHEMY_API")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT")



def enviar_alerta(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, # A quién se lo envía
        "text": mensaje              # Qué texto dirá
    }
    requests.post(url, json=payload) # El cartero lleva el paquete




def obtener_ultimo_bloque(): 

    payload = {
    "jsonrpc": "2.0", ##en que idioma le hablaremos 
    "id": 1, ##el numero de mi pregunta, si envio 100 ya se que numero es cada pregunta 
    "method": "eth_blockNumber", #el metodo para obtener solo el numero de la ultima hoja del ETH 
    "params": []}

    response = requests.post(ALCHEMY_URL, json=payload) 
    data = response.json()
    valor_requerido = data["result"]
    valor_normal = int(valor_requerido,16)
    return valor_normal


while True:
    try:
        print("Attempting to connect to the database...")
        conexion = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )


# The cursor is the messenger that carries our SQL commands to the database
        cursor = conexion.cursor()
        print ("CONEXIÓN EXITOSA")
        enviar_alerta("🟢 Radar encendido en AWS y vigilando bloques.")
        break

    except psycopg2.OperationalError as e:
        print("Database is still waking up. Waiting 3 seconds...")
        time.sleep(3)

def extraer_bloque (numero_bloque):
    hex_bloque = hex(numero_bloque)
    payloadV3 = {
    "jsonrpc": "2.0", ##en que idioma le hablaremos 
    "id": 2, ##el numero de mi pregunta, si envio 100 ya se que numero es cada pregunta 
    "method": "eth_getBlockByNumber", #el metodo para obtener toda la infor de la transaccion 
    "params": [hex_bloque, True]     ##el primer parametro es para saber el bloque, el true es para que descargue las transacciones 
} 

    responsev3 = requests.post(ALCHEMY_URL, json=payloadV3) 
    datav3 = responsev3.json() 
    transactions_listv2 = datav3["result"]["transactions"]


    datos_limpiosv2 = []

    for txv2 in transactions_listv2:
        montov2 = int(txv2["value"],16)
        monto_realv2 = montov2/10**18
        depositantev2 = txv2["from"]
        recibidorv2 = txv2 ["to"]
        pkv2 = txv2["hash"]

        if monto_realv2 > 30:
            tx_limpiav2 = {"pk": pkv2, "de": depositantev2, "para": recibidorv2, "valor": monto_realv2}
            datos_limpiosv2.append(tx_limpiav2)

            try:
                cursor.execute("INSERT INTO eth_whales (hash,de, para, monto_real) VALUES  (%s,%s, %s, %s)", (pkv2,depositantev2, recibidorv2, monto_realv2))
                ## &S --> sirve para reusabilidad y no escribir 50 veces si encuentro 50 ballenas placeholder/marcador de posicion
                if monto_realv2 > 1000:
                    enviar_alerta(f" Megaballena: {monto_realv2} ETH | Hash: {pkv2}")
                
            except Exception as e:
                print (f"Ballena duplicada ignorada. Detalle:{e}")
    carpeta_destino = "./"
    nombre_archivo = f"transacciones_bloque_{numero_bloque}.json"
    ruta_completa = carpeta_destino + nombre_archivo 
    with open(ruta_completa, 'w') as archivov2: ##la letra w es para write, para agregar seria append 'a' 
        json.dump(datos_limpiosv2, archivov2) 


def descargar_rango(inicio, fin):
    for numero_actual in range(inicio, fin):
        extraer_bloque(numero_actual) 



try:
    while True:
    # Paso 1: Usar el radar
        bloque_actual = obtener_ultimo_bloque()
        print(f" Escaneando la red... Bloque actual descubierto: {bloque_actual}")
    
    # Paso 2: Usar la fábrica
        extraer_bloque(bloque_actual)

        conexion.commit()
        print(" Datos guardados en PostgreSQL.")
    
    # Paso 3: Control de ritmo
        print(" Esperando 12 segundos para el siguiente bloque...\n")
        time.sleep(12)

        # Aquí va todo tu bloque del radar y la fábrica
except KeyboardInterrupt:
    print("\nFreno de emergencia activado. Deteniendo el radar...")
    
finally:
    # Esto se ejecutará siempre al final
    cursor.close()
    conexion.close()
    print("Conexiones a la base de datos cerradas de forma segura. ¡Adiós!")




#Damos guardar al borrador 



## para automatizar hay 3 pilares 
## Descubrimiento dinamica - Script pregunta a la red ¿Cuál es el bloque más reciente en este momento? 
## Bucle Infinito - Necesario para que pregunte si quen yo lo haga 
## Control del ritmo (rancing) - Eth hace un bloque cada 12 seg, no puedo hacer mil consultas por seg. Debo "dormir" cierto tiempo 