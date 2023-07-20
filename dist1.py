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
"""
ENDERECO_01 = 26
ENDERECO_02 = 19
ENDERECO_03 = 13
SENSOR_DE_VAGA = 9
SINAL_DE_LOTADO_FECHADO = 6
SENSOR_ABERTURA_CANCELA_ENTRADA = 10
SENSOR_FECHAMENTO_CANCELA_ENTRADA = 22
MOTOR_CANCELA_ENTRADA = 5
SENSOR_ABERTURA_CANCELA_SAIDA = 27
SENSOR_FECHAMENTO_CANCELA_SAIDA = 17
MOTOR_CANCELA_SAIDA = 4
"""
#placa 1-3
ENDERECO_01 = 22
ENDERECO_02 = 26
ENDERECO_03 = 19
SENSOR_DE_VAGA = 18
SINAL_DE_LOTADO_FECHADO = 27
SENSOR_ABERTURA_CANCELA_ENTRADA = 23
SENSOR_FECHAMENTO_CANCELA_ENTRADA = 24
MOTOR_CANCELA_ENTRADA = 10
SENSOR_ABERTURA_CANCELA_SAIDA = 25
SENSOR_FECHAMENTO_CANCELA_SAIDA = 12
MOTOR_CANCELA_SAIDA = 17


#ENDERECO_01 = 22
GPIO.setup(ENDERECO_01, GPIO.OUT)

#ENDERECO_02 = 26
GPIO.setup(ENDERECO_02, GPIO.OUT)

#ENDERECO_03 = 19
GPIO.setup(ENDERECO_03, GPIO.OUT)

#SENSOR_DE_VAGA = 18
GPIO.setup(SENSOR_DE_VAGA, GPIO.IN)

#SINAL_DE_LOTADO_FECHADO = 27
GPIO.setup(SINAL_DE_LOTADO_FECHADO, GPIO.OUT)

#SENSOR_ABERTURA_CANCELA_ENTRADA = 23
GPIO.setup(SENSOR_ABERTURA_CANCELA_ENTRADA, GPIO.IN)

#SENSOR_FECHAMENTO_CANCELA_ENTRADA = 24
GPIO.setup(SENSOR_FECHAMENTO_CANCELA_ENTRADA, GPIO.IN)


#MOTOR_CANCELA_ENTRADA = 10
GPIO.setup(MOTOR_CANCELA_ENTRADA, GPIO.OUT)

#SENSOR_ABERTURA_CANCELA_SAIDA = 25
GPIO.setup(SENSOR_ABERTURA_CANCELA_SAIDA, GPIO.IN)

#SENSOR_FECHAMENTO_CANCELA_SAIDA = 12
GPIO.setup(SENSOR_FECHAMENTO_CANCELA_SAIDA, GPIO.IN)

#MOTOR_CANCELA_SAIDA = 17
GPIO.setup(MOTOR_CANCELA_SAIDA, GPIO.OUT)



def gerar_identificador():
    return str(uuid.uuid4())

#### cancelas
def abrir_cancela_entrada():
    GPIO.output(MOTOR_CANCELA_ENTRADA, GPIO.HIGH)
    

def fechar_cancela_entrada():
    GPIO.output(MOTOR_CANCELA_ENTRADA, GPIO.LOW)


def abrir_cancela_saida():
    GPIO.output(MOTOR_CANCELA_SAIDA, GPIO.HIGH)

 

def fechar_cancela_saida():    
    GPIO.output(MOTOR_CANCELA_SAIDA, GPIO.LOW)

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
    def __init__(self, host='localhost', port=5562, client='client1'):
    #def __init__(self, host='164.41.98.27', port=5562, client='client1'):
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

    vagas_ocupadas =[]
    def controla_sinal(self):
        while True:
            global pode_entrar
            if pode_entrar==True:
                if GPIO.input(SENSOR_ABERTURA_CANCELA_ENTRADA) == GPIO.HIGH:
                    #GPIO.output(MOTOR_CANCELA_ENTRADA, GPIO.HIGH)
                    abrir_cancela_entrada()
                    print("Veiculo passando")

                    if GPIO.wait_for_edge(SENSOR_FECHAMENTO_CANCELA_ENTRADA, GPIO.RISING):
                            # Desativa cancela
                        fechar_cancela_entrada()
                        print("Cancela fechada")
                        
                        
    
            time.sleep(1.5)
            vagas_ocupadas = []            
            for endereco in range(8):
                if leitura_sensor_vaga(endereco):
                    vagas_ocupadas.append(endereco+1)
            total_vagas_ocupadas= len(vagas_ocupadas)
            #print(f"Vagas ocupadas: {vagas_ocupadas}")
            time.sleep(0.3)
            self.envia_servidor(vagas_ocupadas)

            if GPIO.input(SENSOR_ABERTURA_CANCELA_SAIDA) == GPIO.HIGH:
                abrir_cancela_saida()
                print("Veiculo passando")
                if GPIO.wait_for_edge(SENSOR_FECHAMENTO_CANCELA_SAIDA, GPIO.RISING):
                        # Desativa cancela
                    time.sleep(0.4)
                    fechar_cancela_saida()
                    print("Cancela fechada")
            #self.send_message(vagas_ocupadas)
        


    def receive_message(self):
        while True:
            try:
               
        
                
                # Converte os dados em um objeto JSON
               
                # Imprime a mensagem no formato "remetente: mensagem"
                message = self.sock.recv(1024).decode()
                #if not message:
                #    break
                message_dict = json.loads(message)
                #print(f"recebi isso do servidor: {message_dict} ")
            
                #print(message['message'][0])
                global pode_entrar
                if message_dict['message'] == 'fechar':
                    acender_luz_lotado()
                    pode_entrar=False
                if message_dict['message'] == 'abrir':
                    apagar_luz_lotado() 
                    pode_entrar=True   
                
                
            except:
                break
        #self.sock.close()    
    

    def run(self):
        thread_sinal = threading.Thread(target=self.controla_sinal)
        #thread_send = threading.Thread(target=self.send_message)
        thread_receive = threading.Thread(target=self.receive_message)

        #thread_send.start()
        thread_receive.start()
        thread_sinal.start()

if __name__ == '__main__':
    server = DistributedServer(port=10602, client='client1')
    server.run()