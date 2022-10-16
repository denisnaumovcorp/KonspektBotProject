from calendar import monthrange
from telegram import ReplyKeyboardMarkup, Bot, InputMediaDocument
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler
import telegram.ext.filters as filters
from functools import partial
import yadisk
import copy


disk = yadisk.YaDisk(token="y0_AgAAAABALxVvAAhfcwAAAADNm_GdxJ2gzsdISuSJfntSvJ0Kaydd99w")
print(disk.check_token())
years_reg = "(^2022$|^2023$|^2024$)"
months_reg = "(^Сентябрь$|^Октябрь$|^Ноябрь$|^Декабрь$|^Январь$|^Февраль$|^Март$|^Апрель$|^Май$|^Июнь$|^Июль$|^Август$)"
months_dir = {'Январь': 1, 'Февраль': 2, 'Март': 3, 'Апрель': 4, 'Май': 5, 'Июнь': 6, 'Июль': 7, 'Август': 8, 'Сентябрь': 9, 'Октябрь': 10, 'Ноябрь': 11, 'Декабрь': 12}
subjects_reg = "(^Алгебра$|^Геометрия$|^Мат. анализ$|^Русский язык$|^Литература$|^Английский язык$|^Биология$|^ОБЖ$|^История$|^Физика$|^Химия$|^Физ. лаба$|^Обществознание$)"
choice_reg = "(^Конспекты$|^Дз$)"
days_reg = "(^\d{1}$|^\d{2}$)"
action_reg = "(^Загрузить конспекты$|^Посмотреть конспекты$)"

things_reply_keyboard = [["Конспекты"]]
action_reply_keyboard = [["Загрузить конспекты", "Посмотреть конспекты"], ["Назад"], ["Выйти"]]
subjects_reply_keyboard = [["Алгебра", "Геометрия", "Мат. анализ"], ["Русский язык", "Литература", "Английский язык"],["Биология", "ОБЖ", "История"], ["Физика", "Химия", "Физ. лаба"], ["Обществознание"], ["Выйти"]]
years_reply_keyboard = [["2022", "2023", "2024"], ["Назад"], ["Выйти"]]
months_reply_keyboard = [["Сентябрь", "Октябрь", "Ноябрь"], ["Декабрь", "Январь", "Февраль"], ["Март", "Апрель", "Май"], ["Июнь", "Июль", "Август"], ["Назад"], ["Выйти"]]

user_step = 0
ACTION, SUBJECT, YEAR, MONTH, DAY, UPLOAD_PHOTOS, GET_PHOTOS, SEE_PHOTOS, RETURN_USER = range(9)
subject = ''
year = ''
month = ''
day = ''
state = 0
def main() -> None:
    application = Application.builder().token("5769101237:AAFeY_vVY9teDwm3VWqj9hWk1lz8rPiqAQ0").build()
    bot = Bot('5769101237:AAFeY_vVY9teDwm3VWqj9hWk1lz8rPiqAQ0')
    print(len(application.user_data[0]))
    #application.add_handler(MessageHandler(filters.ATTACHMENT, partial(upload, bot=bot)))
    conv_handler = ConversationHandler(entry_points=[CommandHandler("start", start), MessageHandler(filters.ALL, start)],
                                                states={ACTION: [MessageHandler(filters.Regex(choice_reg), choose_an_action)],
                                                        SUBJECT: [MessageHandler(filters.Regex(action_reg), choose_a_subject)],
                                                        YEAR: [MessageHandler(filters.Regex(subjects_reg), choose_a_year)],
                                                        MONTH: [MessageHandler(filters.Regex(years_reg), choose_a_month)],
                                                        DAY: [MessageHandler(filters.Regex(months_reg), choose_a_day)],
                                                        GET_PHOTOS: [MessageHandler(filters.Regex(days_reg), partial(get_or_see_photos, bot=bot))],
                                                        UPLOAD_PHOTOS: [MessageHandler(filters.PHOTO | filters.Document.Category('image/') | filters.Document.MimeType('application/pdf') | filters.Document.MimeType('application/docx'), partial(upload_photos, bot=bot))],
                                                        }, fallbacks=[MessageHandler(filters.Regex("(^Выйти$)"), start)]) #MessageHandler(filters.Regex("(^Назад$)"), def_list[bot.get_me])
    application.add_handler(conv_handler)
    application.run_polling()

