import time
from paho.mqtt import client as mqtt_client
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap
from PyQt5 import QtWidgets, QtCore
from PyQt5 import uic

app = QtWidgets.QApplication([])
janela = uic.loadUi("interface.ui")

broker      = 'broker.emqx.io'
port        = 1883
client_id   = "py_iot"
topic_dht   = "lab318/dht"
topic_led   = "lab318/led"
topic_servo = "lab318/servo"

enable    = False
angle     = 1
step      = 30  

def on_message(client, userdata, message):
    print(f"Mensagem recebida de {message.topic}: {message.payload.decode()}")
    janela.lcdNumber_3.display(janela.dial.value())

    if message.topic == topic_dht:
        try:
            payload = message.payload.decode()
            temp_str, hum_str = payload.split(':')

            temp = float(temp_str)
            hum = float(hum_str)

            janela.lcdNumber.display(temp)
            janela.lcdNumber_2.display(hum)

        except Exception as e:
            print(f"Erro ao processar mensagem: {e}")


def connect_mqtt():
    client = mqtt_client.Client(client_id)
    client.on_message = on_message
    client.connect(broker, port)
    print("Cliente conectado ao Broker MQTT")
    return client

def subscribe(client):
    client.subscribe(topic_dht)    

def publish_led(client):
    global enable
    enable = not enable    
    client.publish(topic_led, b'1' if enable else b'0')    
    
    if not enable:
        janela.pushButton.setStyleSheet("""
            QPushButton {
                background-color: #228B22;  /* Verde */
                border-radius: 40px;
                color: white;
                font-weight: bold;
                font-size: 32px;
            }
        """)
    else:
        janela.pushButton.setStyleSheet("""
            QPushButton {
                background-color: #B22222;  /* Vermelho */
                border-radius: 40px;
                color: white;
                font-weight: bold;
                font-size: 32px;
            }
        """)

def publish_servo(client):
    global angle, direction    

    angle = janela.dial.value()
    if angle >= 180:
        angle = 180        
    elif angle <= 1:
        angle = 1        
    
    client.publish(topic_servo, str(angle).encode())

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_start()    
    janela.dial.setMinimum(1)
    janela.dial.setMaximum(180)
    # Define o estado inicial do botão e seu estilo
    global enable
    enable = False
    janela.pushButton.setStyleSheet("""
        QPushButton {
            background-color: #B22222;  /* Vermelho */
            border-radius: 40px;
            color: white;
            font-weight: bold;
            font-size: 32px;
        }
    """)

    timer = QtCore.QTimer()
    timer.timeout.connect(lambda: publish_servo(client))
    timer.start(1000)

    janela.lcdNumber_3.display(janela.dial.value())
    janela.pushButton.clicked.connect(lambda: publish_led(client))

    janela.show()
    app.exec_()

    client.loop_stop()



if __name__ == '__main__':
    run()
