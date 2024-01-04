from flask import request
from flask_socketio import emit
from .extensions import socketio

import re

users = {}
users_order = []
current_turn_index = 0


@socketio.on("connect")
def handle_connect():
    print("Client connected!")


@socketio.on("user_join")
def handle_user_join(username):
    print(f"User {username} joined!")
    users[username] = request.sid
    users_order.append(username)
    emit_turn_status(username)


@socketio.on("new_message")
def handle_new_message(message):
    print(f"New message: {message}")
    username = None
    for user in users:
        if users[user] == request.sid:
            username = user
    if check_validity(message) and users_order[current_turn_index] == username:
        user_inputs.append(message)
        update_turn()
        print(f"Current turn index after update: {current_turn_index}")
        emit("chat", {"message": message, "username": username}, broadcast=True)
        emit_turn_status(users_order[current_turn_index])
        emit_turn_status(username)


user_inputs = []
valid_words = set()


# Copied from the singleplayer game, checks if a word is valid or not
def check_validity(text):
    special_endings = ['dzs', 'cs', 'dz', 'gy', 'ly', 'ny', 'sz', 'ty', 'zs']

    if text in user_inputs:
        return False

    if user_inputs:
        last_word = user_inputs[-1]
        check_singular = True

        # Check for special endings
        for ending in special_endings:
            if last_word.endswith(ending):
                check_singular = False
                if ending == 'dzs':
                    if last_word[-3:] != text[:3]:
                        return False
                    break
                else:
                    if last_word[-2:] != text[:2]:
                        return False

        # Check the last character of the previous word and the first character of the current word
        if check_singular and last_word[-1] != text[0]:
            return False

    pattern = re.compile(r'^[a-zA-ZöüóéőáűúíÖÜÓÉŐÁŰÚÍ]+(-[a-zA-ZöüóéőáűúíÖÜÓÉŐÁŰÚÍ]+)?$')
    return bool(pattern.match(text) and text in valid_words)


# Load valid words from the text file
with open('szolanc_game/magyar-szavak.txt', 'r') as file:
    valid_words.update(file.read().splitlines())


# Checks if it's a players turn
def emit_turn_status(username):
    if users_order[current_turn_index] == username:
        emit("your_turn", room=users[username])
    else:
        emit("opponent_turn", room=users[username])


# Updates the turn
def update_turn():
    global current_turn_index
    current_turn_index = (current_turn_index + 1) % len(users_order)