async def start(update, context) -> int:
    tempiter = copy.copy(context.user_data)
    for i in tempiter:
        del context.user_data[str(i)]
    context.user_data["step"] = 0
    context.user_data["files_list"] = list(disk.get_files())
    print()
    await update.message.reply_text("Приветствую! Выберите, пожалуйста, то, что Вам нужно", reply_markup=ReplyKeyboardMarkup(keyboard=things_reply_keyboard, one_time_keyboard=False, resize_keyboard=True))
    return ACTION

async def choose_an_action(update, context) -> int:
    context.user_data["step"]+=1
    context.user_data["choice"] = update.message.text
    await update.message.reply_text("Что вы хотите сделать?", reply_markup=ReplyKeyboardMarkup(keyboard=action_reply_keyboard, one_time_keyboard=False, resize_keyboard=True))
    return SUBJECT

async def choose_a_subject(update, context) -> int:
    context.user_data["step"]+=1
    context.user_data["action"] = update.message.text
    if context.user_data["action"] == "Посмотреть конспекты":
        subjects_exist_reply_keyboard=[]
        temp = []
        for i in context.user_data["files_list"]:
            subjects_exist_reply_keyboard.append(i['path'].split('/')[2])
        subjects_set = list(set(subjects_exist_reply_keyboard))
        subjects_exist_reply_keyboard.clear()
        for i in subjects_set:
            temp.append(i)
            if not len(temp)%3:
                subjects_exist_reply_keyboard.append(temp)
                temp = []
            elif i == subjects_set[len(subjects_set)-1]:
                subjects_exist_reply_keyboard.append(temp)
                temp = []
        subjects_exist_reply_keyboard.append(['Выйти'])
        await update.message.reply_text("Выберите предмет", reply_markup=ReplyKeyboardMarkup(keyboard=subjects_exist_reply_keyboard, one_time_keyboard=False, resize_keyboard=True))
    else:
        await update.message.reply_text("Выберите предмет", reply_markup=ReplyKeyboardMarkup(keyboard=subjects_reply_keyboard, one_time_keyboard=False, resize_keyboard=True))
    return YEAR


async def choose_a_year(update, context) -> int:
    context.user_data["step"]+=1
    context.user_data["subject"] = update.message.text
    if context.user_data["action"] == "Посмотреть конспекты":
        years_exist_reply_keyboard = []
        for i in context.user_data["files_list"]:
            if i['path'].split('/')[2] == context.user_data["subject"]:
                years_exist_reply_keyboard.append(i['path'].split('/')[3])
        years_exist_reply_keyboard = [(list(set(years_exist_reply_keyboard)))]
        years_exist_reply_keyboard.append(['Выйти'])
        await update.message.reply_text("Выберите год: ", reply_markup=ReplyKeyboardMarkup(keyboard=years_exist_reply_keyboard, one_time_keyboard=False, resize_keyboard=True))
    else:
        await update.message.reply_text("Выберите год: ", reply_markup=ReplyKeyboardMarkup(keyboard=years_reply_keyboard, one_time_keyboard=False, resize_keyboard=True))
    return MONTH

async def choose_a_month(update, context) -> int:
    context.user_data["step"]+=1
    context.user_data["year"] = update.message.text
    if context.user_data["action"] == "Посмотреть конспекты":
        months_exist_reply_keyboard = []
        temp = []
        for i in context.user_data["files_list"]:
            if i['path'].split('/')[2] == context.user_data["subject"] and i['path'].split('/')[3] == context.user_data["year"]:
                months_exist_reply_keyboard.append(i['path'].split('/')[4])
        months_set = list(set(months_exist_reply_keyboard))
        months_exist_reply_keyboard.clear()
        for i in months_set:
            temp.append(i)
            if not len(temp)%3:
                months_exist_reply_keyboard.append(temp)
                temp = []
            elif i == months_set[len(months_set)-1]:
                months_exist_reply_keyboard.append(temp)
                temp = []
        months_exist_reply_keyboard.append(['Выйти'])
        await update.message.reply_text("Выберите месяц: ", reply_markup=ReplyKeyboardMarkup(keyboard=months_exist_reply_keyboard, one_time_keyboard=False, resize_keyboard=True))
    else:
        await update.message.reply_text("Выберите месяц: ", reply_markup=ReplyKeyboardMarkup(keyboard=months_reply_keyboard, one_time_keyboard=False, resize_keyboard=True))
    return DAY

