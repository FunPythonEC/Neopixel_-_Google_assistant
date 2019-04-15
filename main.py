import machine
import network
import time
from umqtt.robust import MQTTClient
import os
import sys

ledr = machine.Pin(12, machine.Pin.OUT)
ledg = machine.Pin(22, machine.Pin.OUT)
ledb = machine.Pin(23, machine.Pin.OUT)

#RECIBIR EL DATO DEL SERVIDOR PARA ENCENDER LOS pines
#########################
# la siguiente función es la devolución de llamada que es
# llamada cuando se reciben los datos suscritos
def cb(topic, msg):
    print((msg))    

#########################

#color rojo
    if msg == b"7":
        #mientras el rojo esta encendido los otros se apagan
        ledr.on() 
        ledg.off() 
        ledb.off()
        print ("luz roja encedida")

    if msg == b"#ff0000":
        ledr.on() 
        ledg.off() 
        ledb.off()
        print ("luz roja encedida")
    	
#color verde
    if msg == b'2':
        #mientras el verde esta encendido los otros se apagan
        ledr.off() 
        ledg.on() 
        ledb.off()
        print ("led verde encendida")

    if msg == b"#00ff00":
        ledr.off() 
        ledg.on() 
        ledb.off()
	    
#color azul
    if msg == b'3':
        #mientras el azul esta encendido los otros se apagan
        ledr.off() 
        ledg.off() 
        ledb.on() 
        print ("led azul encendida")

    if msg == b"#0000ff":
        ledr.off() 
        ledg.off() 
        ledb.on()

#color amarillo
    if msg == b"4":
        #mientras el amrillo esta encendido los otros se apagan
        #de esa forma solo se ve el color que le indicamos al asistente de google
        ledr.on() 
        ledg.on() 
        ledb.off()
        print ("luz amarilla encedida")

    if msg == b"#ffff00":
        ledr.on() 
        ledg.on() 
        ledb.off()

#color rosado
    if msg == b"5":
        #mientras el rosado esta encendido los otros se apagan
        #de esa forma solo se ve el color que le indicamos al asistente de google
        ledr.on() 
        ledg.off() 
        ledb.on()
        print ("luz rosada encedida")

    if msg == b"#ff00ff":
        ledr.on() 
        ledg.off() 
        ledb.on()

#color celeste
    if msg == b"6":
        #mientras el celeste esta encendido los otros se apagan
        #de esa forma solo se ve el color que le indicamos al asistente de google
        ledr.off() 
        ledg.on() 
        ledb.on()
        print ("luz celeste encedida")

    if msg == b"#00ffff":
        ledr.off() 
        ledg.on() 
        ledb.on()

#color blanco
    if msg == b"1":    
        #blanco es la mezcla de los tres colores rgb
        #de esa forma solo se ve el color que le indicamos al asistente de google
        ledr.on() 
        ledg.on() 
        ledb.on()
        print ("luz blanca encedida")

    if msg == b"#ffffff":
        ledr.on() 
        ledg.on() 
        ledb.on()
        
    if msg == b"ON":
        ledr.on() 
        ledg.on() 
        ledb.on()
        print ("luz blanca encedida")
        
        
#leds apagados    	
    if msg == b"0":
        ledr.off() 
        ledg.off() 
        ledb.off()
        print ("luz blanca apagada")

    if msg == b"#000000":
        ledr.off() 
        ledg.off() 
        ledb.off()
        print ("luz blanca apagada")

    if msg == b"OFF":
        ledr.off() 
        ledg.off() 
        ledb.off()
        print ("luz blanca apagada")

        

#CONEXION A LA RED WIFI
#########################
# Informacion de la red WiFi
WIFI_SSID = 'ssid'
WIFI_PASSWORD = 'pass'

# apagar el punto de acceso WiFi
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)

# conecta el dispositivo a la red WiFi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASSWORD)

# esperar hasta que el dispositivo esté conectado a la red WiFi
MAX_ATTEMPTS = 20
attempt_count = 0

while not wifi.isconnected() and attempt_count < MAX_ATTEMPTS:
    attempt_count += 1
    time.sleep(1)
    print('conectando a la red WiFi...')
    
if attempt_count == MAX_ATTEMPTS:
    print('no se pudo conectar a la red WiFi')
    sys.exit()
    
print('conectado a la red WiFi')
print ("Configuracion de red: ", wifi.ifconfig())

#CONEXION AL SERVIDOR ADAFRUIT-IO
#########################       
# crear un ID de cliente MQTT
mqtt_client_id = bytes('esp_32', 'utf-8')


# conectar con el corredor de Adafruit IO MQTT usando TCP no seguro (puerto 1883)
# 
# Para usar una conexión segura (encriptada) con TLS:
#    establece el parámetro de inicializador MQTTClient a "ssl = True"
#    Advertencia: una conexión segura usa aproximadamente 9k bytes de la pila
#          (aproximadamente 1/4 de la pila de micropython en la plataforma ESP8266)
ADAFRUIT_IO_URL = b'io.adafruit.com' 
ADAFRUIT_USERNAME = b'username'
ADAFRUIT_IO_KEY = b'key_xxxxxx'
ADAFRUIT_IO_FEEDNAME = b'feedname'

client = MQTTClient(client_id=mqtt_client_id, 
                    server=ADAFRUIT_IO_URL, 
                    user=ADAFRUIT_USERNAME, 
                    password=ADAFRUIT_IO_KEY,
                    ssl=False)
print('conectado al servidor MQTT')

try:      
    client.connect()
except Exception as e:
    print('no se pudo conectar al servidor MQTT {}{}'.format(type(e).__name__, e))
    sys.exit()


mqtt_feedname = bytes('user/feeds/name, 'utf-8')
client.set_callback(cb)                    
client.subscribe(mqtt_feedname)  

# Seguir dos líneas es una implementación específica de Adafruit de la función Publicar "retener"
# que permite que una Suscripción reciba inmediatamente el último valor publicado para un feed,
# incluso si ese valor se publicó hace dos horas.
# Descrito en el blog de Adafruit IO, 22 de abril de 2018: https://io.adafruit.com/blog/  
mqtt_feedname_get = bytes('{:s}/get'.format(mqtt_feedname), 'utf-8')    
client.publish(mqtt_feedname_get, '\0')
     

# espere hasta que se hayan publicado los datos en la fuente IO de Adafruit
while True:
    try:
        client.wait_msg()
        
    except KeyboardInterrupt:
        print('Ctrl-C pressed...exiting')
        client.disconnect()
        sys.exit()



