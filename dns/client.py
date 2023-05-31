import re
import socket
from dnslib import DNSRecord
import random

domains = ['vk.com', 'ya.ru', 'amazon.com', 'openai.com', 'e1.ru']
query_types = ['A', 'NS']


def check_valid_ip(ip):
    ip_regex = r'^(\d{1,3}\.){3}\d{1,3}$'
    return True if re.match(ip_regex, ip) else False


def domain_to_ip(domain_name):
    try:
        ip = socket.gethostbyname(domain_name)
        return ip
    except:
        return "Не удалось разрешить IP-адрес"


def ip_to_domain(ip):
    try:
        domain_name = socket.gethostbyaddr(ip)[0]
        return domain_name
    except:
        return "Не удалось разрешить доменное имя"


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = ('localhost', 53)

    for domain in domains:
        print('-----------------------------------')
        if check_valid_ip(domain):
            print(domain + ' ' + ip_to_domain(domain))
        else:
            print(domain + ' ' + domain_to_ip(domain))

        print('-----------------------------------')

        # Формирование запроса
        query_data = DNSRecord.question(domain, random.choice(query_types)).pack()

        # Отправляю запрос
        client_socket.sendto(query_data, server_address)

        # Получаю ответ
        resp_data, _ = client_socket.recvfrom(1024)
        resp = DNSRecord.parse(resp_data)

        print(resp)

    client_socket.close()

if __name__ == "__main__":
    main()