async def choose_a_day(update, context) -> int:
    context.user_data["step"]+=1
    context.user_data["month"] = update.message.text
    if context.user_data["action"] == "Посмотреть конспекты":
        days_exist_reply_keyboard = []
        temp = []
        for i in context.user_data["files_list"]:
            if i['path'].split('/')[2] == context.user_data["subject"] and i['path'].split('/')[3] == context.user_data["year"] and i['path'].split('/')[4] == context.user_data["month"]:
                days_exist_reply_keyboard.append(i['path'].split('/')[5])
        days_set = list(set(days_exist_reply_keyboard))
        days_exist_reply_keyboard.clear()
        for i in days_set:
            temp.append(i)
            if not len(temp)%5:
                days_exist_reply_keyboard.append(temp)
                temp = []
            elif i == days_set[len(days_set)-1]:
                days_exist_reply_keyboard.append(temp)
                temp = []
        days_exist_reply_keyboard.append(['Выйти'])
        await update.message.reply_text("Выберите день: ", reply_markup=ReplyKeyboardMarkup(keyboard=days_exist_reply_keyboard, one_time_keyboard=False, resize_keyboard=True))
    else:
        amount_of_days = monthrange(int(context.user_data["year"]), months_dir[context.user_data["month"]])[1]
        days_reply_keyboard = []
        temp = []
        for i in range(1, amount_of_days + 1):
            temp.append(str(i))
            if i % 5 == 0:
                days_reply_keyboard.append(temp)
                temp = []
            elif i == amount_of_days:
                days_reply_keyboard.append(temp)
                temp = []
        days_reply_keyboard.append(["Выйти"])
        await update.message.reply_text("Выберите день: ", reply_markup=ReplyKeyboardMarkup(keyboard=days_reply_keyboard, one_time_keyboard=False, resize_keyboard=True))
    return GET_PHOTOS

async def get_or_see_photos(update, context, bot) -> int:
    context.user_data["step"]+=1
    file_list = []
    context.user_data["day"] = update.message.text
    context.user_data["path"] = 'conspectbot/' + context.user_data["subject"] + '/' + context.user_data["year"] + '/' + context.user_data["month"] + '/' + context.user_data["day"]
    file_dict_list = list(disk.listdir(context.user_data["path"]))
    for i in file_dict_list:
        if (i['file']):
            file_list.append(InputMediaDocument(i['file']));

    if context.user_data["action"] == "Загрузить конспекты":
        await update.message.reply_text("Отправте в чат изображения, которые вы хотите добавить", reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад"],["Выйти"]], one_time_keyboard=False, resize_keyboard=True))
        return UPLOAD_PHOTOS
    if context.user_data["action"] == "Посмотреть конспекты":
        if not file_list:
            await update.message.reply_text("Извините, на эту дату конспекты не выложенны, попросите выложить",reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад"],["Выйти"]],one_time_keyboard=False, resize_keyboard=True))
        else:
            await update.message.reply_text(text="Вот все фото, которые мне удалось найти:", reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад"],["Выйти"]], one_time_keyboard=False, resize_keyboard=True))
            await bot.send_media_group(update.message.chat.id, file_list)
async def upload_photos(update, context, bot) -> int:
    path = 'conspectbot/' + context.user_data["subject"] + '/' + context.user_data["year"] + '/' + context.user_data["month"] + '/' + context.user_data["day"]
    if update.message.document:
            path += '/' + update.message.document.file_name
            file = await bot.get_file(update.message.document.file_id)
            disk.upload_url(file.file_path, path)
    elif update.message.photo:
            photo_file = max(update.message.photo)
            path += '/' + photo_file.file_unique_id
            file = await bot.get_file(photo_file.file_id)
            disk.upload_url(file.file_path, path)

def_list = [start, choose_an_action, choose_a_subject, choose_a_year, choose_a_month, choose_a_day, get_or_see_photos, upload_photos]

main()