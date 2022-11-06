# Библиотека yadisk для работы с облачным хранилищем данных "Яндекс.Диск"
import yadisk

# Модуль библиотеки calendar для получения количества дней в зависимости от месяца и года
from calendar import monthrange
# Модули библиотеки python-telegram-bot позволяющие работать с Telegram Bot API
from telegram import ReplyKeyboardMarkup, InputMediaDocument
# Модули библиотеки python-telegram-bot дополняющие Telegram Bot API
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters

# Токен облачного хранилища данных "Яндекс.Диск", где расположены все медиа и текстовые файлы
yandex_disk_token = "y0_AgAAAABALxVvAAhfcwAAAADNm_GdxJ2gzsdISuSJfntSvJ0Kaydd99w"
# Создание объекта класса YaDisk, реализующие доступ к REST API Яндекс.Диска
yandex_disk = yadisk.YaDisk(token=yandex_disk_token)

years_reg = "(^2022$|^2023$|^2024$)"
months_reg = "(^Сентябрь$|^Октябрь$|^Ноябрь$|^Декабрь$|^Январь$|^Февраль$|^Март$|^Апрель$|^Май$|^Июнь$|^Июль$|^Август$)"
months_dir = {'Январь': 1, 'Февраль': 2, 'Март': 3, 'Апрель': 4, 'Май': 5, 'Июнь': 6, 'Июль': 7, 'Август': 8,
              'Сентябрь': 9, 'Октябрь': 10, 'Ноябрь': 11, 'Декабрь': 12}
subjects_reg = "(^Алгебра$|^Геометрия$|^Мат. анализ$|^Русский язык$|^Литература$|^Английский язык$|^Биология$|^ОБЖ$|^История$|^Физика$|^Химия$|^Физ. лаба$|^Обществознание$)"
choice_reg = "(^Конспекты$|^Дз$)"
days_reg = "(^\d{1}$|^\d{2}$)"
action_reg = "(^Загрузить конспекты$|^Посмотреть конспекты$)"

things_reply_keyboard = [["Конспекты"]]
action_reply_keyboard = [["Загрузить конспекты", "Посмотреть конспекты"], ["Назад"], ["Выйти"]]
subjects_reply_keyboard = [["Алгебра", "Геометрия", "Мат. анализ"], ["Русский язык", "Литература", "Английский язык"],
                           ["Биология", "ОБЖ", "История"], ["Физика", "Химия", "Физ. лаба"], ["Обществознание"],
                           ["Выйти"]]
years_reply_keyboard = [["2022", "2023", "2024"], ["Назад"], ["Выйти"]]
months_reply_keyboard = [["Сентябрь", "Октябрь", "Ноябрь"], ["Декабрь", "Январь", "Февраль"], ["Март", "Апрель", "Май"],
                         ["Июнь", "Июль", "Август"], ["Назад"], ["Выйти"]]

ACTION, SUBJECT, YEAR, MONTH, DAY, UPLOAD_PHOTOS, GET_PHOTOS, SEE_PHOTOS, RETURN_USER = range(9)


# TestKonspektBotToken = 5525504235:AAElnC-jc2lYK1W2sg0UddRXvmpfwXbsxkc
# MisterKonspektBot = 5769101237:AAFeY_vVY9teDwm3VWqj9hWk1lz8rPiqAQ0

def main() -> None:
    # Токен бота телеграм
    konspektbot_token = "5525504235:AAElnC-jc2lYK1W2sg0UddRXvmpfwXbsxkc"
    # Создание основного объекта класса Application, в котором происходят все взаимодействия пользователя с ботом
    application = Application.builder().token(konspektbot_token).build()
    # Обработчик сообщений, реагирующий на любые сообщения, запускающий цепочку обработки сообщений пользователя
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), MessageHandler(filters.ALL, start)],
        # Цепочка обработки представляет собой словарь, содержащий в себе обработчики сообщений с порядковым номером,
        # представленным переменной для читаемости кода
        states={ACTION: [MessageHandler(filters.Regex(choice_reg),
                                        choose_an_action)],
                SUBJECT: [MessageHandler(filters.Regex(action_reg),
                                         choose_a_subject)],
                YEAR: [MessageHandler(filters.Regex(subjects_reg),
                                      choose_a_year)],
                MONTH: [MessageHandler(filters.Regex(years_reg),
                                       choose_a_month)],
                DAY: [MessageHandler(filters.Regex(months_reg),
                                     choose_a_day)],
                GET_PHOTOS: [MessageHandler(filters.Regex(days_reg), get_or_see_photos)],
                UPLOAD_PHOTOS: [MessageHandler(filters.PHOTO |
                                               filters.Document.Category('image/') |
                                               filters.Document.MimeType('application/pdf') |
                                               filters.Document.MimeType('application/docx'),
                                               upload_photos)], },
        fallbacks=[MessageHandler(filters.Regex("(^Выйти$)"), start)])
    # Добавления обработчика сообщений в основной объект application
    application.add_handler(conv_handler)
    # Запуск бесконечной обработки сообщений
    application.run_polling()


