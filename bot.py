from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import random
import copy

# Исходные вопросы (НЕ трогаем их во время работы)
BASE_QUIZ = [
    {"question": "Что делают коты, когда никто не видит?",
     "options": ["Строят планы по завоеванию мира", "Спят", "Играют в шахматы"],
     "answer": "Играют в шахматы"},

    {"question": "Лучший способ быстро проснуться утром?",
     "options": ["Прыгать в ледяной бассейн", "Звонок будильника", "Кофе"],
     "answer": "Прыгать в ледяной бассейн"},

    {"question": "Если бы слоны могли летать, то…",
     "options": ["Они бы стали пилотами", "Мир бы стал опаснее", "Всё равно оставались бы слонами"],
     "answer": "Всё равно оставались бы слонами"},

    {"question": "Главное оружие программиста?",
     "options": ["Клавиатура", "Супер-мозг", "Кофе"],
     "answer": "Супер-мозг"},

    {"question": "Почему пицца круглая, а коробка квадратная?",
     "options": ["Так задумано природой", "Так удобнее упаковывать", "Чтобы загадать философский вопрос"],
     "answer": "Чтобы загадать философский вопрос"},

    {"question": "Что первым делом сделает робот-домохозяин?",
     "options": ["Выметет пыль", "Сварит кофе", "Начнёт учить людей жить"],
     "answer": "Выметет пыль"},

    {"question": "Лучшее изобретение человечества?",
     "options": ["Велосипед", "Интернет мемы", "Тостер"],
     "answer": "Интернет мемы"},

    {"question": "Почему программисты любят темные темы?",
     "options": ["Чтобы экономить электроэнергию", "Чтобы казаться таинственными", "Потому что светлые слишком светлые"],
     "answer": "Потому что светлые слишком светлые"},

    {"question": "Что сказал бы робот, если бы устал?",
     "options": ["Я выключаюсь", "Мне нужен кофе", "Ошибка 404: энергия не найдена"],
     "answer": "Я выключаюсь"},

    {"question": "Идеальный способ провести выходные?",
     "options": ["Сидеть дома и смотреть сериалы", "Путешествовать по миру", "Спать 48 часов подряд"],
     "answer": "Путешествовать по миру"},
]

# Хранилище данных пользователей
users = {}


def start_quiz(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    quiz = copy.deepcopy(BASE_QUIZ)
    random.shuffle(quiz)

    for q in quiz:
        random.shuffle(q["options"])

    users[user_id] = {
        "quiz": quiz,
        "index": 0,
        "score": 0
    }

    send_question(update, context, user_id)


def send_question(update, context, user_id):
    data = users[user_id]
    idx = data["index"]

    if idx >= len(data["quiz"]):
        finish_quiz(update, user_id)
        return

    q = data["quiz"][idx]

    buttons = []
    for opt in q["options"]:
        is_correct = "1" if opt == q["answer"] else "0"
        buttons.append([InlineKeyboardButton(opt, callback_data=is_correct)])

    update.message.reply_text(
        q["question"],
        reply_markup=InlineKeyboardMarkup(buttons)
    )


def answer(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()

    if user_id not in users:
        query.message.edit_text("Викторина не найдена. Запусти заново.")
        return

    if query.data == "1":
        users[user_id]["score"] += 1

    users[user_id]["index"] += 1
    send_next_question(query, user_id)


def send_next_question(query, user_id):
    data = users[user_id]
    idx = data["index"]

    if idx >= len(data["quiz"]):
        finish_quiz(query, user_id, from_callback=True)
        return

    q = data["quiz"][idx]

    buttons = []
    for opt in q["options"]:
        is_correct = "1" if opt == q["answer"] else "0"
        buttons.append([InlineKeyboardButton(opt, callback_data=is_correct)])

    query.message.edit_text(
        q["question"],
        reply_markup=InlineKeyboardMarkup(buttons)
    )


def finish_quiz(update_or_query, user_id, from_callback=False):
    score = users[user_id]["score"]

    if score >= 9:
        result = "1 место! Отлично!"
    elif score >= 7:
        result = "2 место! Хорошо!"
    elif score == 6:
        result = "3 место! Неплохо!"
    else:
        result = "Попробуй ещё раз."

    text = f"Правильных ответов: {score} из 10\n{result}"

    if from_callback:
        update_or_query.message.edit_text(text)
    else:
        update_or_query.message.reply_text(text)

    del users[user_id]


updater = Updater("8217917375:AAEr_F1AuoE1fZb6pXRhcQm8-e907d9Wius", use_context=True)

updater.dispatcher.add_handler(CommandHandler("start_quiz", start_quiz))
updater.dispatcher.add_handler(CallbackQueryHandler(answer))

updater.start_polling()
updater.idle()
