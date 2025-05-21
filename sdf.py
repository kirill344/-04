import telebot
from telebot import types
import datetime
import time
BOT_TOKEN = '8157373788:AAElkZZ39k2dKIy4HEPiZSFNy-r-EF4CzCY'
bot = telebot.TeleBot(BOT_TOKEN)
projects = {}
volunteer_requests = {}
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    item1 = types.KeyboardButton("Создать проект")
    item2 = types.KeyboardButton("Список проектов")
    item3 = types.KeyboardButton("Помощь")
    markup.add(item1, item2, item3)

    bot.send_message(message.chat.id, """
Привет! Я бот для управления волонтерскими проектами.
Я могу помочь вам:
- Создавать новые волонтерские проекты.
- Просматривать список существующих проектов.
- Присоединяться к проектам в качестве волонтера.

/start - начать работу или перезапустить бота
/help - получить справку
""", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Помощь")
def help_message(message):
     bot.reply_to(message, """
Я бот для управления волонтерскими проектами.
Я могу помочь вам:
- Создавать новые волонтерские проекты.
- Просматривать список существующих проектов.
- Присоединяться к проектам в качестве волонтера.

/start - начать работу или перезапустить бота
/help - получить справку
""")

@bot.message_handler(commands=['create_project'])
@bot.message_handler(func=lambda message: message.text == "Создать проект")
def create_project_command(message):
    bot.send_message(message.chat.id, "Давайте создадим новый проект!  Как он называется?")
    bot.register_next_step_handler(message, get_project_name)

def get_project_name(message):
    project_name = message.text
    projects[project_name] = {}  # Создаем запись для проекта
    projects[project_name]['creator_id'] = message.from_user.id #Сохраняем ID создателя.
    bot.send_message(message.chat.id, f"Отлично! Теперь, пожалуйста, опишите проект '{project_name}'.")
    bot.register_next_step_handler(message, get_project_description, project_name)

def get_project_description(message, project_name):
    project_description = message.text
    projects[project_name]['description'] = project_description
    bot.send_message(message.chat.id, f"Окей. Укажите дату начала проекта (в формате ГГГГ-ММ-ДД).")
    bot.register_next_step_handler(message, get_project_start_date, project_name)

def get_project_start_date(message, project_name):
    try:
        start_date = datetime.datetime.strptime(message.text, '%Y-%m-%d').date()
        projects[project_name]['start_date'] = str(start_date)
        bot.send_message(message.chat.id, f"Прекрасно! Где будет проходить проект '{project_name}'?")
        bot.register_next_step_handler(message, get_project_location, project_name)
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат даты. Пожалуйста, введите дату в формате ГГГГ-ММ-ДД.")
        bot.register_next_step_handler(message, get_project_start_date, project_name) #Повторяем шаг

def get_project_location(message, project_name):
    project_location = message.text
    projects[project_name]['location'] = project_location
    projects[project_name]['volunteers'] = [] #Список волонтеров, присоединившихся к проекту.
    bot.send_message(message.chat.id, f"Проект '{project_name}' успешно создан!\n\n"
                                      f"Название: {project_name}\n"
                                      f"Описание: {projects[project_name]['description']}\n"
                                      f"Дата начала: {projects[project_name]['start_date']}\n"
                                      f"Местоположение: {projects[project_name]['location']}")


@bot.message_handler(commands=['list_projects'])
@bot.message_handler(func=lambda message: message.text == "Список проектов")
def list_projects_command(message):
    if not projects:
        bot.send_message(message.chat.id, "Пока нет ни одного созданного проекта.")
        return

    project_list = "Список доступных проектов:\n\n"
    for project_name, project_data in projects.items():
        project_list += f"- {project_name}\n"
        project_list += f"  Описание: {project_data['description']}\n"
        project_list += f"  Дата начала: {project_data['start_date']}\n"
        project_list += f"  Местоположение: {project_data['location']}\n"
        project_list += f"  Волонтеров: {len(project_data['volunteers'])}\n\n"

        join_button = types.InlineKeyboardButton(text="Присоединиться", callback_data=f"join_{project_name}")

        info_button = types.InlineKeyboardButton(text="Информация", callback_data=f"info_{project_name}")

        if message.from_user.id == project_data['creator_id']:
            edit_button = types.InlineKeyboardButton(text="Редактировать", callback_data=f"edit_{project_name}")
        else:
            edit_button = None

        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(join_button, info_button)
        if edit_button:
            keyboard.add(edit_button)
        bot.send_message(message.chat.id, project_list, reply_markup=keyboard)
        project_list = ""
@bot.callback_query_handler(func=lambda call: call.data.startswith('join_'))
def join_project_callback(call):
    project_name = call.data[5:]
    if call.from_user.id in projects[project_name]['volunteers']:
        bot.answer_callback_query(call.id, "Вы уже являетесь участником этого проекта!")
        return
    volunteer_requests[call.from_user.id] = {'project': project_name, 'username': call.from_user.username}
    creator_id = projects[project_name]['creator_id']
    markup = types.InlineKeyboardMarkup(row_width=2)
    approve_button = types.InlineKeyboardButton(text="Одобрить", callback_data=f"approve_{call.from_user.id}_{project_name}")
    reject_button = types.InlineKeyboardButton(text="Отклонить", callback_data=f"reject_{call.from_user.id}_{project_name}")
    markup.add(approve_button, reject_button)
    bot.send_message(creator_id, f"Волонтер @{call.from_user.username} хочет присоединиться к проекту '{project_name}'.", reply_markup=markup)
    bot.answer_callback_query(call.id, "Ваша заявка отправлена на рассмотрение организатору.")
@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_'))
def approve_volunteer_callback(call):
    user_id, project_name = call.data[8:].split('_')
    user_id = int(user_id)
    if user_id in projects[project_name]['volunteers']:
         bot.answer_callback_query(call.id, "Волонтер уже является участником этого проекта!")
         return

    projects[project_name]['volunteers'].append(user_id)
    bot.send_message(user_id, f"Ваша заявка на участие в проекте '{project_name}' одобрена!")
    bot.answer_callback_query(call.id, "Вы одобрили заявку волонтера.")
    if user_id in volunteer_requests:
        del volunteer_requests[user_id]


@bot.callback_query_handler(func=lambda call: call.data.startswith('reject_'))
def reject_volunteer_callback(call):
     user_id, project_name = call.data[7:].split('_')
     user_id = int(user_id)
     bot.send_message(user_id, f"Ваша заявка на участие в проекте '{project_name}' отклонена.")
     bot.answer_callback_query(call.id, "Вы отклонили заявку волонтера.")

     if user_id in volunteer_requests:
         del volunteer_requests[user_id]


@bot.callback_query_handler(func=lambda call: call.data.startswith('info_'))
def project_info_callback(call):
    project_name = call.data[5:]
    project = projects[project_name]

    info = f"Информация о проекте '{project_name}':\n\n"
    info += f"Описание: {project['description']}\n"
    info += f"Дата начала: {project['start_date']}\n"
    info += f"Местоположение: {project['location']}\n"
    info += f"Волонтеров: {len(project['volunteers'])}\n"

    bot.send_message(call.message.chat.id, info)
    bot.answer_callback_query(call.id, "Информация о проекте")


@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_'))
def edit_project_callback(call):
    project_name = call.data[5:]
    #TODO: Реализовать редактирование проекта. Пока просто сообщение.
    bot.send_message(call.message.chat.id, "Функция редактирования в разработке.")
    bot.answer_callback_query(call.id, "Редактирование проекта")
if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Ошибка подключения: {e}.  Переподключение через 15 секунд...")
            time.sleep(15)