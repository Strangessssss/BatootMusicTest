import json
import User


class DataBase:
    def __init__(self):
        self.users_dict = {}
        self.stuff_dict = {}

    def add_user(self, user_id):
        self.users_dict[str(user_id)] = []
        self.stuff_dict[str(user_id)] = User.User()

    def is_new_user(self, user_id):
        for user in self.users_dict.keys():
            if int(user) == user_id:
                return False
        else:
            return True

    def save_message(self, message):
        self.stuff_dict[str(message.chat.id)].saved_message[message.text] = message.id

    def get_saved_message(self, user_id, message_text):
        return self.stuff_dict[str(user_id)].saved_message[message_text]

    def allow_user(self, user_id, yon):
        self.stuff_dict[str(user_id)].allowed = yon

    def get_allow(self, user_id):
        return self.stuff_dict[str(user_id)].allowed

    def get_songs_list(self, user_id):
        return self.stuff_dict[str(user_id)].song_list

    def set_songs_list(self, user_id, song_list):
        self.stuff_dict[str(user_id)].song_list = song_list

    def set_show(self, user_id):
        self.stuff_dict[str(user_id)].show = not self.stuff_dict[str(user_id)].show

    def get_show(self, user_id):
        return self.stuff_dict[str(user_id)].show

    def set_last_song(self, user_id, song):
        self.stuff_dict[str(user_id)].last_song = song

    def get_last_song(self, user_id):
        return self.stuff_dict[str(user_id)].last_song

    def save(self):
        user_list = {}
        for user in self.users_dict.keys():
            user_list[user] = self.users_dict[user]
        with open("db", "w") as file:
            file.write(json.dumps(user_list))

    def load(self):
        self.users_dict.clear()
        with open("db", "r") as file:
            red = file.read()
        data = json.loads(red)
        for user in data.keys():
            self.users_dict[user] = data[user]

        for user in self.users_dict.keys():
            self.stuff_dict[user] = User.User()
