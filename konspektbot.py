# Модуль библиотеки calendar для получения количества дней в зависимости от месяца и года
from calendar import monthrange
# Модуль библиотеки functools для передачи дополнительных аргументов в функцию
from functools import partial
# Библиотека yadisk для работы с облачным хранилищем данных "Яндекс.Диск"
import yadisk

# Модули библиотеки python-telegram-bot позволяющие работать с Telegram Bot API
from telegram import ReplyKeyboardMarkup, Bot, InputMediaDocument
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
    # Создание основного объекта класса Bot, репрезентирующий бота, с которым пользователь взаимодействует
    bot = Bot(konspektbot_token)
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
                GET_PHOTOS: [MessageHandler(filters.Regex(days_reg),
                                            partial(get_or_see_photos, bot=bot))],
                UPLOAD_PHOTOS: [MessageHandler(filters.PHOTO |
                                               filters.Document.Category('image/') |
                                               filters.Document.MimeType('application/pdf') |
                                               filters.Document.MimeType('application/docx'),
                                               partial(upload_photos, bot=bot))], },
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
        existing_subjects_reply_keyboard = [(list((set(existing_subjects)))[i:i + 3]
                                             for i in range(0, len(set(existing_subjects)), 3)),
                                            ['Выйти']]
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
        existing_year = []
        for i in context.user_data["files_list"]:
            if i['path'].split('/')[2] == context.user_data["subject"]:
                existing_year.append(i['path'].split('/')[3])
        years_exist_reply_keyboard = [(list(set(existing_year))),
                                      ['Выйти']]
        await update.message.reply_text("Выберите год: ",
                                        reply_markup=ReplyKeyboardMarkup(
                                            keyboard=years_exist_reply_keyboard,
                                            one_time_keyboard=False,
                                            resize_keyboard=True))
    elif context.user_data["action"] == "Загрузить конспекты":
        await update.message.reply_text("Выберите год: ",
                                        reply_markup=ReplyKeyboardMarkup(
                                            keyboard=years_reply_keyboard,
                                            one_time_keyboard=False,
                                            resize_keyboard=True))
    # Возвращение порядкового номера функции в словаре для её последующего вызова
    return MONTH


async def choose_a_month(update, context) -> int:
    context.user_data["year"] = update.message.text
    if context.user_data["action"] == "Посмотреть конспекты":
        existing_months = []
        for i in context.user_data["files_list"]:
            if i['path'].split('/')[2] == context.user_data["subject"] and \
                    i['path'].split('/')[3] == context.user_data["year"]:
                existing_months.append(i['path'].split('/')[4])
        existing_months_reply_keyboard = [(list((set(existing_months)))[i:i + 3]
                                           for i in range(0, len(set(existing_months)), 3)),
                                          ['Выйти']]
        await update.message.reply_text("Выберите месяц: ",
                                        reply_markup=ReplyKeyboardMarkup(
                                            keyboard=existing_months_reply_keyboard,
                                            one_time_keyboard=False,
                                            resize_keyboard=True))
    else:
        await update.message.reply_text("Выберите месяц: ",
                                        reply_markup=ReplyKeyboardMarkup(
                                            keyboard=months_reply_keyboard,
                                            one_time_keyboard=False,
                                            resize_keyboard=True))
    return DAY


async def choose_a_day(update, context) -> int:
    context.user_data["month"] = update.message.text
    if context.user_data["action"] == "Посмотреть конспекты":
        existing_days = []
        for i in context.user_data["files_list"]:
            if i['path'].split('/')[2] == context.user_data["subject"] and \
                    i['path'].split('/')[3] == context.user_data["year"] and \
                    i['path'].split('/')[4] == context.user_data["month"]:
                existing_days.append(i['path'].split('/')[5])
        existing_days_reply_keyboard = [(list((set(existing_days)))[i:i + 5]
                                         for i in range(0, len(set(existing_days)), 5)),
                                        ['Выйти']]

        await update.message.reply_text("Выберите день: ",
                                        reply_markup=ReplyKeyboardMarkup(keyboard=existing_days_reply_keyboard,
                                                                         one_time_keyboard=False, resize_keyboard=True))
    else:
        amount_of_days = monthrange(int(context.user_data["year"]), months_dir[context.user_data["month"]])[1]
        days_reply_keyboard = [[[i
                                 for i in range(ii, ii + 5 - (5 - amount_of_days % 5) * (amount_of_days // 5 * 5 <= ii))]
                                 for ii in range(1, amount_of_days + 1, 5)],
                               ['Выйти']]
        await update.message.reply_text("Выберите день: ",
                                        reply_markup=ReplyKeyboardMarkup(keyboard=days_reply_keyboard,
                                                                         one_time_keyboard=False, resize_keyboard=True))
    return GET_PHOTOS


async def get_or_see_photos(update, context, bot) -> int:
    context.user_data["day"] = update.message.text
    context.user_data["path"] = 'conspectbot/' \
                                + context.user_data["subject"] + '/' \
                                + context.user_data["year"] + '/' \
                                + context.user_data["month"] + '/' \
                                + context.user_data["day"]
    existing_files = list(yandex_disk.listdir(context.user_data["path"]))
    existing_files = [existing_files[i:i + 9] for i in (0, len(existing_files) + 1, 9)]
    if context.user_data["action"] == "Загрузить конспекты":
        await update.message.reply_text("Отправте в чат изображения, которые вы хотите добавить",
                                        reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад"], ["Выйти"]],
                                                                         one_time_keyboard=False, resize_keyboard=True))
        return UPLOAD_PHOTOS
    if context.user_data["action"] == "Посмотреть конспекты":
        if existing_files is None:
            await update.message.reply_text("Извините, на эту дату конспекты не выложены, попросите выложить",
                                            reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад"], ["Выйти"]],
                                                                             one_time_keyboard=False,
                                                                             resize_keyboard=True))
        elif existing_files is not None:
            await update.message.reply_text(text="Вот все фото, которые мне удалось найти:",
                                            reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад"], ["Выйти"]],
                                                                             one_time_keyboard=False,
                                                                             resize_keyboard=True))
            for i in existing_files:
                await bot.send_media_group(update.message.chat.id, i)


async def upload_photos(update, context, bot) -> int:
    path = 'conspectbot/' + context.user_data["subject"] + '/' + context.user_data["year"] + '/' + context.user_data[
        "month"] + '/' + context.user_data["day"]
    if update.message.document:
        path += '/' + update.message.document.file_name
        file = await bot.get_file(update.message.document.file_id)
        yandex_disk.upload_url(file.file_path, path)
    elif update.message.photo:
        photo_file = update.message.photo[len(update.message.photo) - 1]
        path += '/' + photo_file.file_unique_id
        file = await bot.get_file(photo_file.file_id)
        yandex_disk.upload_url(file.file_path, path)


main()
