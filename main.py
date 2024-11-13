import Helper
from pytubefix import Search, YouTube
import telebot
import DataBase
from hello_by_time import hello_by_time
from telebot import types
import os
from telebot import formatting
import list_scroll
from keyboards import no_keyboard
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from aiogram.utils.markdown import hlink
import requests
import datetime
import subprocess

db = DataBase.DataBase()

to_sep = "!(_TOSEPATE_)!"

db.load()

client_id = '6b63e9f22cc0448080ee58c94eb9746b'
client_secret = '4668575b427e4eca83e4af35f7e19439'

BOT_TOKEN = "6917358816:AAFpLd1gzblm7u70v61BjynmDDLmVvnZ894"

GOOGLE_API = "AIzaSyDt8jSu_8VgVG2PUhu__rm6zQPXAEwHCk0"

bot = telebot.TeleBot(BOT_TOKEN)


def get_spotify():
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    spot = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return spot


sp = get_spotify()


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, hello_by_time(), parse_mode="HTML")
    if not db.is_new_user(message.chat.id):
        bot.send_message(message.chat.id, formatting.hbold("⌨️Enter the song or singer name\n") + formatting.hitalic(
            "For example: Happy nation or Ace of Base"), parse_mode="HTML")
    else:
        new_user(message)


@bot.message_handler(commands=["help"])
def send_help(message):
    bot.send_message(message.chat.id,
                     "You can use the following commands:\n\n" +
                     "1. <b>download by name</b> - <i>Download any song by its name. Just enter the name of the song in the chat.</i>\n\n" +
                     "2. <b>download by YouTube link</b> - <i>Download a song by its YouTube link. Simply paste the link in the chat.</i>\n\n"
                     , parse_mode='HTML')


@bot.message_handler()
def add_song(message):
    db.save_message(bot.send_message(message.chat.id, "🔄Loading"))
    db.allow_user(message.chat.id, False)
    if not message.text.startswith("https://"):
        db.set_songs_list(message.chat.id, Helper.Helper.get_results_by(message.text))
        show_music_list(message)
    else:
        db.save_message(bot.send_message(message.chat.id, "🥲Sorry, we can't search by links"))
    db.allow_user(message.chat.id, True)
    bot.delete_message(message.chat.id, db.get_saved_message(message.chat.id, "🔄Loading"))


def new_user(message):
    bot.send_message(message.chat.id, "🎵 Welcome to our music bot! 🎶\n\n"
                                      "You can use the following commands:\n\n" +
                     "1. <b>download by name</b> - <i>Download any song by its name. Just enter the name of the song in the chat.</i>\n\n" +
                     "2. <b>add to playlist</b> - <i>Add a channel to use it as a playlist.</i>\n\n" + "Enjoy the music! 🎧🎉"
                     , parse_mode='HTML')
    db.add_user(message.chat.id)
    with open("newUsers", "a") as f:
        f.write(f"New one user!: {message.chat.id} {message.from_user.username} {datetime.datetime.now()}\n")
    db.save()


@bot.callback_query_handler(func=lambda call: True)
def handle_button_click(call):
    if call.data.startswith("next"):
        if call.data.split(' ')[1] == "next":
            next_songs_page(call, make_music_list)
        if call.data.split(' ')[1] == "prev":
            prev_songs_page(call, make_music_list)
        if call.data.split(' ')[1] == "cancel":
            cancel_songs_page(call)
    elif call.data.startswith("donut"):
        db.set_show(call.message.chat.id)
        bot.edit_message_text("❤️Found songs", call.message.chat.id,
                              db.get_saved_message(call.message.chat.id, "❤️Found songs"),
                              reply_markup=make_music_list(call.message, db.get_show(call.message.chat.id)))
        print("!!Someone wants to donate!!")
    else:
        if db.get_allow(call.message.chat.id):
            db.allow_user(call.message.chat.id, False)
            yt_obj = YouTube(f"https://www.youtube.com/watch?v={call.data}")
            send_youtube_audio(call.message,
                               yt_obj,
                               f"https://www.youtube.com/watch?v={call.data}")
            db.allow_user(call.message.chat.id, True)


