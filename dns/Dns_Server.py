import pickle
import socket
from datetime import datetime, timedelta
from dnslib import DNSRecord, RCODE

CACHE_PATH = 'cache.pickle'
TTL = 360


class DNSCache:
    def __init__(self):
        self.cache = {}

    def add_record(self, key, record):
        self.cache[key] = (record, datetime.now())

    def get_record(self, key):
        if key in self.cache:
            record, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=TTL):
                return record
            else:
                print(f'запись {key} удалена')
                del self.cache[key]
        return None

    def save_cache(self):
        with open(CACHE_PATH, "wb") as file:
            pickle.dump(self.cache, file)

    def load_cache(self):
        try:
            with open(CACHE_PATH, "rb") as file:
                self.cache = pickle.load(file)
        except FileNotFoundError:
            pass


class DnsServer:
    def __init__(self):
        self.cache = DNSCache()
        self.cache.load_cache()

    def query_solution(self, query_data):
        try:
            query = DNSRecord.parse(query_data)
            key = (query.q.qname, query.a.rtype)
            # Ищем запись в кэше и возвращаем ее, если она действительна
            cache_record = self.cache.get_record(key)

            if cache_record:
                print(f'Запись найдена в кэше')
                return cache_record.pack()

            # DNS google '8.8.8.8'
            # -//- yandex '77.88.8.1'
            resp = query.send('77.88.8.1', 53, timeout=5)
            resp_record = DNSRecord.parse(resp)
            # Если ответ получен успешно, добавляем запись в кэш и сохраняем его в файл
            if resp_record.header.rcode == RCODE.NOERROR:
                self.cache.add_record(key, resp_record)
                self.cache.save_cache()
                print(f"Добавлена запись в кэш")
            return resp
        except Exception as e:
            print(f"Ошибка: {e}")
            return None

    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(('localhost', 53))

        print("DNS Сервер запущен.")
        try:
            while True:

                query_data, addr = server_socket.recvfrom(1024)
                print(f'Получен запрос от: {addr}')
                resp_data = self.query_solution(query_data)
                if resp_data:
                    server_socket.sendto(resp_data, addr)

        except KeyboardInterrupt:
            print("Завершение работы сервера.")
            server_socket.close()


dns_server = DnsServer()
dns_server.run()
