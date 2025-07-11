**Установка, если нет python:**
1. Скачайте python по ссылке https://www.python.org/. Обязательно поставить галочку "Add python to path"

**Запуск:**
1. Открыть командную строку:
    
    **Для Windows:**
    Win + R, далее "cmd"
    
    **Для Mac:**
    Cmd + Space, далее "Terminal"
    
    **Для Linux:**
    Ctrl + Alt + T
2. Далее перейти в папку с проектом: ```cd путь_к_папке_с_проектом``` у каждого свой путь.
3. Создание и активация виртуального окружения:
    
    **Создание виртуального окружения:**
    ```python -m venv venv```
    
    **Активация:**
    ```venv\Scripts\activate```
    
    **Для Mac или Linux:**
    ```source venv/bin/activate```
4. Установить зависимости: ```pip install -r requirements.txt```
5. Запустить проект: ```python -m uvicorn main:app --reload```
6. Откройте браузер по готовой ссылке или сгенерированной:
   
    **Нужная ссылка: "http://localhost:8000/docs"**
   
    Либо найдите строку: **Uvicorn running on ←[1mhttp://127.0.0.1:8000←[0m (Press CTRL+C to quit)**.
    Скопируйте **"http://127.0.0.1:8000"** и добавьте **"/docs"** в строку

**Как использовать?**

**Для деревьев:**

1. Откройте документацию по адресу /docs и найдите эндпоинт /tree_ascii.

2. Нажмите кнопку "Try it out" рядом с полем для ввода параметров.

3. В открывшемся JSON-окне можно ввести массив чисел — например:
```
{
  "values": [5, 3, 7, 2, null, 6, 8],
  "mode": null
}
```
Можно изменять числа и менять "mode" на "bst" для сбалансированного бинарного дерева

4. Внизу нажмите кнопку "Execute"
5. Ниже появится ответ сервера с визуализацией дерева в ASCII-формате — это и есть дерево

**Для кодирования и декодирования:**

1. Откройте документацию по адресу /docs и найдите эндпоинты "/custom-base/encode" или "/custom-base/decode".

2. Нажмите кнопку "Try it out" рядом с полем для ввода параметров.

3. В открывшемся JSON-окне можно вводить числа и строки для кодирования и декодирования — например:
```
{
  "decimal": 12345
}
```
```
{
  "encoded": "ABc1"
}
```

4. Внизу нажмите кнопку "Execute"
5. Появится ответ в JSON-формате
**Система кодирования:**

Поддерживается кодирование чисел в **пользовательскую систему счисления (до 1007-ричной)** с использованием:

**Базовые символы:**
Цифры: "0-9" - 10
Латинские буквы: "A-Z", "a-z" (регистрозависимо) - 52

**Специальные префиксы** (для расширения диапазона):
("!", "@", "#", "$", "%", "^", "&", "*", "_", "~", "α", "β", "γ", "δ", "λ") - 15

**Особенности:**
Префиксы можно комбинировать с базовыми символами (например: "!A", "β3")

Максимальная длина входной строки: 1050 символов

Поддерживаются отрицательные числа (используйте "-" в начале)

Большие числа возвращаются в виде строки (без экспоненциальной записи) #До этого было не так