async def start(update, context) -> int:  # Стартовая функция отвечающая за начало работы бота
    """
    tempiter = copy.copy(context.user_data)
    for i in range(len(context.user_data)-1):
        context.user_data[i] = 0
    context.user_data["step"] = 0
    """
    # Получение списка объектов всех файлов находящихся в облачном хранилище "Яндекс.Диске"
    context.user_data["files_list"] = list(yandex_disk.get_files())
    # Вызов функции отправки сообщения пользователю и вызова дополнительной клавиатуру для выбора опции,
    # задействующая things_reply_keyboard
    await update.message.reply_text("Приветствую! Выберите, пожалуйста, то, что Вам нужно",
                                    reply_markup=ReplyKeyboardMarkup(
                                        keyboard=things_reply_keyboard,
                                        one_time_keyboard=False,
                                        resize_keyboard=True))
    return ACTION


async def choose_an_action(update, context) -> int:  # Функция выбора действия, задействующая action_reply_keyboard
    # Сохранения сообщения пользователя, репрезентующая выбор опции
    context.user_data["choice"] = update.message.text
    # Вызов функции отправки сообщения пользователю и вызов дополнительной клавиатуру для выбора действия
    await update.message.reply_text("Что вы хотите сделать?",
                                    reply_markup=ReplyKeyboardMarkup(
                                        keyboard=action_reply_keyboard,
                                        one_time_keyboard=False,
                                        resize_keyboard=True))
    # Возвращение порядкового номера функции в словаре для её последующего вызова
    return SUBJECT


async def choose_a_subject(update, context) -> int:  # Функция выбора учебного предмета
    # Сохранения сообщения пользователя, репрезентующая выбор действия
    context.user_data["action"] = update.message.text
    # Ветвление, определяющие, какое действие выбрал пользователь
    if context.user_data["action"] == "Посмотреть конспекты":
        # Переменная, содержащая все учебные предметы с выложенными конспектами
        existing_subjects = []
        # Поиск всех учебных предметов с выложенными конспектами
        for i in context.user_data["files_list"]:
            existing_subjects.append(i['path'].split('/')[2])
        # Создание двумерного списка, содержащего списки со всеми учебными предметами с выложенными конспектами
        # (По три учебных предмета в каждом списке, для удобного использования дополнительной клавиатуры)
        existing_subjects_reply_keyboard = [list((set(existing_subjects)))[i:i + 3]
                                            for i in range(0, len(set(existing_subjects)), 3)]
        existing_subjects_reply_keyboard.append(['Выйти'])
        # Вызов функции отправки сообщения пользователю, с использованием existing_subjects_reply_keyboard,
        # и вызов дополнительной клавиатуру для выбора учебного предмета
        await update.message.reply_text("Выберите предмет",
                                        reply_markup=ReplyKeyboardMarkup(
                                            keyboard=existing_subjects_reply_keyboard,
                                            one_time_keyboard=False,
                                            resize_keyboard=True))
    elif context.user_data["action"] == "Загрузить конспекты":
        # Вызов функции отправки сообщения пользователю, с использованием subjects_reply_keyboard,
        # и вызов дополнительной клавиатуру для выбора действия
        await update.message.reply_text("Выберите предмет",
                                        reply_markup=ReplyKeyboardMarkup(
                                            keyboard=subjects_reply_keyboard,
                                            one_time_keyboard=False,
                                            resize_keyboard=True))
    # Возвращение порядкового номера функции в словаре для её последующего вызова
    return YEAR


async def choose_a_year(update, context) -> int:  # Функция выбора календарного года
    # Сохранения сообщения пользователя, репрезентующая выбор учебного предмета
    context.user_data["subject"] = update.message.text
    # Ветвление, определяющие, какое действие выбрал пользователь
    if context.user_data["action"] == "Посмотреть конспекты":
        # Получение годов, на которые загружены конспекты по выбранному предмету
        existing_year = []
        for i in context.user_data["files_list"]:
            if i['path'].split('/')[2] == context.user_data["subject"]:
                existing_year.append(i['path'].split('/')[3])
        # Создание на основе existing_year, оформленного для дополнительной клавиатуры, списка
        existing_year_reply_keyboard = [list(set(existing_year)), ['Выйти']]
        # Вызов функции отправки сообщения пользователю, с использованием years_exist_reply_keyboard,
        # и вызов дополнительной клавиатуру для выбора года просмотра конспектов
        await update.message.reply_text("Выберите год: ",
                                        reply_markup=ReplyKeyboardMarkup(
                                            keyboard=existing_year_reply_keyboard,
                                            one_time_keyboard=False,
                                            resize_keyboard=True))
    elif context.user_data["action"] == "Загрузить конспекты":
        # Вызов функции отправки сообщения пользователю, с использованием years_reply_keyboard,
        # и вызов дополнительной клавиатуру для выбора года для загрузки конспектов
        await update.message.reply_text("Выберите год: ",
                                        reply_markup=ReplyKeyboardMarkup(
                                            keyboard=years_reply_keyboard,
                                            one_time_keyboard=False,
                                            resize_keyboard=True))
    # Возвращение порядкового номера функции в словаре для её последующего вызова
    return MONTH


