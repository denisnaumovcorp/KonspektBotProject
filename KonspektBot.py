from calendar import monthrange
from telegram import Update, ForceReply, Message, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, WebAppData, Bot, File
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext
import telegram.ext.filters as filters
from functools import partial
import yadisk

print('hi')
disk = yadisk.YaDisk(token="y0_AgAAAABALxVvAAhfcwAAAADNm_GdxJ2gzsdISuSJfntSvJ0Kaydd99w")
print(disk.check_token())
years = ["2022", "2023", "2024"]
months = ["Сентябрь", "Октябрь", "Ноябрь","Декабрь", "Январь", "Февраль","Март", "Апрель", "Май","Июнь", "Июль", "Август"]
months_dir = {'Январь': 1, 'Февраль': 2, 'Март': 3, 'Апрель': 4, 'Май': 5, 'Июнь': 6, 'Июль': 7, 'Август': 8,'Сентябрь': 9, 'Октябрь': 10, 'Ноябрь': 11, 'Декабрь': 12}
subjects = ["Алгебра", "Геометрия", "Русский язык", "Литература"]
days = [str(i) for i in range(1,32)]

things_reply_keybord = [["Конспекты", "Дз"]]
years_reply_keyboard = [["2022", "2023", "2024"]]
months_reply_keyboard = [["Сентябрь", "Октябрь", "Ноябрь"],["Декабрь", "Январь", "Февраль"],["Март", "Апрель", "Май"],["Июнь", "Июль", "Август"]]
subjects_reply_keybord = [["Алгебра", "Геометрия"],["Русский язык", "Литература"]]

subject = ''
year = ''
month =''
day =''
state = 0

def main() -> None:
    application = Application.builder().token("5769101237:AAFeY_vVY9teDwm3VWqj9hWk1lz8rPiqAQ0").build()

    bot = Bot('5769101237:AAFeY_vVY9teDwm3VWqj9hWk1lz8rPiqAQ0')
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT, text))
    application.add_handler(MessageHandler(filters.ATTACHMENT, partial(photo, bot=bot)))

    application.run_polling()

'''for i in years:
    disk.mkdir('conspectbot/' + i)
    for ii in months:
        disk.mkdir('conspectbot/' + i + '/' + ii)
        for iii in range(1,monthrange(int(i), months_dir[ii])[1]):
            disk.mkdir('conspectbot/' + i + '/' + ii + '/' + str(iii))
'''
async def start(update, context):
    await update.message.reply_text("Приветствую! Выберите, пожалуйста, то, что Вам нужно", reply_markup=ReplyKeyboardMarkup(keyboard = things_reply_keybord, one_time_keyboard=False, resize_keyboard=True))
async def text(update,context):
    global subject,year,month,day,state
    if update.message.text == "Конспекты":
        await update.message.reply_text("Что вы хотите сделать?", reply_markup=ReplyKeyboardMarkup(keyboard = [["Загрузить конспекты","Посмотреть конспекты"]], one_time_keyboard=False, resize_keyboard=True))
    if update.message.text == "Загрузить конспекты":
        state = 1
        await update.message.reply_text("Выберите предмет", reply_markup=ReplyKeyboardMarkup(keyboard = subjects_reply_keybord, one_time_keyboard=False, resize_keyboard=True))
    elif update.message.text == "Посмотреть конспекты":
        await update.message.reply_text("Выберите предмет", reply_markup=ReplyKeyboardMarkup(keyboard = subjects_reply_keybord, one_time_keyboard=False, resize_keyboard=True))
    if update.message.text in subjects:
        subject = update.message.text
        await update.message.reply_text("Выберите год: ", reply_markup=ReplyKeyboardMarkup(keyboard = years_reply_keyboard, one_time_keyboard=False, resize_keyboard=True))
    if update.message.text in years:
        year = update.message.text
        await update.message.reply_text("Выберите месяц: ", reply_markup=ReplyKeyboardMarkup(keyboard = months_reply_keyboard, one_time_keyboard=False, resize_keyboard=True))
    if update.message.text in months:
        month = update.message.text
        amount_of_days = monthrange(int(year), months_dir[month])[1]
        reply_keyboard = []
        temp = []
        for i in range(1, amount_of_days+1):
            temp.append(i)
            if i % 5 == 0:
                reply_keyboard.append(temp)
                temp = []
            elif i == amount_of_days:
                reply_keyboard.append(temp)
                temp = []
        await update.message.reply_text("Выберите день: ", reply_markup=ReplyKeyboardMarkup(keyboard = reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    if update.message.text in days:
        day = update.message.text
        if state:
            await update.message.reply_text("Отправте в чат изображения, которые вы хотите добавить")
            #while()
        #else:
async def photo(update, context, bot):
    #path = 'pictures/' + year + '/' + month + '/' + str(day) + '/' + update.message.document.file_name
    file = await bot.get_file(update.message.document.file_id)
    print(dir(file))
    disk.upload_url(file.file_path,'conspectbot/123')
    
main()
