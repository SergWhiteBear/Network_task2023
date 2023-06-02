import socket
import datetime
from config import HOST, PORT, TIME_OFFSET


def get_current_time():
    """Функция для получения текущего точного времени от OC"""
    return datetime.datetime.now()


def modify_time(current_time, offset):
    """Функция для модификации времени на заданное смещение"""
    modified_time = current_time + datetime.timedelta(seconds=offset)
    return modified_time


def run_server():
    """Функция для запуска сервера"""
    # Создание UDP-сокета
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        # Привязка сокета к адресу и порту
        server_socket.bind((HOST, PORT))
        print(f"Сервер запущен на {HOST}:{PORT}")
        print(f"Смещение времени: {TIME_OFFSET} секунд")

        while True:
            # Принятие запроса от клиента
            data, address = server_socket.recvfrom(1024)
            print(f"Запрос получен от клиента {address}")

            # Получение текущего времени
            current_time = get_current_time()

            # Модификация времени на заданное смещение
            modified_time = modify_time(current_time, TIME_OFFSET)

            # Отправка времени клиенту
            server_socket.sendto(str(modified_time).encode(), address)


# Запуск сервера
if __name__ == "__main__":
    run_server()
