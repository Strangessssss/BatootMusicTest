def scroll_back(db, call):
    for j in range(5):
        db.get_songs_list(call.message.chat.id).insert(0, db.get_songs_list(call.message.chat.id).pop())


def scroll_forward(db, call):
    for j in range(5):
        db.get_songs_list(call.message.chat.id).append(db.get_songs_list(str(call.message.chat.id))[0])
        db.get_songs_list(call.message.chat.id).pop(0)
