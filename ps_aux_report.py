import datetime
from subprocess import run


def get_list_processes():
    # Выполняем команду "ps aux"
    result = run(["ps", "aux"], capture_output=True, check=True, timeout=3)
    # Парсим результат команды в словарь процессов
    output = result.stdout.decode().strip().split('\n')
    headers = [h for h in ' '.join(output[0].split()).split() if h]
    data = list(map(lambda s: s.strip().split(maxsplit=len(headers) - 1), output[1:]))
    processes = [dict(zip(headers, d)) for d in data]
    return processes


def get_os_users(processes: list):
    # Получаем список уникальных пользователей из словаря процессов
    os_users = []
    for process in processes:
        if process['USER'] not in os_users:
            os_users.append(process['USER'])
    # Составляем из списка пользователей строку с информацией по пользователям для отчёта
    output_os_users = ""
    for n in range(len(os_users)):
        output_os_users += f"'{str(os_users[n])}'"
        if n < len(os_users) - 1:
            output_os_users += ', '
    return output_os_users


def get_count_user_processes(processes: list):
    # Получаем список пользователей по каждому процессу из словаря
    list_users = []
    for process in processes:
        list_users.append(process['USER'])
    # Составляем словарь с количеством процессов по каждому пользователю
    counter_proc = {}
    for user in list_users:
        if user in counter_proc:
            counter_proc[user] += 1
        else:
            counter_proc[user] = 1
    # Составляем строку для отчета
    result_string = '\n'.join([f'{key}: {value}' for key, value in counter_proc.items()])
    return result_string


def analyze_mem_usage(processes: list):
    # Получаем словарь - имя процесса: процент использования памяти
    mem_usage = {item['COMMAND'][:20]: item['%MEM'] for item in processes}
    # Получаем общий процент использования памяти:
    sum_mem_usage = sum(float(mem_usage[key]) for key, val in mem_usage.items())
    # Ищем процесс с самым большим потреблением памяти
    most_mem_usage = ' - '.join(sorted(mem_usage.items(), key=lambda item: item[1], reverse=True)[0])
    return sum_mem_usage, most_mem_usage


def analyze_cpu_usage(processes: list):
    # Получаем словарь - имя процесса: процент использования памяти
    cpu_usage = {item['COMMAND']: item['%CPU'] for item in processes}
    # Получаем общий процент использования памяти:
    sum_cpu_usage = sum(float(cpu_usage[key]) for key, val in cpu_usage.items())
    # Ищем процесс с самым большим потреблением памяти
    most_cpu_usage = ' - '.join(sorted(cpu_usage.items(), key=lambda item: item[1], reverse=True)[0])
    return sum_cpu_usage, most_cpu_usage


def create_report(processes):
    # Создаем отчет

    os_users = get_os_users(processes)
    count_proc = len(processes)
    count_usr_proc = get_count_user_processes(processes)
    sum_mem_usage, most_mem_usage = analyze_mem_usage(processes)
    sum_cpu_usage, most_cpu_usage = analyze_cpu_usage(processes)
    report = "Отчёт о состоянии системы:\n" \
             f"Пользователи системы: {os_users}\n" \
             f"Процессов запущено: {count_proc}\n" \
             f"\n" \
             f"Пользовательских процессов:\n" \
             f"{count_usr_proc}\n" \
             f"\n" \
             f"Всего памяти используется: {sum_mem_usage}%\n" \
             f"Всего CPU используется: {sum_cpu_usage}\n" \
             f"Больше всего памяти использует: {most_mem_usage}%\n" \
             f"Больше всего CPU использует: {most_cpu_usage}\n"
    print(report)
    return report


def write_file(result_output: str):
    # Запись отчета в txt-файл
    with open(f"{datetime.datetime.now().strftime('%d-%m-%Y-%H-%M-scan')}.txt", "w") as file:
        file.write(result_output)


if __name__ == '__main__':
    list_processes = get_list_processes()
    result = create_report(list_processes)
    write_file(result)
