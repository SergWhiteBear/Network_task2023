import socket
from config import HOST, PORT


def run_client():
    """Функция для запуска клиента"""
    # Создание UDP-сокета
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:

        while True:
            # Отправка запроса на сервер
            client_socket.sendto(b"Time Request", (HOST, PORT))

            # Получение ответа от сервера
            data, server_address = client_socket.recvfrom(1024)
            print(f"Текущее точное время: {data.decode()}")


if __name__ == "__main__":
    run_client()
