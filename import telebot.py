import telebot
from telebot import types
BOT_TOKEN = '8157373788:AAElkZZ39k2dKIy4HEPiZSFNy-r-EF4CzCY'
bot = telebot.TeleBot(BOT_TOKEN)
volunteers = {}
projects = {}
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    register_button = types.KeyboardButton("Зарегистрироваться как волонтер")
    view_projects_button = types.KeyboardButton("Посмотреть доступные проекты")
    markup.add(register_button, view_projects_button)
    bot.reply_to(message,
                 "Привет! Я бот для управления волонтерскими проектами.\n"
                 "Используйте команды ниже:\n"
                 "/register - Зарегистрироваться как волонтер\n"
                 "/projects - Посмотреть доступные проекты\n"
                 "/help - Показать это сообщение",
                 reply_markup=markup)
@bot.message_handler(func=lambda message: message.text == "Зарегистрироваться как волонтер" or message.text == "/register")
def register_volunteer(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Пожалуйста, введите ваше имя:")
    bot.register_next_step_handler(message, process_name_step)
def process_name_step(message):
    chat_id = message.chat.id
    name = message.text
    volunteers[chat_id] = {'name': name}
    bot.send_message(chat_id, "Пожалуйста, введите вашу контактную информацию (email или телефон):")
    bot.register_next_step_handler(message, process_contact_step)
def process_contact_step(message):
    chat_id = message.chat.id
    contact = message.text
    volunteers[chat_id]['contact'] = contact
    bot.send_message(chat_id, f"Спасибо за регистрацию, {volunteers[chat_id]['name']}! "
                             f"Ваша контактная информация: {volunteers[chat_id]['contact']}. "
                             "Теперь вы можете просматривать доступные проекты.")
@bot.message_handler(func=lambda message: message.text == "Посмотреть доступные проекты" or message.text == "/projects")
def view_projects(message):
    chat_id = message.chat.id
    if not projects:
        bot.send_message(chat_id, "К сожалению, сейчас нет доступных проектов.")
    else:
        project_list = "\n".join([f"- {title}: {description}" for title, description in projects.items()])
        bot.send_message(chat_id, "Доступные проекты:\n" + project_list)
@bot.message_handler(commands=['add_project'])
def add_project_command(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Пожалуйста, введите название проекта:")
    bot.register_next_step_handler(message, process_project_name_step)
def process_project_name_step(message):
    chat_id = message.chat.id
    project_name = message.text
    projects[project_name] = {}  # Создаем запись для проекта
    bot.send_message(chat_id, "Пожалуйста, введите описание проекта:")
    bot.register_next_step_handler(message, process_project_description_step, project_name=project_name)
def process_project_description_step(message, project_name):
    chat_id = message.chat.id
    project_description = message.text
    projects[project_name] = project_description  # Обновляем описание проекта
    bot.send_message(chat_id, f"Проект '{project_name}' успешно добавлен.")
if __name__ == '__main__':
    bot.infinity_polling()