import pickle
import socket
from datetime import datetime, timedelta
from dnslib import DNSRecord, RCODE

CACHE_PATH = 'cache.pickle'
TTL = 10


class DnsServer:
    def __init__(self):
        self.cache = {}
        self.get_cache()

    def get_cache(self):
        try:
            with open(CACHE_PATH, 'rb') as f:
                cache_data = pickle.load(f)
                for key, (record, valid_period) in cache_data.items():
                    if datetime.now() - valid_period < timedelta(seconds=TTL):
                        self.cache[key] = (record, valid_period)
        except FileNotFoundError:
            print('Кэш пуст!')

    def save_cache(self):
        with open(CACHE_PATH, 'wb') as f:
            pickle.dump(self.cache, f)

    # Получаем данные из кэша по ключу и проверяем их на валидность
    def get_valid_cache_records(self, key):
        records_data = self.cache.get(key)
        if records_data:
            record, valid_period = records_data
            if datetime.now() - valid_period < timedelta(seconds=TTL):
                return record
            del self.cache[key]
        return None

    def update_cache(self, key, record):
        self.cache[(key, record.a.rtype)] = (record, datetime.now())  # ??

    def query_solution(self, query_data):  # ??
        try:
            query = DNSRecord.parse(query_data)
            key = (query.q.qname, query.a.rtype)
            # Ищем запись в кэше и возвращаем ее, если она действительна
            cache_record = self.get_valid_cache_records(key)
            if cache_record:
                return cache_record.pack()
            # DNS google '8.8.8.8'
            # -//- yandex '77.88.8.1'
            resp = query.send('77.88.8.1', 53)
            resp_record = DNSRecord.parse(resp)

            # Если ответ получен успешно, добавляем запись в кэш и сохраняем его в файл
            if resp_record.header.rcode == RCODE.NOERROR:
                self.update_cache(resp_record.a.rname, resp_record)
                self.save_cache()

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
                resp_data = self.query_solution(query_data)

                if resp_data:
                    server_socket.sendto(resp_data, addr)

        except KeyboardInterrupt:
            print("Завершение работы сервера.")
            server_socket.close()


dns_server = DnsServer()
dns_server.run()
