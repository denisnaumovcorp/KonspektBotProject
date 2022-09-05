from calendar import monthrange
from telegram import Update, ForceReply, Message, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, CallbackContext, ConversationHandler
import telegram.ext.filters as filters
from functools import partial
import yadisk

disk = yadisk.YaDisk(token="y0_AgAAAABALxVvAAhfcwAAAADNm_GdxJ2gzsdISuSJfntSvJ0Kaydd99w")
print(disk.check_token())
years_reg = "(^2022$|^2023$|^2024$)"
months_reg = "(^Сентябрь$|^Октябрь$|^Ноябрь$|^Декабрь$|^Январь$|^Февраль$|^Март$|^Апрель$|^Май$|^Июнь$|^Июль$|^Август$)"
months_dir = {'Январь': 1, 'Февраль': 2, 'Март': 3, 'Апрель': 4, 'Май': 5, 'Июнь': 6, 'Июль': 7, 'Август': 8, 'Сентябрь': 9, 'Октябрь': 10, 'Ноябрь': 11, 'Декабрь': 12}
subjects_reg = "(^Алгебра$|^Геометрия$|^Мат. анализ$|^Русский язык$|^Литература$|^Английский язык$|^Биология$|^ОБЖ$|^История$|^Физика$|^Химия$|^Физ. лаба$|^Обществознание$)"
choice_reg = "(^Конспекты$|^Дз$)"
days_reg = "(^\d{1}$|^\d{2}$)"
action_reg = "(^Загрузить конспекты$|^Посмотреть конспекты$)"

things_reply_keyboard = [["Конспекты", "Дз"]]
years_reply_keyboard = [["2022", "2023", "2024"]]
months_reply_keyboard = [["Сентябрь", "Октябрь", "Ноябрь"], ["Декабрь", "Январь", "Февраль"], ["Март", "Апрель", "Май"], ["Июнь", "Июль", "Август"]]
subjects_reply_keyboard = [["Алгебра", "Геометрия", "Мат. анализ"], ["Русский язык", "Литература", "Английский язык"], ["Биология", "ОБЖ", "История"], ["Физика", "Химия", "Физ. лаба"], ["Обществознание"]]

ACTION, SUBJECT, YEAR, MONTH, DAY, UPLOAD_PHOTOS, GET_PHOTOS, SEE_PHOTOS = range(8)

subject = ''
year = ''
month = ''
day = ''
state = 0

def main() -> None:
    application = Application.builder().token("5769101237:AAFeY_vVY9teDwm3VWqj9hWk1lz8rPiqAQ0").build()

    bot = Bot('5769101237:AAFeY_vVY9teDwm3VWqj9hWk1lz8rPiqAQ0')

    #application.add_handler(MessageHandler(filters.ATTACHMENT, partial(upload, bot=bot)))
    conv_handler = ConversationHandler(entry_points=[CommandHandler("start", start)],
                                                states={ACTION: [MessageHandler(filters.Regex(choice_reg), choose_an_action)],
                                                        SUBJECT: [MessageHandler(filters.Regex(action_reg), choose_a_subject)],
                                                        YEAR: [MessageHandler(filters.Regex(subjects_reg), choose_a_year)],
                                                        MONTH: [MessageHandler(filters.Regex(years_reg), choose_a_month)],
                                                        DAY: [MessageHandler(filters.Regex(months_reg), choose_a_day)],
                                                        GET_PHOTOS: [MessageHandler(filters.Regex(days_reg), partial(get_or_see_photos, bot = bot))],
                                                        UPLOAD_PHOTOS: [MessageHandler(filters.PHOTO | filters.Document.Category('image/'), partial(upload_photos, bot=bot))]}, fallbacks=[MessageHandler(filters.Regex("^Готов$"), start)])
    application.add_handler(conv_handler)


    application.run_polling()

async def start(update, context) -> int:
    await update.message.reply_text("Приветствую! Выберите, пожалуйста, то, что Вам нужно", reply_markup=ReplyKeyboardMarkup(keyboard=things_reply_keyboard, one_time_keyboard=False, resize_keyboard=True))
    return ACTION
async def choose_an_action(update, context) -> int:
    context.user_data["choice"] = update.message.text
    await update.message.reply_text("Что вы хотите сделать?", reply_markup=ReplyKeyboardMarkup(keyboard=[["Загрузить конспекты", "Посмотреть конспекты"]], one_time_keyboard=False, resize_keyboard=True))
    return SUBJECT

async def choose_a_subject(update, context) -> int:
    context.user_data["action"] = update.message.text
    await update.message.reply_text("Выберите предмет", reply_markup=ReplyKeyboardMarkup(keyboard=subjects_reply_keyboard, one_time_keyboard=False, resize_keyboard=True))
    return YEAR

async def choose_a_year(update, context) -> int:
    context.user_data["subject"] = update.message.text
    await update.message.reply_text("Выберите год: ", reply_markup=ReplyKeyboardMarkup(keyboard=years_reply_keyboard, one_time_keyboard=False, resize_keyboard=True))
    return MONTH

async def choose_a_month(update, context) -> int:
    context.user_data["year"] = update.message.text
    await update.message.reply_text("Выберите месяц: ", reply_markup=ReplyKeyboardMarkup(keyboard=months_reply_keyboard, one_time_keyboard=False, resize_keyboard=True))
    return DAY

async def choose_a_day(update, context) -> int:
    context.user_data["month"] = update.message.text
    amount_of_days = monthrange(int(context.user_data["year"]), months_dir[context.user_data["month"]])[1]
    reply_keyboard = []
    temp = []
    for i in range(1, amount_of_days + 1):
        temp.append(str(i))
        if i % 5 == 0:
            reply_keyboard.append(temp)
            temp = []
        elif i == amount_of_days:
            reply_keyboard.append(temp)
            temp = []
    await update.message.reply_text("Выберите день: ", reply_markup=ReplyKeyboardMarkup(keyboard=reply_keyboard, one_time_keyboard=False, resize_keyboard=True))
    return GET_PHOTOS
async def get_or_see_photos(update, context, bot) -> int:
    context.user_data["day"] = update.message.text
    if context.user_data["action"] == "Загрузить конспекты":
        await update.message.reply_text("Отправте в чат изображения, которые вы хотите добавить")
        return UPLOAD_PHOTOS
    if context.user_data["action"] == "Посмотреть конспекты":
        path = 'conspectbot/' + context.user_data["subject"] + '/' + context.user_data["year"] + '/' + context.user_data["month"] + '/' + context.user_data["day"]
        file_list = list(disk.listdir(path))
        for i in file_list:
            if i.file != None:
                await bot.send_photo(update.message.chat.id, i.file)

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

#async def see_photos(update, context, bot) -> int:
    #file_list = list(disk.listdir('conspectbot/'))
        #for i in file_list:
                #if i.file != None:
                    #await bot.send_photo(update.message.chat.id, i.file)

main()
