import argparse  # Импортируем модуль для работы с аргументами командной строки
import xml.etree.ElementTree as ET  # Импортируем модуль для работы с XML
import sys  # Импортируем модуль для работы с системными вызовами
import re # Импортируем модуль для работы с регулярными выражениями
import xml.dom.minidom
#Функция для вычисления префиксного выражения
def evaluate_prefix(expression, constants):
    # Убираем квадратные скобки и разбиваем строку на токены
    tokens = expression.strip('[]').split()
    stack = []  # Стек для хранения операндов
    i = len(tokens) - 1  # Индекс для перебора токенов (начинаем с конца)

    while i >= 0:
        token = tokens[i]  # Получаем текущий токен
        if token.isdigit():  # Если токен - число
            stack.append(int(token))  # Добавляем его в стек как целое число
        elif token in constants:  # Если токен - константа
            stack.append(constants[token])  # Добавляем значение константы в стек
        elif token == '+':  # Если токен - операция сложения
            if len(stack) < 2:  # Проверяем, достаточно ли операндов
                raise ValueError("Недостаточно операндов для выполнения операции.")
            a = stack.pop()  # Извлекаем первый операнд
            b = stack.pop()  # Извлекаем второй операнд
            stack.append(a + b)  # Выполняем сложение и помещаем результат в стек
        elif token == '-':  # Если токен - операция вычитания
            if len(stack) < 2:
                raise ValueError("Недостаточно операндов для выполнения операции.")
            a = stack.pop()  # Извлекаем первый операнд
            b = stack.pop()  # Извлекаем второй операнд
            stack.append(a - b)  # Выполняем вычитание и помещаем результат в стек
        elif token == '*':  # Если токен - операция умножения
            if len(stack) < 2:
                raise ValueError("Недостаточно операндов для выполнения операции.")
            a = stack.pop()  # Извлекаем первый операнд
            b = stack.pop()  # Извлекаем второй операнд
            stack.append(a * b)  # Выполняем умножение и помещаем результат в стек
        elif token == '/':  # Если токен - операция деления
            if len(stack) < 2:
                raise ValueError("Недостаточно операндов для выполнения операции.")
            a = stack.pop()  # Извлекаем первый операнд
            b = stack.pop()  # Извлекаем второй операнд
            stack.append(a / b)  # Выполняем деление и помещаем результат в стек
        elif token == 'pow':  # Если токен - операция возведения в степень
            if len(stack) < 2:
                raise ValueError("Недостаточно операндов для операции pow.")
            base = stack.pop()  # Извлекаем второй операнд
            exponent = stack.pop()  # Извлекаем первый операнд
            stack.append(base ** exponent)  # Выполняем возведение в степень и помещаем результат в стек
        else:  # Если токен не распознан
            raise ValueError(f"Неизвестный токен: {token}")
         
        i -= 1  # Переходим к следующему токену (в обратном порядке)

    if len(stack) != 1:  # Проверяем, что в стеке остался только один результат
        raise ValueError("Ошибка в выражении")
    
    return stack[0]  # Возвращаем результат вычисления

# Функция для удаления комментариев
def remove_comments(text):   
    # Удаляем однострочные комментарии, начинающиеся с "::"
    text = re.sub(r'::.*', '', text)  
    # Удаляем многострочные комментарии, заключенные в фигурные скобки {}
    text = re.sub(r'\{.*?\}', '', text, flags=re.DOTALL)  
    # Возвращаем текст без пробелов в начале и в конце
    return text.strip()  