def send_youtube_audio(message, yt_obj, link):
    youtube_url = link
    user = message.chat.id
    db.save_message(bot.send_message(user, "➡️Sending", reply_markup=no_keyboard))
    song = search(yt_obj.title)
    audio = yt_obj.streams.filter().first()
    newname = song['tracks']['items'][0]['name'] + '.mp4'
    img_name = song['tracks']['items'][0]['name'] + '.jpg'
    audio.download(filename=newname)
    if download_image(sp.album(song['tracks']['items'][0]['album']['id'])['images'][0]['url'], img_name):
        with open(newname, 'rb') as audio_file:
            to_sent = ""
            if message.chat.id == 5717723469:
                to_sent += formatting.hcode("❤️‍🔥Recommended song")
            to_sent += hlink('\nspotify.link', song['tracks']['items'][0]['external_urls']['spotify']) + ' / ' + hlink(
                'youtube.link', youtube_url)
            bot.send_audio(user, audio_file,
                           caption=to_sent,
                           title=song['tracks']['items'][0]['name'], parse_mode='HTML', thumb=open(img_name, 'rb'))

            os.remove(img_name)
    else:
        with open(newname, 'rb') as audio_file:
            bot.send_audio(user, audio_file,
                           caption=hlink('song.link', song['tracks']['items'][0]['external_urls']['spotify']),
                           title=song['tracks']['items'][0]['name'], parse_mode='HTML')
    bot.delete_message(user, db.get_saved_message(message.chat.id, "➡️Sending"))
    os.remove(newname)


def show_music_list(message):
    keyboard = make_music_list(message, db.get_show(message.chat.id))
    db.save_message(bot.send_message(message.chat.id, formatting.hbold("❤️Found songs"), reply_markup=keyboard,
                                     parse_mode="HTML"))


def next_songs_page(call, func):
    list_scroll.scroll_forward(db, call)
    keyboard = func(call.message, db.get_show(call.message.chat.id))
    bot.edit_message_text(formatting.hbold("❤️Found songs"), call.message.chat.id,
                          db.get_saved_message(call.message.chat.id, "❤️Found songs"),
                          reply_markup=keyboard,
                          parse_mode="HTML")


def cancel_songs_page(call):
    bot.delete_message(call.message.chat.id, db.get_saved_message(call.message.chat.id, "❤️Found songs"))
    try:
        bot.delete_message(call.message.chat.id,
                           db.get_saved_message(call.message.chat.id, "🗂️Which channel do you wanna send it to?"))
    except Exception:
        pass
    bot.send_message(call.message.chat.id, formatting.hbold("🙃Something else?"), parse_mode="HTML")


def prev_songs_page(call, func):
    list_scroll.scroll_back(db, call)
    keyboard = func(call.message, db.get_show(call.message.chat.id))
    bot.edit_message_text(formatting.hbold("❤️Found songs"), call.message.chat.id,
                          db.get_saved_message(call.message.chat.id, "❤️Found songs"),
                          reply_markup=keyboard,
                          parse_mode="HTML")


def make_music_list(message, show):
    keyboard = types.InlineKeyboardMarkup()
    i = 0
    for video in db.get_songs_list(message.chat.id):
        if i == 5:
            break
        button = types.InlineKeyboardButton(text=video.title, callback_data=video.video_id)
        keyboard.add(button)
        i += 1
    if show:
        donate = "🦁Leobank: 4098 5844 6883 9723"
    else:
        donate = "🍩"
    keyboard.add(telebot.types.InlineKeyboardButton(text=donate, callback_data=f"donut"))
    keyboard.row(telebot.types.InlineKeyboardButton(text="⏪️", callback_data=f"next prev"),
                 telebot.types.InlineKeyboardButton(text="🚫", callback_data=f"next cancel"),
                 telebot.types.InlineKeyboardButton(text="⏩️", callback_data=f"next next"))
    return keyboard


def search(name):
    result = sp.search(q=name, limit=1)
    return result


def download_image(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
        return 1
    else:
        return 0


result = subprocess.run(["node", "node_modules/po_receiver.js"], capture_output=True, text=True)


while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
