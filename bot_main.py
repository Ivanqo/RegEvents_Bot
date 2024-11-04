import telebot
from create_excel import event
from database import base_promt
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
#в base_promt вписываем запрос к базе данных
#через event создаём файл участников мероприятия

bot = telebot.TeleBot('***token***')

page = 1
count = int()


@bot.callback_query_handler(func=lambda call:True)
def callback_query(call):
    req = call.data.split(',')
    global count
    global page

    events_id = base_promt(f"SELECT event_id FROM events;")
    for i in range(len(events_id)):
        events_id[i] = str(events_id[i][0])

	#Обработка кнопки - скрыть
    if req[0] == 'unseen':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        main_menu(call.message)

    #Обработка кнопки - вперед
    #Функцию нужно доделать для всех типов мероприятий! Также для случая когда page > count
    elif req[0] == 'next-page':
        #CE - creating events
        #ME - my events
        if page < count:
            n = ((page-1)*5)
            m = 5 + ((page-1)*5)
            page = page + 1
            markup = InlineKeyboardMarkup()
            if req[1] == "CE":
                data = base_promt(f"SELECT * FROM events WHERE event_id in (SELECT event_id FROM event_creations WHERE login_telegram = {call.message.chat.id}) LIMIT({m}) OFFSET({n});")
            elif req[1] == "ME":
                data = base_promt(f"SELECT * FROM events {req[1]} LIMIT({m}) OFFSET({n});")
    
            for i in range(n, m):
                if i < len(data):
                    markup.add(InlineKeyboardButton(text = f'{data[i][1]}'))

            
            markup.add(InlineKeyboardButton(text=f'<--- Назад', callback_data=f'back-page'),InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                       InlineKeyboardButton(text=f'Вперёд --->', callback_data=f'next-page'))
            markup.add(InlineKeyboardButton(text='Скрыть список', callback_data='unseen'))
            bot.edit_message_text(f'Страница {page} из {count}', reply_markup = markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    

    #Обработка кнопки - назад
    elif req[0] == 'back-page':
        if page > 1:
            page = page - 1
            markup = InlineKeyboardMarkup()
            
            markup.add(InlineKeyboardButton(text=f'<--- Назад', callback_data=f'back-page'),InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                       InlineKeyboardButton(text=f'Вперёд --->', callback_data=f'next-page'))
            markup.add(InlineKeyboardButton(text='Скрыть список', callback_data='unseen'))
            bot.edit_message_text(f'Страница {page} из {count}', reply_markup = markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
    #Обработка id мероприятия


    elif req[0] == 'actual-events':
        n = ((page-1)*5)
        m = 5 + ((page-1)*5)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        event_data = base_promt(f"SELECT * FROM events WHERE event_id = {req[1]} LIMIT({m}) OFFSET({n})")[0]
        markup = telebot.types.ReplyKeyboardMarkup()
        btn1 = telebot.types.KeyboardButton("Записаться на мероприятие")
        btn2 = telebot.types.KeyboardButton("Вернуться к списку")
        markup.row(btn1, btn2)
        bot.send_message(chat_id=call.message.chat.id, text = f"<b>Название:</b> {event_data[1]}\n<b>Участники:</b> {event_data[2]}\n<b>Описание:</b> {event_data[3]}\n<b>Дата проведения:</b> {event_data[4]}\n<b>Место проведения:</b> {event_data[5]}", parse_mode="HTML", reply_markup=markup)
        bot.register_next_step_handler(call.message, register_event, req[1])

    elif req[0] == 'my-events':
        n = ((page-1)*5)
        m = 5 + ((page-1)*5)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        event_data = base_promt(f"SELECT * FROM events WHERE event_id = {req[1]} LIMIT({m}) OFFSET({n})")[0]
        markup = telebot.types.ReplyKeyboardMarkup()
        btn1 = telebot.types.KeyboardButton("Удалить запись")
        btn2 = telebot.types.KeyboardButton("Вернуться к списку")
        markup.row(btn1, btn2)
        bot.send_message(chat_id=call.message.chat.id, text = f"<b>Название:</b> {event_data[1]}\n<b>Участники:</b> {event_data[2]}\n<b>Описание:</b> {event_data[3]}\n<b>Дата проведения:</b> {event_data[4]}\n<b>Место проведения:</b> {event_data[5]}", parse_mode="HTML", reply_markup=markup)
        bot.register_next_step_handler(call.message, delete_registration, req[1])

    elif req[0] == 'creating-events':
        n = ((page-1)*5)
        m = 5 + ((page-1)*5)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        event_data = base_promt(f"SELECT * FROM events WHERE event_id = {req[1]} LIMIT({m}) OFFSET({n})")[0]
        markup = telebot.types.ReplyKeyboardMarkup()
        btn1 = telebot.types.KeyboardButton("Получить список участников")
        btn2 = telebot.types.KeyboardButton("Отправить сообщение всем участникам")
        btn3 = telebot.types.KeyboardButton("Вернуться к списку")
        btn4 = telebot.types.KeyboardButton("Удалить мероприятие")
        markup.row(btn1, btn2)
        markup.row(btn3)
        markup.row(btn4)
        bot.send_message(chat_id=call.message.chat.id, text = f"<b>Название:</b> {event_data[1]}\n<b>Участники:</b> {event_data[2]}\n<b>Описание:</b> {event_data[3]}\n<b>Дата проведения:</b> {event_data[4]}\n<b>Место проведения:</b> {event_data[5]}", parse_mode="HTML", reply_markup=markup)
        bot.register_next_step_handler(call.message, work_with_creating, req[1])
        

@bot.message_handler(commands=['start'])
def welcome(message):
    chat_id = message.chat.id
    check = base_promt(f"SELECT login_telegram FROM users WHERE login_telegram = {chat_id}")

    if check[0][0] != chat_id:
        bot.send_message(chat_id,'Добро пожаловать в бота событий МГСУ! \nВведите своё Ф.И.О.')
        bot.register_next_step_handler(message, save_fio)
    else:
        btn1 = telebot.types.KeyboardButton("Поехали")
        markup = telebot.types.ReplyKeyboardMarkup()
        markup.row(btn1)
        bot.send_message(chat_id, 'Добро пожаловать в бота событий МГСУ!', reply_markup=markup)
        bot.register_next_step_handler(message, main_menu)

def save_fio(message):
    chat_id = message.chat.id
    fio = message.text
    bot.send_message(chat_id,
                     f'Отлично, {fio.split(' ')[1]}. Теперь укажите ИКГ (институт, курс, группа) \n Если вы преподаватель, укажите название кафедры')
    base_promt(f"INSERT INTO users(login_telegram, fio) VALUES ({chat_id}, '{fio}')")
    bot.register_next_step_handler(message, save_ikg)
    
def save_ikg(message):
    numbers = '123456'
    chat_id = message.chat.id
    ikg = message.text
    flag = 0
    for i in range(len(ikg)):
        if ikg[i] in numbers:
            flag = 1

    if flag == 0:
        base_promt(f"UPDATE users SET membership = '{ikg}', status = 'Преподаватель' WHERE login_telegram = {chat_id}")
    else:
        base_promt(f"UPDATE users SET membership = '{ikg}', status = 'Студент' WHERE login_telegram = {chat_id}")
    btn1 = telebot.types.KeyboardButton("Отправляемся")
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row(btn1)
    bot.send_message(chat_id, 'Замечательно, теперь в меню!', reply_markup=markup)
    bot.register_next_step_handler(message, main_menu)
    

def main_menu(message):
    admins = base_promt("SELECT chat_id FROM admins")[0]
    chat_id = message.chat.id
    if chat_id in admins:        
        btn1 = telebot.types.KeyboardButton("☑️Актуальные мероприятия")
        btn2 = telebot.types.KeyboardButton("☑️Мои мероприятия")
        btn3 = telebot.types.KeyboardButton("☑️Мой профиль")
        btn4 = telebot.types.KeyboardButton("☑️Создать мероприятие")
        btn5 = telebot.types.KeyboardButton("☑️Список созданных мероприятий")

        markup = telebot.types.ReplyKeyboardMarkup()
        markup.row(btn1, btn2)
        markup.row(btn3)
        markup.row(btn4,btn5)
    else:
        btn1 = telebot.types.KeyboardButton("☑️Актуальные мероприятия")
        btn2 = telebot.types.KeyboardButton("☑️Мои мероприятия")
        btn3 = telebot.types.KeyboardButton("☑️Мой профиль")
        markup = telebot.types.ReplyKeyboardMarkup()
        markup.row(btn1, btn2)
        markup.row(btn3)
    
    bot.send_message(chat_id,'Главное меню', reply_markup=markup)
    bot.register_next_step_handler(message, spisok)


def spisok(message):
    chat_id = message.chat.id

    if message.text == "☑️Актуальные мероприятия": #сделано
        list_of_event(message)

    elif message.text == "☑️Мои мероприятия":
        my_event(message)

    elif message.text == "☑️Мой профиль": #сделано
        profile(message)

    elif message.text == "☑️Создать мероприятие": #сделано
        create_event(message)

    elif message.text == "☑️Список созданных мероприятий":
        list_of_creating_events(message)
    
    elif message.text == "☑️В главное меню": #сделано
        main_menu(message)
    
    elif message.text == "☑️Изменить данные": #сделано
        changing_data(message)
    
    elif message.text == "ФИО":#сделано
        markup = telebot.types.ReplyKeyboardRemove()
        bot.send_message(chat_id, "Введите новое ФИО\n(перепроверьте перед отправкой)", reply_markup=markup)
        bot.register_next_step_handler(message,rename)
    
    elif message.text == "ИКГ/Кафедру":#сделано
        markup = telebot.types.ReplyKeyboardRemove()
        bot.send_message(chat_id, "Введите новое ИКГ/Кафедру\n(перепроверьте перед отправкой)", reply_markup=markup)
        bot.register_next_step_handler(message,remembership)
    elif message.text == "Удалить мероприятие":
        pass

        

#Функция для вывода профиля человека
def profile(message):
    chat_id = message.chat.id
    data = base_promt(f"SELECT * FROM users WHERE login_telegram = {chat_id};")
    btn1 = telebot.types.KeyboardButton("☑️Изменить данные")
    btn2 = telebot.types.KeyboardButton("☑️В главное меню")
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row(btn1, btn2)
    bot.send_message(chat_id,"Ваш профиль")
    if data[0][4] == "Студент":
            bot.send_message(chat_id, f"ФИО: {data[0][2]}\n-----------------\nИКГ:{data[0][3]}\n-----------------\nВы {data[0][4]}.",reply_markup=markup)
    else:
            bot.send_message(chat_id, f"ФИО: {data[0][2]}\n-----------------\nВаша кафедра:{data[0][3]}\n-----------------\nВы {data[0][4]}.",reply_markup=markup)
    
    bot.register_next_step_handler(message, spisok)


#------------------------------------------------------------

#Функция изменения данных в профиле
def changing_data(message):
    chat_id = message.chat.id
    btn1 = telebot.types.KeyboardButton("ФИО")
    btn2 = telebot.types.KeyboardButton("ИКГ/Кафедру")
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row(btn1, btn2)
    bot.send_message(chat_id, "Выберите что, вы хотите изменить", reply_markup=markup)
    bot.register_next_step_handler(message, spisok)

#функция перезаписи фио
def rename(message):
    base_promt(f"UPDATE users SET fio = ('{message.text}') WHERE login_telegram = {message.chat.id}")
    profile(message)

#функция перезаписи икг или кафедры
def remembership(message):
    base_promt(f"UPDATE users SET membership = ('{message.text}') WHERE login_telegram = {message.chat.id}")
    profile(message)

#------------------------------------------------------------

def create_event(message):
    chat_id = message.chat.id
    markup = telebot.types.ReplyKeyboardRemove()
    bot.send_message(chat_id, "Введите название мероприятия", reply_markup=markup)
    bot.register_next_step_handler(message, create_event_step_1)
#Далее идут функции обработчики создания мероприятия
def create_event_step_1(message):
    chat_id = message.chat.id    
    bot.send_message(chat_id, "Укажите для кого мероприятие")
    base_promt(f"INSERT INTO events(title, place) VALUES ('{message.text}', 'ввод');")
    base_promt(f"INSERT INTO event_creations(event_id,login_telegram) VALUES((SELECT event_id FROM events WHERE title = '{message.text}'), {chat_id});")
    bot.register_next_step_handler(message, create_event_step_2)

def create_event_step_2(message):
    chat_id = message.chat.id    
    bot.send_message(chat_id, "Введите описание мероприятия (до 500 символов)")
    base_promt(f"UPDATE events SET members = '{message.text}' WHERE place ='ввод' and event_id IN (SELECT event_id FROM event_creations WHERE login_telegram = {chat_id});")
    bot.register_next_step_handler(message, create_event_step_3)

def create_event_step_3(message):
    chat_id = message.chat.id    
    bot.send_message(chat_id, "Введите дату проведения\nФормат(ГГГГ-ММ-ДД)")
    base_promt(f"UPDATE events SET description = '{message.text}' WHERE place ='ввод' and event_id IN (SELECT event_id FROM event_creations WHERE login_telegram = {chat_id});")
    bot.register_next_step_handler(message, create_event_step_4)

def create_event_step_4(message):
    chat_id = message.chat.id    
    bot.send_message(chat_id, "Укажите место проведения")
    base_promt(f"UPDATE events SET date = '{message.text}' WHERE place ='ввод' and event_id IN (SELECT event_id FROM event_creations WHERE login_telegram = {chat_id});")
    bot.register_next_step_handler(message, create_event_step_end)

def create_event_step_end(message):
    chat_id = message.chat.id    
    bot.send_message(chat_id, "Замечательно, вы создали мероприятие!")
    base_promt(f"UPDATE events SET place = '{message.text}' WHERE place ='ввод' and event_id IN (SELECT event_id FROM event_creations WHERE login_telegram = {chat_id});")
    event_data = base_promt(f"SELECT * FROM events WHERE event_id = (SELECT max(event_id) FROM event_creations WHERE login_telegram = {chat_id})")
    event_data = event_data[0]
    bot.send_message(chat_id, f"<b>Название:</b> {event_data[1]}\n<b>Участники:</b> {event_data[2]}\n<b>Описание:</b> {event_data[3]}\n<b>Дата проведения:</b> {event_data[4]}\n<b>Место проведения:</b> {event_data[5]}", parse_mode="HTML")
    main_menu(message)

#------------------------------------------------------------

def list_of_event(message):
    global page
    global count
    events_data = base_promt("SELECT * FROM events;")
    count = len(events_data) // 5 + 1
    markup = InlineKeyboardMarkup()

    n = ((page-1)*5)
    m = 5 + ((page-1)*5)

    for i in range(n, m):
        if i < len(events_data):
            markup.add(InlineKeyboardButton(text = f'{events_data[i][1]}', callback_data=f'actual-events,{events_data[i][0]}'))

    markup.add(InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
               InlineKeyboardButton(text=f'Вперёд --->', callback_data=f'next-page, '))
    markup.add(InlineKeyboardButton(text='Скрыть список', callback_data='unseen'))
    bot.send_message(message.from_user.id, "<b>Список актуальных мероприятий</b>", parse_mode="HTML", reply_markup = markup)

def list_of_creating_events(message): #!Доделать
    global page
    global count
    chat_id = message.chat.id
    
    n = ((page-1)*5)
    m = 5 + ((page-1)*5)
    events_data = base_promt(f"SELECT * FROM events WHERE event_id in (SELECT event_id FROM event_creations WHERE login_telegram = {chat_id});")
    markup = InlineKeyboardMarkup()
    count = len(events_data) // 5 + 1
    
    for i in range(n, m):
        if i < len(events_data):
            markup.add(InlineKeyboardButton(text = f'{events_data[i][1]}', callback_data=f'creating-events,{events_data[i][0]}'))
    
    markup.add(InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
               InlineKeyboardButton(text=f'Вперёд --->', callback_data=f'next-page,CE'))
    markup.add(InlineKeyboardButton(text='Скрыть список', callback_data='unseen'))
    bot.send_message(chat_id, 'Список созданных мероприятий', reply_markup= markup)

#------------------------------------------------------------

def my_event(message):
    global count
    global page
    chat_id = message.chat.id
    events = base_promt(f'''
    SELECT * FROM events 
    INNER JOIN event_participants ON events.event_id = event_participants.event_id
    INNER JOIN users ON event_participants.user_id = users.user_id
    WHERE users.login_telegram = {chat_id};
    ''')

    count = len(events) // 5 + 1

    if len(events) > 0: #проверка есть ли хоть одна запись на мероприятие
        n = ((page-1)*5)
        m = 5 + ((page-1)*5)
        markup = InlineKeyboardMarkup()

        for i in range(n, m):
            if i < len(events):
                markup.add(InlineKeyboardButton(text = f'{events[i][1]}', callback_data=f'my-events,{events[i][0]}'))

        markup.add(InlineKeyboardButton(text='Скрыть', callback_data='unseen'))
        markup.add(InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                InlineKeyboardButton(text=f'Вперёд --->', callback_data=f'''next-page'''))
        bot.send_message(message.from_user.id, "Список ваших мероприятий", reply_markup = markup)
    else:
        bot.send_message(chat_id, "У вас нет записей на мероприятия")
        main_menu(message)

#------------------------------------------------------------
def register_event(message, event_id):
    if message.text == "Записаться на мероприятие":
        chat_id = message.chat.id
        check = base_promt(f"SELECT participant_id FROM event_participants WHERE event_id = {event_id} and user_id = (SELECT user_id FROM users WHERE login_telegram = {chat_id})")
        if event_id != None and check == []:
            base_promt(f"INSERT INTO event_participants(event_id, user_id) VALUES ({event_id}, (SELECT user_id FROM users WHERE login_telegram = {chat_id}))")
            bot.send_message(chat_id, "Вы <b>успешно</b> зарегистрированы на данное мероприятие!", parse_mode="HTML")
        else:
            bot.send_message(chat_id, "Вы уже <b>участник</b> данного мероприятия!", parse_mode="HTML")
        main_menu(message)
    elif message.text == "Вернуться к списку":
        markup = telebot.types.ReplyKeyboardRemove()
        bot.send_message(chat_id, 'Возврат к списку', reply_markup=markup)
        list_of_event(message)

#------------------------------------------------------------

def delete_registration(message, event_id):
    chat_id = message.chat.id
    if message.text == "Удалить запись":
        base_promt(f"DELETE FROM event_participants WHERE event_id = {event_id} and user_id = (SELECT user_id FROM users WHERE login_telegram = {chat_id})")
        bot.send_message(chat_id, '<b><i>Вы успешно отменили регистрацию!</i></b>', parse_mode="HTML")
        my_event(message)
    elif message.text == "Вернуться к списку":
        markup = telebot.types.ReplyKeyboardRemove()
        bot.send_message(chat_id, 'Возврат к списку', reply_markup=markup)
        my_event(message)

#------------------------------------------------------------

def work_with_creating(message, event_id):#Доделать уведомление пользователей о удалении Мероприятия!
    chat_id = message.chat.id
    users_id = base_promt(f'''SELECT login_telegram FROM
                                users INNER JOIN event_participants ON users.user_id = event_participants.user_id
                                WHERE event_id = {event_id};''')

    if message.text == "Получить список участников":
        doc = open(event(base_promt(
            f'''SELECT fio, membership FROM
                users
                INNER JOIN event_participants ON event_participants.user_id = users.user_id
                WHERE event_id = {event_id};'''
        )), 'rb')
        bot.send_document(chat_id, document=doc)
        bot.send_message(chat_id, "Список участников мероприятия")
        list_of_creating_events(message)

    elif message.text == "Отправить сообщение всем участникам":
        chat_id = message.chat.id
        bot.send_message(chat_id, 'Введите сообщение, которое хотите отправить', reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, message_sendler, users_id,event_id)

    elif message.text == "Вернуться к списку":
        list_of_creating_events(message)

    elif message.text == "Удалить мероприятие":
        base_promt(f"DELETE FROM event_participants WHERE event_id = {event_id}")
        base_promt(f"DELETE FROM events WHERE event_id = {event_id}")
        bot.send_message(chat_id, '<b><i>Вы успешно удалили созданное мероприятие</i></b>\nВсем записавшимся пользователям отправлено уведомление', parse_mode="HTML",reply_markup=telebot.types.ReplyKeyboardRemove())
        message_sendler(message, users_id, event_id)
        list_of_creating_events(message)

def message_sendler(message, users_id,event_id):
    chat_id = message.chat.id
    name_event = base_promt(f"SELECT title FROM events WHERE event_id = {event_id}")[0][0]

    if message.text == "Удалить мероприятие":
        for i in users_id:
            bot.send_message(i[0], text=f"Мероприятие <b>{name_event}</b> было удалено!", parse_mode="HTML")
    else:
        for i in users_id:
            bot.send_message(i[0], text=f"{message.text}\n\nСообщение участникам мероприятия: {name_event}")
        bot.send_message(chat_id, "Сообщение успешно отправлено!")
        list_of_creating_events(message)

@bot.message_handler(commands=['push'])
def time(message):
    pass



if __name__ == '__main__':
    print('Бот запущен!')
    bot.infinity_polling()
