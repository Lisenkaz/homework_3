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