# Функция для парсинга объявления константы
def parse_constants(text):   
    constants = {}  # Словарь для хранения найденных констант
    remaining_lines = []  # Список для хранения строк, не являющихся константами
    
    # Проходим по каждой строке входного текста
    for line in text.splitlines():
        line = line.strip()  # Убираем лишние пробелы в начале и конце строки
        
        # Проверяем, начинается ли строка с объявления константы
        if '=' in line and "=>" not in line:
            name, expression = line.split('=', 1)  # Разделяем на имя и выражение
            name = name.strip()  # Убираем лишние пробелы
            expression = expression.strip()  # Убираем лишние пробелы
            
            # Проверяем, является ли выражение префиксным
            if expression.startswith('[') and expression.endswith(']'):
                try:
                    # Вычисляем значение префиксного выражения
                    value = evaluate_prefix(expression, constants)
                    constants[name] = value  # Сохраняем результат в словарь констант
                except ValueError as e:
                    raise ValueError(f"Ошибка при вычислении выражения '{expression}': {e}")
            else:
                # Проверяем, является ли значением числом
                match = re.match(r"(\d+)", expression)
                if match:
                    constants[name] = int(match.group(1))  # Сохраняем константу в словарь, преобразуя значение в целое число
                else:
                    raise ValueError(f"Неверный формат константы: {line}")
        else:
            remaining_lines.append(line)  # Если строка не является константой, добавляем ее в список оставшихся строк
            
    return constants, "\n".join(remaining_lines)  # Возвращаем словарь констант и оставшийся текст в виде строки

# Функция для парсинга словаря
def parse_dict(text, constants):
    if not text.startswith('table(') or not text.endswith(')'):
        raise ValueError("Неверный формат словаря: должен начинаться с 'table(' и заканчиваться ')'")
    
    # Убираем 'table(' и ')' и лишние пробелы
    text = text[6:-1].strip()  
    result = {}  # Словарь для хранения пар ключ-значение
    buffer = ""  # Буфер для хранения текущей пары ключ-значение
    
    depth = 0  # Переменная для отслеживания вложенности
    for char in text:
        if char == ',' and depth == 0:  # Если встречаем запятую и глубина вложенности равна нулю
            if buffer.strip():  # Если буфер не пустой
                key_value = buffer.split('=>', 1)  # Разделяем на ключ и значение
                if len(key_value) != 2:  # Проверяем, что пара состоит из ключа и значения
                    raise ValueError(f"Неверный формат пары: {buffer}")
                key = key_value[0].strip()  # Извлекаем и обрезаем ключ
                value = key_value[1].strip()  # Извлекаем и обрезаем значение
                
                # Обработка значения
                if value.isdigit():
                    result[key] = int(value)  # Если значение - число, добавляем как целое
                elif value in constants:
                    result[key] = constants[value]  # Если значение - константа, добавляем ее значение
                else:
                    raise ValueError(f"Неизвестное значение: {value}")
                
                buffer = ""  # Очищаем буфер
        else:
            buffer += char  # Добавляем символ в буфер
            if char == '{':
                depth += 1  # Увеличиваем глубину при встрече открывающей скобки
            elif char == '}':
                depth -= 1  # Уменьшаем глубину при встрече закрывающей скобки

    # Обрабатываем последний элемент
    if buffer.strip():
        key_value = buffer.split('=>', 1)
        if len(key_value) != 2:
            raise ValueError(f"Неверный формат пары: {buffer}")
        key = key_value[0].strip()
        value = key_value[1].strip()
        
        if value.isdigit():
            result[key] = int(value)
        elif value in constants:
            result[key] = constants[value]
        else:
            raise ValueError(f"Неизвестное значение: {value}")

    return result  # Возвращаем собранный словарь

def parse_key_value(item, constants):    
    # Разделяем элемент по '=>' на ключ и значение
    key_value = item.split('=>', 1)  
    if len(key_value) != 2:  # Проверяем, что мы получили ровно две части
        raise ValueError(f"Неверный формат элемента: {item}")  # Если нет, выбрасываем ошибку
    
    key = key_value[0].strip()  # Извлекаем и обрезаем ключ
    value = key_value[1].strip()  # Извлекаем и обрезаем значение
    
    # Преобразуем значение
    if value.isdigit():  # Если значение является числом
        value = int(value)  # Преобразуем его в целое число
    elif value in constants:  # Если значение является константой
        value = constants[value]  # Заменяем его на соответствующее значение константы
    elif value.startswith('table(') and value.endswith(')'):  # Если значение - это словарь
        value = parse_dict(value, constants)  # Парсим словарь
    else:  # В противном случае считаем значение строкой
        value = value.strip('"')  # Убираем кавычки вокруг строки, если они есть
    
    return key, value  # Возвращаем ключ и обработанное значение