async def choose_a_month(update, context) -> int:  # Функция выбора месяца
    # Сохранения сообщения пользователя, репрезентующая выбор календарного года
    context.user_data["year"] = update.message.text
    # Ветвление, определяющие, какое действие выбрал пользователь
    if context.user_data["action"] == "Посмотреть конспекты":
        # Получение месяцев, на которые загружены конспекты по выбранному предмету и году
        existing_months = []
        for i in context.user_data["files_list"]:
            if i['path'].split('/')[2] == context.user_data["subject"] and \
                    i['path'].split('/')[3] == context.user_data["year"]:
                existing_months.append(i['path'].split('/')[4])
        # Создание на основе existing_months, оформленного для дополнительной клавиатуры, списка
        existing_months_reply_keyboard = [list(set(existing_months))[i:i + 3]
                                          for i in range(0, len(set(existing_months)), 3)]
        existing_months_reply_keyboard.append(['Выйти'])
        # Вызов функции отправки сообщения пользователю, с использованием existing_months_reply_keyboard,
        # и вызов дополнительной клавиатуру для выбора месяца для просмотра конспектов
        await update.message.reply_text("Выберите месяц: ",
                                        reply_markup=ReplyKeyboardMarkup(
                                            keyboard=existing_months_reply_keyboard,
                                            one_time_keyboard=False,
                                            resize_keyboard=True))
    elif context.user_data["action"] == "Загрузить конспекты":
        # Вызов функции отправки сообщения пользователю, с использованием months_reply_keyboard,
        # и вызов дополнительной клавиатуру для выбора месяца для загрузки конспектов
        await update.message.reply_text("Выберите месяц: ",
                                        reply_markup=ReplyKeyboardMarkup(
                                            keyboard=months_reply_keyboard,
                                            one_time_keyboard=False,
                                            resize_keyboard=True))
    # Возвращение порядкового номера функции в словаре для её последующего вызова
    return DAY


