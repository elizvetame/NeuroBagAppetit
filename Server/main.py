import socket
from threading import Thread
import json

HOST, PORT = 'localhost', 8080  # Адрес сервера
MAX_PLAYERS = 2  # Максимальное кол-во подключений


class Server:

    def __init__(self, addr, max_conn):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(addr)  # запускаем сервер от заданного адреса

        self.max_players = max_conn
        self.players = []  # создаем массив из игроков на сервере

        self.sock.listen(self.max_players)  # устанавливаем максимальное кол-во прослушиваний на сервере
        self.listen()  # вызываем цикл, который отслеживает подключения к серверу

    def listen(self):
        while True:
            if not len(self.players) >= self.max_players:  # проверяем не превышен ли лимит
                # одобряем подключение, получаем взамен адрес и другую информацию о клиенте
                conn, addr = self.sock.accept()

                print("New connection", addr)

                Thread(target=self.handle_client,
                       args=(conn,)).start()  # Запускаем в новом потоке проверку действий игрока

    def handle_client(self, conn):

        # Настраиваем стандартные данные для игрока
        self.player = {
            "id": len(self.players),
            "x": 400,
            "y": 300
        }
        self.players.append(self.player)  # добавляем его в массив игроков

        while True:
            try:
                data = conn.recv(1024)  # ждем запросов от клиента

                if not data:  # если запросы перестали поступать, то отключаем игрока от сервера
                    print("Disconnect")
                    break

                # загружаем данные в json формате
                data = json.loads(data.decode('utf-8'))

                # запрос на получение игроков на сервере
                if data["request"] == "get_players":
                    conn.sendall(bytes(json.dumps({
                        "response": self.players
                    }), 'UTF-8'))

                # движение
                if data["request"] == "move":

                    if data["move"] == "left":
                        self.player["x"] -= 1
                    if data["move"] == "right":
                        self.player["x"] += 1
                    if data["move"] == "up":
                        self.player["y"] -= 1
                    if data["move"] == "down":
                        self.player["y"] += 1
            except Exception as e:
                print(e)
                break

        self.players.remove(self.player)  # если вышел или выкинуло с сервера - удалить персонажа


if __name__ == "__main__":
    server = Server((HOST, PORT), MAX_PLAYERS)