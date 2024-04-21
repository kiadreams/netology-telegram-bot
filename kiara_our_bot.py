import os
import telebot

bot = telebot.TeleBot(os.environ["TOKEN_KIARA_BOT"])
print(os.environ)


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, f"Привет я {bot.get_my_name().name}")


@bot.message_handler(commands=["h"])
def send_h(message):
    bot.reply_to(message, "Я знаю две команды не полных!")

#
# if __name__ == "__main__":
#     print("Bot is running!")
#     bot.polling()