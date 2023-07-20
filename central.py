import socket
import threading
import json
from datetime import datetime
import uuid
import time


vagas_andar1 = {'A1': 0, 'A2': 0, 'A3': 0, 'A4': 0, 'A5': 0, 'A6': 0, 'A7': 0, 'A8': 0}

vagas_andar2 = {'B1': 0, 'B2': 0, 'B3': 0, 'B4': 0, 'B5': 0, 'B6': 0, 'B7': 0, 'B8': 0}

vagas_ocupadas_andar2=[]

carros_estacionados_anterior_andar2=[]

total_carros = 0

valorTotal = 0.0

carros = []

carros_andar2=[]

vagas_ocupadas=[]

carros_estacionados_anterior=[]

vagas_ocupadas2=0
vagas_ocupadas1=0

class Carro:
    def __init__(self, vaga, hora_chegada):
        self.vaga = vaga
        self.hora_chegada = hora_chegada
  

class CentralServer:
    #host='164.41.98.27'
    def __init__(self, host='localhost', port=10602):
    #def __init__(self, host='164.41.98.27', port=10602):
        self.host = host
        self.port = port

        self.clients = []
        self.lock = threading.Lock()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        
    def gerar_identificador():
        return str(uuid.uuid4())

    def accept_connections(self):
        while True:
            conn, addr = self.sock.accept()
            print(f"Nova conexão: {addr}")

            self.clients.append(conn)

            thread_receive = threading.Thread(target=self.receive_message, args=(conn,))
            thread_receive.start()

    estacionamento_cheio='False'
    def receive_message(self, conn):
        while True:
            global vagas_ocupadas2
            global vagas_ocupadas1
            global vagas_andar1 ,carros_andar2, total_carros, carros, vagas_ocupadas, carros_estacionados_anterior, valorTotal
            global carros_estacionados_anterior_andar2, vagas_andar2
            try:
                
                message = conn.recv(1024).decode()
                message = json.loads(message)
                #if message and message["from"] != "server":
                #print(f"Mensagem recebida do cliente {message['from']}: {message['message']}")
                vagas_ocupadas= message['message'][0]['vaga_ocupada']
                #print(message['from'])

                # carros que estavam antes e não estão mais
                if(message['from']=='client1'):
                    carros_que_sairam = list(set(carros_estacionados_anterior) - set(vagas_ocupadas))
                    vagas_ocupadas1=len(vagas_ocupadas)
                    #print(carros_que_sairam)
                    for i in carros_que_sairam:
                        #print(i)
                        vaga = f"A{i}"
                        #print(vaga)
                        # Calcula preço do estacionamento
                        for carro in carros:
                
                            if carro.vaga == vaga:
                                data_dif = datetime.now() - carro.hora_chegada
                                minutos = data_dif.total_seconds() / 60
                                preco =  0.15 * minutos
                                valorTotal= valorTotal +preco
                                print(f"Carro na vaga {vaga} saiu e o preço é: R$ {preco:.2f} e o total {valorTotal:.2f}")
                                break

                    carros_estacionados_anterior = vagas_ocupadas # para a próx iteração
    
                # muda estado no dicionário
                    for i in vagas_ocupadas:
                        if f'A{i}' in vagas_andar1.keys():
                            if vagas_andar1[f'A{i}'] == 0:
                                #print(f"O carro {i} acabou de chegar e estacionou na vaga A{i}.")
                                carros.append(Carro(f'A{i}', datetime.now()))
                                vagas_andar1[f'A{i}'] = 1
                            """
                            else:
                                print(f"O carro {i} já estava estacionado na vaga A{i}.")
                            """
                        else:
                            print(f"A vaga A{i} não existe no andar 1.")
                   
                
                if(message['from']=='client2'):
                    
                    
                    carros_que_sairam = list(set(carros_estacionados_anterior_andar2) - set(vagas_ocupadas))
                    
                    vagas_ocupadas2= len(vagas_ocupadas)
                    for i in carros_que_sairam:
                     
                        vaga = f"B{i}"
                    
                        # Calcula preço do estacionamento
                    
                        for carro in carros_andar2:
                            print(vaga)
                            if carro.vaga == vaga:
                                data_dif = datetime.now() - carro.hora_chegada
                                minutos = data_dif.total_seconds() / 60
                                preco =  0.15 * minutos
                                valorTotal= valorTotal +preco
                                print(f"Carro na vaga {vaga} saiu e o preço é: R$ {preco:.2f} e o total {valorTotal:.2f}")
                                break
                    #print(carros_estacionados_anterior_andar2)
                    #print(vagas_ocupadas)
                    carros_estacionados_anterior_andar2 = vagas_ocupadas # para a próx iteração
                    
                    # muda estado no dicionário
                    for i in vagas_ocupadas:
                        if f'B{i}' in vagas_andar2.keys():
                            if vagas_andar2[f'B{i}'] == 0:
                                #print(f"O carro {i} acabou de chegar e estacionou na vaga A{i}.")
                                carros_andar2.append(Carro(f'B{i}', datetime.now()))
                                vagas_andar2[f'B{i}'] = 1
                          
                        else:
                            print(f"A vaga B{i} não existe no andar 1.")
                    
                

                print(f"Preço total {valorTotal:.2f}")
                print(f"Total de carros estacionados no 1 andar: {vagas_ocupadas1}")
                print(f"Total de carros estacionados no 2 andar: {vagas_ocupadas2}")
                print(f"Estacionamento: {vagas_andar2}")
                print(f"Estacionamento: {vagas_andar1}")

                if(vagas_ocupadas1 + vagas_ocupadas2) == 16 :
                   
                   #self.envia_client( estacionamento_cheio)
                   self.send_message('fechar')
            
                else:
                   self.send_message('abrir')
                
                time.sleep(0.8) ## pra estabilizar
                
                if(vagas_ocupadas2==8):
                    self.send_message('fecha 2 andar')
            
                else:
                   self.send_message('abre 2 andar')
                  
            except:
                break
        conn.close()
  
    def send_message_to_clients(self, sender, message):
        for client in self.clients:
            if client != sender:
                try:
                    client.send(json.dumps(message).encode())
                except:
                    print(f"Erro ao enviar mensagem para {client.getpeername()}")
                    self.clients.remove(client)
  

    def send_message(self, message):
        message_dict = {"from": "server", "message": message}
        self.send_message_to_clients(None,message_dict)
  
    def run(self):
        thread_accept = threading.Thread(target=self.accept_connections)
        #thread_send = threading.Thread(target=self.send_message)

        thread_accept.start()
        #thread_send.start()


if __name__ == '__main__':
    server = CentralServer()
    server.run()