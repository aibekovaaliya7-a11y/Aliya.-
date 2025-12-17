from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import random

# Вопросы и варианты
quiz_data = [
    {"question": "Что делают коты, когда никто не видит?", 
     "options": ["Строят планы по завоеванию мира", "Спят", "Играют в шахматы"], "answer": 2},

    {"question": "Лучший способ быстро проснуться утром?", 
     "options": ["Прыгать в ледяной бассейн", "Звонок будильника", "Кофе"], "answer": 0},

    {"question": "Если бы слоны могли летать, то…", 
     "options": ["Они бы стали пилотами", "Мир бы стал опаснее", "Всё равно оставались бы слонами"], "answer": 2},

    {"question": "Главное оружие программиста?", 
     "options": ["Клавиатура", "Супер-мозг", "Кофе"], "answer": 1},

    {"question": "Почему пицца круглая, а коробка квадратная?", 
     "options": ["Так задумано природой", "Так удобнее упаковывать", "Чтобы загадать философский вопрос"], "answer": 2},

    {"question": "Что первым делом сделает робот-домохозяин?", 
     "options": ["Выметет пыль", "Сварит кофе", "Начнёт учить людей жить"], "answer": 0},

    {"question": "Лучшее изобретение человечества?", 
     "options": ["Велосипед", "Интернет мемы", "Тостер"], "answer": 1},

    {"question": "Почему программисты любят темные темы?", 
     "options": ["Чтобы экономить электроэнергию", "Чтобы казаться таинственными", "Потому что светлые слишком светлые"], "answer": 2},

    {"question": "Что сказал бы робот, если бы устал?", 
     "options": ["Я выключаюсь", "Мне нужен кофе", "Ошибка 404: энергия не найдена"], "answer": 0},

    {"question": "Идеальный способ провести выходные?", 
     "options": ["Сидеть дома и смотреть сериалы", "Путешествовать по миру", "Спать 48 часов подряд"], "answer": 1},
]

# Перемешиваем варианты ответов и корректируем индекс правильного ответа
for q in quiz_data:
    options = q["options"]
    correct_answer = options[q["answer"]]
    random.shuffle(options)
    q["answer"] = options.index(correct_answer)

# Добавляем буквы A, B, C к вариантам
for q in quiz_data:
    q["options"] = [f"{chr(65+i)}. {opt}" for i, opt in enumerate(q["options"])]

# Хранилище прогресса пользователей
user_data = {}

# Команда /start_quiz
def start_quiz(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_data[user_id] = {"score": 0, "q_index": 0}
    send_question(update, context, user_id)

# Отправка вопроса
def send_question(update, context, user_id):
    q_index = user_data[user_id]["q_index"]
    if q_index < len(quiz_data):
        q = quiz_data[q_index]
        buttons = [[InlineKeyboardButton(opt, callback_data=str(i))] for i, opt in enumerate(q["options"])]
        update.message.reply_text(q["question"], reply_markup=InlineKeyboardMarkup(buttons))
    else:
        finish_quiz(update, context, user_id, from_callback=False)

# Обработка ответа
def answer(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()

    q_index = user_data[user_id]["q_index"]

    if q_index >= len(quiz_data):
        finish_quiz(query, context, user_id, from_callback=True)
        return

    selected = int(query.data)
    correct = quiz_data[q_index]["answer"]

    # Подсчёт очков
    user_data[user_id]["score"] = (lambda s: s + 1 if selected == correct else s)(user_data[user_id]["score"])

    user_data[user_id]["q_index"] += 1
    send_next_question(query, context, user_id)

def send_next_question(query, context, user_id):
    q_index = user_data[user_id]["q_index"]
    if q_index < len(quiz_data):
        q = quiz_data[q_index]
        buttons = [[InlineKeyboardButton(opt, callback_data=str(i))] for i, opt in enumerate(q["options"])]
        query.message.edit_text(q["question"], reply_markup=InlineKeyboardMarkup(buttons))
    else:
        finish_quiz(query, context, user_id, from_callback=True)

# Завершение викторины
def finish_quiz(update_or_query, context, user_id, from_callback=True):
    score = user_data[user_id]["score"]
    if score >= 9:
        place = "1 место! Отлично!"
    elif score >= 7:
        place = "2 место! Хорошо!"
    elif score == 6:
        place = "3 место! Неплохо!"
    else:
        place = "Попробуйте ещё раз!"

    text = f"Вы ответили правильно на {score} из 10.\n{place}"

    if from_callback:
        # update_or_query — это CallbackQuery
        update_or_query.message.edit_text(text)
    else:
        # update_or_query — это Update от /start_quiz
        update_or_query.message.reply_text(text)

    del user_data[user_id]

# Вставь сюда свой токен
updater = Updater("8217917375:AAEr_F1AuoE1fZb6pXRhcQm8-e907d9Wius", use_context=True)

updater.dispatcher.add_handler(CommandHandler("start_quiz", start_quiz))
updater.dispatcher.add_handler(CallbackQueryHandler(answer))

updater.start_polling()
updater.idle()