async def choose_a_day(update, context) -> int:  # Функция выбора дня
    # Сохранения сообщения пользователя, репрезентующая выбор месяца
    context.user_data["month"] = update.message.text
    # Ветвление, определяющие, какое действие выбрал пользователь
    if context.user_data["action"] == "Посмотреть конспекты":
        # Получение дней, на которые загружены конспекты по выбранному предмету, году и месяцу
        existing_days = []
        for i in context.user_data["files_list"]:
            if i['path'].split('/')[2] == context.user_data["subject"] and \
                    i['path'].split('/')[3] == context.user_data["year"] and \
                    i['path'].split('/')[4] == context.user_data["month"]:
                existing_days.append(int(i['path'].split('/')[5]))
        # Сортируем список существующих дней по возрастанию
        existing_days = sorted(set(existing_days))
        # Меняем тип данных каждого элемента списка
        existing_days = list(map(str, existing_days))
        # Создание на основе existing_days, оформленного для дополнительной клавиатуры, списка
        existing_days_reply_keyboard = [existing_days[i:i + 5]
                                        for i in range(0, len(existing_days), 5)]
        existing_days_reply_keyboard.append(['Выйти'])
        # Вызов функции отправки сообщения пользователю, с использованием existing_days_reply_keyboard,
        # и вызов дополнительной клавиатуру для выбора дня для просмотра конспектов
        await update.message.reply_text("Выберите день: ",
                                        reply_markup=ReplyKeyboardMarkup(keyboard=existing_days_reply_keyboard,
                                                                         one_time_keyboard=False, resize_keyboard=True))
    elif context.user_data["action"] == "Загрузить конспекты":
        # Получение количества дней в выбранном месяце и годе
        amount_of_days = monthrange(int(context.user_data["year"]), months_dir[context.user_data["month"]])[1]
        # Создание на основе amount_of_days, оформленного для дополнительной клавиатуры, списка
        days_reply_keyboard = [[str(i)
                                for i in
                                range(ii, ii + 5 - (5 - amount_of_days % 5) * (amount_of_days // 5 * 5 <= ii))]
                               for ii in range(1, amount_of_days + 1, 5)]
        days_reply_keyboard.append(['Выйти'])
        # Вызов функции отправки сообщения пользователю, с использованием days_reply_keyboard,
        # и вызов дополнительной клавиатуру для выбора дня для загрузки конспектов
        await update.message.reply_text("Выберите день: ",
                                        reply_markup=ReplyKeyboardMarkup(keyboard=days_reply_keyboard,
                                                                         one_time_keyboard=False, resize_keyboard=True))
    # Возвращение порядкового номера функции в словаре для её последующего вызова
    return GET_PHOTOS


async def get_or_see_photos(update, context):  # Функция просмотра или запуска функции загрузки фото и/или документов
    # Переменная, для последующего использования в ветвление для лучшей читаемости кода
    empty = None
    # в зависимости от выбранной опции и действия в начале
    # Сохранения сообщения пользователя, репрезентующая выбор дня
    context.user_data["day"] = update.message.text
    # Создание переменной, хранящей полный путь до файлов
    context.user_data["path"] = "conspectbot/" \
                                + context.user_data["subject"] + '/' \
                                + context.user_data["year"] + '/' \
                                + context.user_data["month"] + '/' \
                                + context.user_data["day"]
    # Получение и оформление полного списка файлов, хранящегося по данному пути
    # (Оформление из-за того, что бот отправляет файлы группой, которая максимум может содержать 10 файлов)
    # (Сам способ отправки файлов группами используется для оптимизации процесса,
    # так как загрузка файлов с "Яндекс.Диска" достаточна медленная и заставляет бота фризить)
    existing_files = list(yandex_disk.listdir(context.user_data["path"]))
    existing_files = [[InputMediaDocument(yd_object["file"])
                       for yd_object in (existing_files[i:i + 9]) if yd_object["file"] is not None]
                      for i in range(0, len(existing_files) + 1, 9)]
    # Ветвление, определяющие, какое действие выбрал пользователь
    if context.user_data["action"] == "Загрузить конспекты":
        # Вызов функции отправки сообщения пользователю
        # и вызов дополнительной клавиатуру для выбора дня для загрузки конспектов
        await update.message.reply_text("Отправьте в чат изображения, которые вы хотите добавить",
                                        reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад"], ["Выйти"]],
                                                                         one_time_keyboard=False, resize_keyboard=True))
        # Возвращение порядкового номера функции в словаре для её последующего вызова
        return UPLOAD_PHOTOS
    # Ветвление, определяющие, какое действие выбрал пользователь
    elif context.user_data["action"] == "Посмотреть конспекты":
        # Ветвление, определяющие, существуют ли конспекты по заданному path
        if existing_files is empty:
            # Вызов функции отправки сообщения пользователю,
            # и вызов дополнительной клавиатуру для возможности вернуться в начало
            await update.message.reply_text("Извините, на эту дату конспекты не выложены, попросите выложить",
                                            reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад"], ["Выйти"]],
                                                                             one_time_keyboard=False,
                                                                             resize_keyboard=True))
        elif existing_files is not empty:
            # Вызов функции отправки сообщения пользователю,
            # и вызов дополнительной клавиатуру для возможности вернуться в начало
            await update.message.reply_text(text="Вот все фото, которые мне удалось найти:",
                                            reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад"], ["Выйти"]],
                                                                             one_time_keyboard=False,
                                                                             resize_keyboard=True))
            # Цикл оправки файлов пользователю
            for group_of_files in existing_files:
                # Функция отправки групп файлов пользователю
                await context.bot.send_media_group(update.message.chat.id, group_of_files, protect_content=True)


async def upload_photos(update, context) -> None:  # Функция для загрузки фото и/или документов
    # Создание локальной переменной, содержащей выбранный пользователем путь
    temp_path = context.user_data["path"]
    # Ветвление, которое определяет тип присланного пользователем файла
    if update.message.document:
        # Путь, по которому будет загружен присланный пользователем файл
        temp_path += '/' + context.from_user.username + '_' + update.message.document.file_name
        # Получение образа файла при помощи бота
        file = await context.bot.get_file(update.message.document.file_id)
        # Загрузка файла на диск
        yandex_disk.upload_url(file.file_path, temp_path)
    elif update.message.photo:
        # Получение фото из List[TelegramPhotoSize] с максимальным разрешением
        photo_file = update.message.photo[len(update.message.photo) - 1]
        # Путь, по которому будет загружено присланное пользователем фото
        temp_path += '/' + context.from_user.username + '_' + photo_file.file_unique_id
        # Получение образа фото при помощи бота
        file = await context.bot.get_file(photo_file.file_id)
        # Загрузка фото на диск
        yandex_disk.upload_url(file.file_path, temp_path)

# Запуск программы
main()
