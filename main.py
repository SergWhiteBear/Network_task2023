import json
import re
import subprocess
import sys
from urllib import request
from prettytable import PrettyTable
from row_view import Row_view

# Регулярное выражение для ip-шников и возможные исходы tracert
ip_regex = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
not_resolve_node = 'Не удается разрешить системное имя узла'
tracing_route = 'Трассировка маршрута'
time_out = 'Превышен интервал ожидания для запроса'
hops = 'прыжков'


# Получение вывода tracert hostname, т.е. получаем строки из которых будем доставать ip-шники регуляркой
def get_console_tracert(hostname):
    return subprocess.Popen(["tracert", hostname], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.readline


# Получение информации по ip
def get_ip_info(ip):
    url = f'https://ipinfo.io/{ip}/json'
    response = request.urlopen(url).read()
    return json.loads(response)


# Построение таблицы
def get_table(rows: list[Row_view]):
    table = PrettyTable()
    table.field_names = ['№', 'IP', 'AS', 'COUNTRY', 'PROVIDER']
    for i in range(len(rows)):
        table.add_row([
            i + 1,
            rows[i].ip,
            rows[i].as_block,
            rows[i].country,
            rows[i].provider
        ])
    return table


# Обработка вывода tracert hostname и заполнение таблицы информацией об ip, которые были пройдены при маршрутизации
def get_trace_as(hostname):
    trace_begin = False
    table_result = []
    curr_ip = ""
    count_time_out = 0
    for raw_line in iter(get_console_tracert(hostname), ""):
        raw_line = raw_line.decode(encoding='cp866')
        if not_resolve_node in raw_line:
            print(not_resolve_node)
            return
        elif tracing_route in raw_line:
            print(raw_line)
            curr_ip = ip_regex.findall(raw_line)[0]
        elif time_out in raw_line:
            if count_time_out == 4:
                break
            count_time_out += 1
        elif hops in raw_line:
            trace_begin = True
        route_ips = ip_regex.findall(raw_line)
        if not route_ips:
            continue
        ip = route_ips[0]
        if trace_begin:
            if ip == curr_ip:
                break
            table_result.append(Row_view(get_ip_info(ip)))
    return get_table(table_result)


def main():
    print(get_trace_as(sys.argv[1]))


if __name__ == '__main__':
    main()
