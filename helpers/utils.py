from telebot.types import Message


def get_user_from_message(message: Message):
    return message.from_user
