import base64
import json
import mimetypes
import os
import socket
import ssl
import time

host_addr = 'smtp.yandex.ru'
port = 465


def request(s, req):
    """
    Отправка запроса и получение ответа от сервера
    """
    s.send((req + '\n').encode())
    s.setblocking(0)
    recv_data = b""
    while True:
        try:
            chunk = s.recv(4096)
            if not chunk:
                break
            recv_data += chunk
        except socket.error as e:
            if e.errno == socket.errno.EWOULDBLOCK:  # Нет доступных данных для получения
                time.sleep(1)
                continue
            else:
                break
    return recv_data.decode("UTF-8")


class SMTPClient:
    def __init__(self):
        """
        Инициализация объекта SMTPClient
        """
        self.ssl_contex = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.ssl_contex.check_hostname = False
        self.ssl_contex.verify_mode = ssl.CERT_NONE
        self.user_name_from = None
        self.list_user_name_to = None
        self.user_name_from = None
        self.subject_msg = None
        self.attachment_path = None
        self.pswd = None
        self.get_json_conf()
        self.get_pswd()

    def get_json_conf(self):
        """
        Получение конфигурации из JSON-файла
        """
        with open('config.json', 'r', encoding='UTF-8') as json_file:
            file = json.load(json_file)
            self.user_name_from = file['from']  # считываем кто отправляет
            self.list_user_name_to = file['to']  # считываем список кому отправляем
            if isinstance(self.list_user_name_to, str):
                self.list_user_name_to = [self.list_user_name_to]
            self.subject_msg = file['subject']
            self.attachment_path = file['attachment_path']

    def get_pswd(self):
        """
        Получение пароля из файла
        """
        with open('pswd.txt', 'r', encoding="UTF-8") as file:
            self.pswd = file.read().strip()

    def message_prepare(self):
        """
        Подготовка тела сообщения
        """
        with open('msg.txt', 'r', encoding="UTF-8") as file_msg:
            boundary_msg = "bound.40629"
            users_name_to = ','.join(self.list_user_name_to)
            headers = f'from: {self.user_name_from}\n' \
                      f'to: {users_name_to}\n' \
                      f'subject: {self.subject_msg}\n' \
                      'MIME-Version: 1.0\n' \
                      'Content-Type: multipart/mixed;\n' \
                      f'\tboundary={boundary_msg}\n'

            # тело сообщения началось
            msg = file_msg.read()
            message_body = f'--{boundary_msg}\n' \
                           'Content-Type: text/plain; charset=utf-8\n\n' \
                           f'{msg}\n'

            for filename in os.listdir(self.attachment_path):
                mime_type = mimetypes.guess_type(filename)

                with open(self.attachment_path + '/' + filename, 'rb') as attachment:
                    str_attachment = base64.b64encode(attachment.read()).decode()

                message_body += f'--{boundary_msg}\n' \
                                'Content-Disposition: attachment;\n' \
                                f'\tfilename="{filename}"\n' \
                                'Content-Transfer-Encoding: base64\n' \
                                f'Content-Type: {mime_type[0]};\n' \
                                f'\tname="{filename}"\n\n' \
                                f'{str_attachment}\n'

            message_body += f'--{boundary_msg}--'

            message = headers + '\n' + message_body + '\n.\n'
            print(message)
            return message

    def run(self):
        with socket.create_connection((host_addr, port)) as sock:
            with self.ssl_contex.wrap_socket(sock, server_hostname=host_addr) as client:
                print(client.recv(1024))  # в smpt сервер первый говорит
                print(request(client, f'ehlo {self.user_name_from}'))
                base64login = base64.b64encode(self.user_name_from.encode()).decode()

                base64password = base64.b64encode(self.pswd.encode()).decode()
                print(request(client, 'AUTH LOGIN'))
                print(request(client, base64login))
                print(request(client, base64password))
                print(request(client, f'MAIL FROM:{self.user_name_from}'))
                for user_name_to in self.list_user_name_to:
                    print(request(client, f"RCPT TO:{user_name_to}"))
                print(request(client, 'DATA'))
                print(request(client, self.message_prepare()))
                print(request(client, 'QUIT'))


def main():
    smtp_client = SMTPClient()
    smtp_client.run()


if __name__ == '__main__':
    main()
