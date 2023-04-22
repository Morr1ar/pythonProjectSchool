# Импорт всех необходимых модулей
import os # Модуль для обработки файлов
import pyttsx3  # Модуль для воспроизведения текста в речь
import speech_recognition as sr  # Модуль для прослушивания микрофона
import colorama
from fuzzywuzzy import fuzz   # Модуль для нечёткого сравнения строк
import datetime  # Модуль для определения время
from os import system
import sys
from random import choice # Модуль для управления генерацией случайных чисел
from pyowm import OWM # Модуль для реализации погоды
from pyowm.utils.config import get_default_config
import webbrowser  # Модуль для выполнения запросов и открытия вкладок в вашем браузере
import configparser # Модуль для работы с INI-файлами Microsoft Windows
import time
import json # Модуль для обмена данными


class Assistant:
    settings = configparser.ConfigParser()
    settings.read('settings.ini')

    config_dict = get_default_config()  # Инициализация get_default_config()
    config_dict['language'] = 'ru'  # Установка языка

    def __init__(self):       #конструктор
        # Глобальные переменные
        self.engine = pyttsx3.init()
        self.r = sr.Recognizer()  # Инициализация распознавателя
        self.text = ''  # Создание глобальной переменной text

        self.num_task = 0
        self.j = 0
        self.ans = ''

        # Словарь со всеми настройками
        self.cmds = {   # список функций и команд, при которых они выполняются
            ('привет', 'добрый день', 'доброе утро', 'добрый вечер', 'здравствуй'): self.hello,
            ('пока', 'вырубись'): self.quite,
            ('время', 'который час'): self.time,
            ('выключи компьютер', 'выруби компьютер'): self.shut,
            ('какая погода', 'погода'): self.weather,
            ('запиши контакт', 'запиши телефон'): self.contacts_list_save,
            ('номер телефона', 'список контактов', 'контакты'): self.contacts_reminder,
            ('удалить контакт', 'удали контакт'): self.del_contact,
            ('запомни', 'сделай заметку'): self.save_reminder,
            ('заметки',): self.reminder,
            ('удалить заметку', 'удали заметку'): self.del_reminder,
            ('добавить рецепт', 'новый рецепт'): self.save_recipes,
            ('рецепты', 'напомни рецепт', 'книга рецептов'): self.recipes_reminder,
            ('удалить рецепт', 'удали рецепт'): self.del_recipes,
            ('посчитай', 'включи калькулятор', 'калькулятор'): self.colculator,
            ('гугл закладки', 'google закладки', 'закладки'): self.google_marks,
        }
        # список имен и слов на которые откликается ассистент
        self.ndels = ['морган', 'морген', 'моргэн', 'морг', 'ладно', 'не могла бы ты', 'пожалуйста',
                      'текущее', 'сейчас']
        # список команд
        self.commands = [
            'привет', 'добрый день', 'здравствуй',
            'пока', 'вырубись',
            'время', 'который час',
            'выключи компьютер', 'выруби компьютер',
            'какая погода', 'погода',
            'запиши контакт', 'запиши телефон',
            'номер телефона', 'список контактов', 'контакты',
            'удалить контакт', 'удали контакт',
            'запомни', 'сделай заметку',
            'заметки',
            'удалить заметку', 'удали заметку',
            'добавить рецепт', 'новый рецепт',
            'рецепты', 'напомни рецепт', 'книга рецептов',
            'удалить рецепт', 'удали рецепт',
            'посчитай', 'включи калькулятор', 'калькулятор',
            'гугл закладки', 'google закладки', 'закладки',
        ]

    def text_save(self, text, file_name):   # метод записывания текста в выбранный файл
        file = open(file_name, 'a+', encoding="utf-8")
        if file_name != 'bookmarks.txt':
            self.talk("Записываю...")
        self.text = ""
        file.write(text + "\n")
        file.close()

    def del_text(self, index, count, filename):     # метод удаления текста из файла по индексу строки (удаляет выбранное количество строк)
        file = open(filename, encoding="utf-8")
        text = file.readlines()

        del text[index:index + count]
        file.close()

        file = open(filename, 'w', encoding="utf-8")
        file.write("".join(text))
        file.close()

    def text_replace(self, filename, name, text_to_add):
        file = open(filename, encoding="utf-8")
        old_text = file.read()
        text_list = old_text.split()
        numb = text_list.index(name)

        new_text = old_text.replace(text_list[numb + 1], text_list[numb + 1] + "%" + text_to_add)
        file.close()

        file = open(filename, 'w', encoding='utf-8')
        file.write(new_text)
        file.close()

    def parse_bookmarks(self):
        filename = 'bookmarks.txt'
        homepath = os.getenv('USERPROFILE')

        open(filename, 'w', encoding='utf-8').close()

        f = open(homepath + r'\AppData\Local\Google\Chrome\User Data\Default\Bookmarks', encoding='utf-8')
        text = json.load(f)

        text = text['roots']

        key = 'bookmark_bar'
        key1 = 'children'
        for key2 in text[key][key1]:
            if 'children' in key2:
                continue
            self.text_save(key2['name'], filename)
            self.text_save(key2['url'], filename)
        f.close()

    def number_check(self, number):     # проверка корректности написания номера телефона
        if len(number) == 15:
            return True
        else:
            return False

    def fuzz_ratio(self, text, list):
        for i in range(len(list)):
            k = fuzz.ratio(text, list[i])
            if (k > 70) & (k > self.j):
                text = list[i]
                self.j = k

    def google_marks(self):     # добавиь фузратио
        self.parse_bookmarks()
        filename = "bookmarks.txt"
        text_list = [line.strip() for line in open(filename, encoding="utf-8").readlines()]
        self.talk("Вот список всех ваших закладок:")
        numb = 1
        for i, mark in enumerate(text_list):
            if i % 2 == 0:
                print(str(numb) + ': ' + mark, text_list[i + 1])
                numb += 1
        self.talk('Какую открыть?')
        while True:
            print('Скажите номер')
            self.listen("")
            try:
                self.talk('Перехожу...')
                webbrowser.open(text_list[int(self.text) * 2 - 1])
                break
            except ValueError:
                self.talk('Повторите, пожалуйста')
            except IndexError:
                self.talk('Такой закладки нет')

    def contacts_list_save(self):   # метод записывания нового контакта в файл с контактами
        filename = "numbers_list.txt"
        self.listen("Как назвать контакт?")
        error_word = "напомни номер телефона"
        k = True
        while k:
            if fuzz.ratio(self.text, error_word) > 70:
                self.listen("Некорректно назван контакт! Повторите ещё раз.")
            else:
                k = False
        text_list = [line.strip() for line in open(filename, encoding="utf-8").readlines()]
        self.fuzz_ratio(self.text, text_list)
        name = self.text
        if self.text in text_list:  # проверяет есть ли данный контакт в списке контактов. если есть, то записывает новый номер рядом с имеющимся
            n = True
            self.listen("Диктуй номер")
            count = 0
            while n:
                count += 1
                print(count)
                if self.number_check(self.text) == True:
                    self.text_replace(filename, name, self.text)
                    n = False
                else:
                    self.talk("Некорректно назван номер! Повторите ещё раз.")
        else:   # если нет записывает новый контакт
            self.text_save(name, filename)
            m = True
            self.listen("Диктуй номер")
            c = 0
            while m:
                c += 1
                print(c)
                if self.number_check(self.text) == True:
                    print(self.text)
                    self.text_save(self.text, filename)
                    m = False
                else:
                    self.talk("Некорректно назван номер! Повторите ещё раз.")

    def contacts_reminder(self):    # метод напоминания номера телефона
        filename = 'numbers_list.txt'
        self.listen(choice(["Чей номер вам напомнить?", "Чей номер вы хотите знать?", "Чей номер вам нужен?"]))
        text_list = [line.strip() for line in open(filename, encoding="utf-8").readlines()]
        self.fuzz_ratio(self.text, text_list)
        if self.text in text_list:
            for numb in range(len(text_list)):
                if self.text in text_list[numb]:
                    numbers_list = text_list[numb + 1].split("%")
                    if len(numbers_list) > 1:
                        self.talk("Вот список номеров этого контакта:")     # он только печатает список номеров если их несколько
                        for i in range(len(numbers_list)):
                            self.talk(numbers_list[i])
                    else:
                        self.talk("Номер: " + numbers_list[0])

    def colculator(self):   # простой калькулятор (4 операции)
        print('Скажите "Завершить" чтобы мы закончили!')
        while True:
            self.listen("")
            if self.text == 'Завершить':
                break
            text = self.text.split(" ")
            a = text[0]
            op = text[1]
            b = text[2]
            if op in ('+', '-', '*', '/'):
                if op + b != "/0":
                    self.talk(eval(a + op + b))
                else:
                    self.talk("На ноль делить я еще не научилась!")
            else:
                self.talk("Не поняла!")

    def save_reminder(self):    # метод записывания новой заметки в файл с заметками
        filename = "reminder_list.txt"
        self.listen("Слушаю вас")
        if self.text.startswith(('надо', 'нужно', 'напомни', 'напомни мне')):    # вырезает ненужные слова из сказанного текста
            for i in ('надо', 'нужно', 'напомни', 'напомни мне'):
                self.text = self.text.replace(i, '').strip()
                self.text = self.text.replace('  ', ' ').strip()
        self.text_save(self.text, filename)
        self.listen("Когда напомнить? Скажите дату.")
        self.text_save(self.time_converter(self.text)[-5:], filename)
        self.listen("Во сколько?")
        self.text_save(self.text, filename)


    def reminder(self): # напоминание заметок на сегодня
        filename = 'reminder_list.txt'
        text_list = [line.strip() for line in open(filename, encoding="utf-8").readlines()]
        date_today = str(datetime.date.today())[5:]
        if date_today in text_list:
            self.talk(choice(['Вам сегодня надо:', 'В списке ваших дел на сегодня:']))
            for numb in range(len(text_list)):
                if date_today in text_list[numb]:
                    self.talk(text_list[numb - 1] + ' в ' + text_list[numb + 1] )
                else:
                    continue
        else:
            self.talk(choice(["На сегодня напоминаний нет", "На сегодня дел нет", "Сегодня дел никаких нет"]))

    def time_converter(self, text):     # метод изменения текста в дату. пример: 12 января --> 01-12
        text = text.replace('января', '01')
        text = text.replace('февраля', '02')
        text = text.replace('марта', '03')
        text = text.replace('апреля', '04')
        text = text.replace('мая', '05')
        text = text.replace('июня', '06')
        text = text.replace('июля', '07')
        text = text.replace('августа', '08')
        text = text.replace('сентября', '09')
        text = text.replace('октября', '10')
        text = text.replace('ноября', '11')
        text = text.replace('декабря', '12')
        text = str("-".join(text.split()[::-1]))
        return text

    def time_back_converter(self, text):    # метод изменения даты в текст. пример: 01-12 --> 12 января
        text = " ".join(text.split("-")[::-1])
        text1 = text[:2]
        text2 = text[2:]
        text2 = text2.replace('01', 'января')
        text2 = text2.replace('02', 'февраля')
        text2 = text2.replace('03', 'марта')
        text2 = text2.replace('04', 'апреля')
        text2 = text2.replace('05', 'мая')
        text2 = text2.replace('06', 'июня')
        text2 = text2.replace('07', 'июля')
        text2 = text2.replace('08', 'августа')
        text2 = text2.replace('09', 'сентября')
        text2 = text2.replace('10', 'октября')
        text2 = text2.replace('11', 'ноября')
        text2 = text2.replace('12', 'декабря')
        return text1 + text2

    def del_contact(self):      # метод удаления контакта
        filename = 'numbers_list.txt'
        self.listen(choice(["Чей контакт хотите удалить?", "Чей номер вы хотите удалить?", "Чей номер вам не нужен?"]))
        text_list = [line.strip() for line in open(filename, encoding="utf-8").readlines()]
        self.fuzz_ratio(self.text, text_list)
        if self.text in text_list:
            for numb in range(len(text_list)):
                if self.text in text_list[numb]:
                    self.del_text(numb, 2, filename)
                    self.talk(choice(["Контакт удален!", "Уже удалила.", "Сделано!"]))
                    break
                else:
                    continue
        else:
            self.talk("Контакт не найден!")

    def del_reminder(self):     # метод удаления заметки
        filename = 'reminder_list.txt'

        self.listen(choice(["Желаете прослушать все имеющиеся заметки?", "Хотите прослушать все имеющиеся заметки?"]))
        list = ['Хочу', 'Желаю', 'Да']
        self.fuzz_ratio(self.text, list)
        if self.text in list:
            self.all_reminder()

        self.listen(choice(["Какая дата?", "Какое число?"]))
        text_list = [line.strip() for line in open(filename, encoding="utf-8").readlines()]
        self.fuzz_ratio(self.text, text_list)
        if self.text in text_list:
            for numb in range(len(text_list)):
                if self.text in text_list[numb]:
                    self.del_text(numb, 2, filename)
                    self.talk(choice(["Заметка удалена!", "Уже удалила.", "Сделано!"]))
                else:
                    continue
        else:
            self.talk("Напоминаний на эту дату не найдено!")

    def del_reminder_init(self):    # метод автомотического удаления ненужных заметок
        filename = 'reminder_list.txt'
        text_list = [line.strip() for line in open(filename, encoding="utf-8").readlines()]
        month = int(str(datetime.date.today())[5:7])
        day = int(str(datetime.date.today())[8:10])
        for line in range(1, len(text_list), 3):
            date = text_list[line]
            if (month > int(date[:2])) or ((month == int(date[:2])) and (day > int(date[3:]))):
                self.del_text(line - 1, 3, filename)
            else:
                continue

    def all_reminder(self):     # метод напоминания всех имеющихся заметок
        filename = 'reminder_list.txt'
        text_list = [line.strip() for line in open(filename, encoding="utf-8").readlines()]

        if len(text_list) >= 3:
            self.talk(choice(['Вам сегодня надо:', 'В списке ваших дел на сегодня:']))

            for numb in range(1, len(text_list), 3):
                self.talk(self.time_back_converter(text_list[numb]) + " " + text_list[numb - 1] + ' в ' + text_list[numb + 1])

        else:
            self.talk(choice(["На сегодня напоминаний нет", "На сегодня дел нет", "Сегодня дел никаких нет"]))

    def save_recipes(self):     # метод добавления рецепта
        filename = 'recipes_list.txt'
        self.listen("Как назвать блюдо?")
        text_list = [line.strip() for line in open(filename, encoding="utf-8").readlines()]
        self.fuzz_ratio(self.text, text_list)
        if self.text in text_list:
            name_of_recipe = self.text
            self.listen("Слушаю вас...")
            self.text_replace(filename, name_of_recipe, self.text)
        else:
            self.text_save(self.text, filename)
            self.listen("Слушаю вас...")
            self.text_save(self.text, filename)

    def del_recipes(self):     # метод удаления рецепта
        filename = 'recipes_list.txt'
        self.listen("Какой рецепт хотите удалить?")
        text_list = [line.strip() for line in open(filename, encoding="utf-8").readlines()]
        self.fuzz_ratio(self.text, text_list)
        if self.text in text_list:
            self.del_text(text_list.index(self.text), 2, filename)
            self.talk("Рецепт удален!")
        else:
            self.talk("Рецепт не найден!")

    def recipes_reminder(self):     # метод напоминания рецепта
        filename = 'recipes_list.txt'
        self.listen("Рецепт какого блюда вам напомнить?")
        text_list = [line.strip() for line in open(filename, encoding="utf-8").readlines()]
        self.fuzz_ratio(self.text, text_list)
        if self.text in text_list:
            recipes_list = text_list[text_list.index(self.text) + 1].split("%")
            self.talk("Вот список рецептов этого блюда")
            for i in range(1, len(recipes_list) + 1):
                self.talk(str(i) + ": " + recipes_list[i - 1])
        else:
            self.talk("Рецепта такого блюда у меня нет")

    def web_search(self, text):
        words = ('найди', 'найти', 'ищи', 'кто такой', 'что такое')
        remove = ["пожалуйста", "ладно", "давай", "сейчас"]  # Создание списка со слов которые будут удалены из запроса
        if text.startswith(words):  # Проверка начинается, ли наш голосовой запрос с ключевых слов записанных в словаре words
            for i in words:  # Создание цикла для очистки слов находящихся в словаре words в запросе
                text = text.replace(i, '')  # Очистка ключевых слов, находящихся в словаре words с запроса
            for j in remove:  # Создание цикла для очистки слов находящихся в списке remove в запросе
                text = text.replace(j, '')  # Очистки слов находящихся в списке remove в запросе
                text = text.strip()  # Преобразование переменной search в строку
            print(text)  # Вывод текста нашего запроса
            webbrowser.open(f'https://www.google.com/search?q={text}&oq={text}'
                            f'81&aqs=chrome..69i57j46i131i433j0l5.2567j0j7&sourceid=chrome&ie=UTF-8')  # выполнение запроса в браузере

    def cleaner(self, text):
        self.text = text
        if text is not None:
            for i in self.ndels:  # Создание цикла для очистки слов находящихся в словаре words в запросе
                self.text = self.text.replace(i, '').strip()  # Очистка ключевых слов, находящихся в словаре ndels с запроса
                self.text = self.text.replace('  ', ' ').strip()  # Очистка ключевых слов, находящихся в словаре ndels с запроса

            self.ans = self.text

            self.fuzz_ratio(self.ans, self.commands)    # поиск совпадений в списке известных команд

            return str(self.ans)

    def recognizer(self):  # метод распознавания речи /  главная функция
        self.text = self.cleaner(self.listen(""))
        if self.text is not None:
            print(self.text)
            print('______')

            if self.text.startswith(('найди', 'найти', 'ищи', 'кто такой', 'что такое')):
                self.web_search(self.text)

            if self.text.startswith(('открой', 'запусти', 'зайди', 'зайди на')):    # если просьба начинается с этих команд выполняется специальная функция
                self.opener(self.text)

            for tasks in self.cmds:     # выбор и привод в действие нужной функции из списка команд
                for task in tasks:
                    if fuzz.ratio(task, self.text) >= 80:
                        self.active = True
                        self.cmds[tasks]()


        self.engine.runAndWait()
        #self.engine.stop()

    def time(self):     # метод, который сообщает текущее время
        now = datetime.datetime.now()
        self.talk("Сейчас " + str(now.hour) + ":" + str(now.minute))

    def opener(self, task):     # метод для выполнения специальных функций
        links = {
            ('youtube', 'ютуб', 'ютюб'): 'https://youtube.com/',
            ('вк', 'вконтакте', 'vk'): 'https:vk.com/feed',
            ('браузер', 'интернет', 'browser'): 'https://google.com/',
            ('insta', 'instagram', 'инста', 'инсту', 'инстаграм'): 'https://www.instagram.com/',
            ('почта', 'почту', 'gmail', 'гмейл', 'гмеил', 'гмаил'): 'http://gmail.com/',
        }
        j = 0
        if 'и' in task:
            task = task.replace('и', '').replace('  ', ' ')
        double_task = task.split()
        if j != len(double_task):
            for i in range(len(double_task)):
                for vals in links:
                    for word in vals:
                        if fuzz.ratio(word, double_task[i]) > 75:
                            webbrowser.open(links[vals])
                            self.talk('Открываю ' + double_task[i])
                            j += 1
                            break

    def cfile(self):    # метод чтения файла settings.ini
        try:
            cfr = Assistant.settings['SETTINGS']['fr']
            if cfr != 1:
                file = open('settings.ini', 'w', encoding='UTF-8')
                file.write('[SETTINGS]\ncountry = RU\nplace = Moscow\nfr = 1')
                file.close()
        except Exception as e:
            print('Перезапустите Ассистента!', e)
            file = open('settings.ini', 'w', encoding='UTF-8')
            file.write('[SETTINGS]\ncountry = RU\nplace = Moscow\nfr = 1')
            file.close()

    def quite(self):    # метод выключения голосового ассистента по команде
        self.talk(choice(['Надеюсь мы скоро увидимся', 'Рада была помочь', 'Пока пока', 'Я отключаюсь']))
        self.engine.stop()
        system('cls')
        self.active = False
        #sys.exit(0)

    def shut(self):     # метод выключения компьютера по команде с подтверждением
        text = self.listen("Подтвердите действие!")
        print(text)
        if (fuzz.ratio(text, 'подтвердить') > 60) or (fuzz.ratio(text, "подтверждаю") > 60):
            self.talk('Действие подтверждено')
            self.talk('До скорых встреч!')
            system('shutdown /s /f /t 10')
            self.quite()
        elif fuzz.ratio(text, 'отмена') > 60:
            self.talk("Действие не подтверждено")
        else:
            self.talk("Действие не подтверждено")

    def hello(self):    # метод приветствия
        self.talk(choice(['Привет', 'Здраствуйте', 'Приветствую']))   # отвечает на мое приветствие
        self.reminder()     # говорит заметки на сегодня
        self.talk('Чем могу помочь?')


    def weather(self):      # метод погоды

        place = Assistant.settings['SETTINGS']['place']
        country = Assistant.settings['SETTINGS']['country']  # Переменная для записи страны/кода страны
        country_and_place = place + ", " + country  # Запись города и страны в одну переменную через запятую
        #owm = OWM('84061a2a5ff54b490d63bd38d557b06d')  # Ваш ключ с сайта open weather map
        owm = OWM('0ca3b9ee1b369a0535434d07a6c572e8')  # Ваш ключ с сайта open weather map
        mgr = owm.weather_manager()  # Инициализация owm.weather_manager()
        observation = mgr.weather_at_place(country_and_place)
        # Инициализация mgr.weather_at_place() И передача в качестве параметра туда страну и город

        w = observation.weather

        status = w.detailed_status  # Узнаём статус погоды в городе и записываем в переменную status
        w.wind()  # Узнаем скорость ветра
        humidity = w.humidity  # Узнаём Влажность и записываем её в переменную humidity
        temp = w.temperature('celsius')[
            'temp']  # Узнаём температуру в градусах по цельсию и записываем в переменную temp
        self.talk("В городе " + str(place) + " сейчас " + str(status) +  # Выводим город и статус погоды в нём
                  "\nТемпература " + str(
            round(temp)) + " градусов по цельсию" +  # Выводим температуру с округлением в ближайшую сторону
                  "\nВлажность составляет " + str(humidity) + "%" +  # Выводим влажность в виде строки
                  "\nСкорость ветра " + str(w.wind()['speed']) + " метров в секунду")  # Узнаём и выводим скорость ветра

    def talk(self, text):
        # Вывод сказанного текста на экран и озвучивание
        print(text)
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self, ask_or_text):  # метод прослушивания микрофона и обработки запроса
        with sr.Microphone() as source:  # Запуск прослушки микрофона и объявление что sr.Microphone() мы используем как source
            #self.r.adjust_for_ambient_noise(source)  # Этот метод нужен для автоматического понижения уровня шума
            try:
                self.talk(ask_or_text)
                audio = self.r.listen(source, timeout=5)  # Инициализация r.listen(source) в переменную audioprint(44444444444444444)
                try:  # Создание обработчика ошибок
                    self.text = self.r.recognize_google(audio, language="ru-RU").lower()  # Распознавание и преобразование речи в текст
                    #self.active = True
                except Exception as e:
                    print(e)
                return self.text  # Возвращаем переменную для передачи данных в другую функцию
            except Exception as e:
                print(e)

    def start(self):  # функция старт
        self.cfile()
        self.del_reminder_init()
        self.parse_bookmarks()
        self.active = True
        self.talk("Голосовой помощник запущен!")
        while self.active:
            Assistant().recognizer()

    #def start(self):    # функция старт
        #self.cfile()
        #self.del_reminder_init()
        #self.parse_bookmarks()
        #self.active = True
        #Assistant().recognizer()
        # c = 0
        # cc = time.time()
        # while c <= 1000 and self.active:  # цикл слушания
        #     Assistant().recognizer()  # Вызов функции recognizer()
        #     if self.active:
        #         c = 0
        #         cc = time.time()
        #         self.active = False
        #     else:
        #         c = time.time() - cc
        #         print(c)
        #         break
        # print('Выключился')



if __name__ == '__main__':
    Assistant().start()
    #Assistant().recognizer()