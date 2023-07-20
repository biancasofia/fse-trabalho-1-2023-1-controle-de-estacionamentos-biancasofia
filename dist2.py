import socket
import threading
import json
import RPi.GPIO as GPIO
import uuid
import time
from datetime import datetime


#como bcm
GPIO.setmode(GPIO.BCM)
#placa 4
#como bcm

############# placa de 1 a 3 ##############

ENDERECO_01 = 13
ENDERECO_02 = 6
ENDERECO_03 = 5
SENSOR_DE_VAGA = 20
SINAL_DE_LOTADO_FECHADO = 8
SENSOR_DE_PASSAGEM_1 = 16
SENSOR_DE_PASSAGEM_2 = 21
"""
###########################################

##############placa 4 #####################
ENDERECO_01=21
ENDERECO_02=20
ENDERECO_03=16
SENSOR_DE_VAGA=12
SINAL_DE_LOTADO_FECHADO=23
SENSOR_DE_PASSAGEM_1=25
SENSOR_DE_PASSAGEM_2=24
############# andar 2###########
"""
GPIO.setup(ENDERECO_01, GPIO.OUT)
GPIO.setup(ENDERECO_02, GPIO.OUT)
GPIO.setup(ENDERECO_03, GPIO.OUT)
GPIO.setup(SENSOR_DE_VAGA, GPIO.IN)
GPIO.setup(SINAL_DE_LOTADO_FECHADO, GPIO.OUT)
GPIO.setup(SENSOR_DE_PASSAGEM_1, GPIO.IN)
GPIO.setup(SENSOR_DE_PASSAGEM_2, GPIO.IN)


def ler_sensor_vaga():
    return GPIO.input(SENSOR_DE_VAGA)
##############


def acender_luz_lotado():
    GPIO.output(SINAL_DE_LOTADO_FECHADO, GPIO.HIGH)

def apagar_luz_lotado():
    GPIO.output(SINAL_DE_LOTADO_FECHADO, GPIO.LOW)
##############################


def leitura_sensor_vaga(endereco):
    GPIO.output(ENDERECO_01, (endereco & 0b001) == 0b001)
    GPIO.output(ENDERECO_02, (endereco & 0b010) == 0b010)
    GPIO.output(ENDERECO_03, (endereco & 0b100) == 0b100)
    time.sleep(0.1)  # Espera para estabilização do sinal
    return GPIO.input(SENSOR_DE_VAGA)

pode_entrar = True #global

class DistributedServer:
    def __init__(self, host='localhost', port=5562, client='client2'):
    #def __init__(self, host='164.41.98.27', port=5562, client='client2'):
        self.host = host
        self.port = port
        self.client = client
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        
    def envia_servidor(self, vagas_ocupadas):
        
        message = [{
                "vaga_ocupada": vagas_ocupadas
            
            }]
        message_dict = {
            "from": self.client,
            "message": message
        }
            
        self.sock.send(json.dumps(message_dict).encode())
        
  
    def controla_sinal(self):
        while True:
    
            
            vagas_ocupadas = []            
            for endereco in range(8):
                if leitura_sensor_vaga(endereco):
                    vagas_ocupadas.append(endereco+1)
            
            #print(f"Vagas ocupadas: {vagas_ocupadas}")
            #print(vagas_ocupadas)
            time.sleep(0.5)
            self.envia_servidor(vagas_ocupadas)


    def receive_message(self):
        while True:
            try:

                message = self.sock.recv(1024).decode()
                message_dict = json.loads(message)
                #print(f"recebi isso do servidor: {message_dict} ")
                
                
              
                if message_dict['message'] == 'fecha 2 andar':
                    acender_luz_lotado()
                   
                if message_dict['message'] == 'abre 2 andar':
                    apagar_luz_lotado() 
                     
                
                
            except:
                break
        self.sock.close()    
    

    def run(self):
        thread_sinal = threading.Thread(target=self.controla_sinal)
        #thread_send = threading.Thread(target=self.send_message)
        thread_receive = threading.Thread(target=self.receive_message)

        #thread_send.start()
        thread_receive.start()
        thread_sinal.start()

if __name__ == '__main__':
    server = DistributedServer(port=10602, client='client2')
    server.run()