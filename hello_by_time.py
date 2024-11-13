from datetime import datetime
from telebot import formatting


def hello_by_time():
    cur_hour = datetime.now().hour + 4
    if 5 <= cur_hour <= 11:
        return formatting.hitalic("☀️Good morning!")
    elif 12 <= cur_hour <= 18:
        return formatting.hitalic("😋G'day!")
    elif 19 <= cur_hour <= 23:
        return formatting.hitalic("😎Hi there!")
    elif 0 <= cur_hour <= 4:
        return formatting.hitalic("🌘Why are you not sleeping?")
