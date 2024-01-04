from flask import Flask, render_template, request
import re

app = Flask(__name__)

user_inputs = []
valid_words = set()

# Load valid words from the text file
with open('magyar-szavak.txt', 'r') as file:
    valid_words.update(file.read().splitlines())


# This function checks if the entered text is valid or not
def check_validity(text):

    # Check if it is already written
    if text in user_inputs:
        return False

    # Check if the first letter is the same as the last words' last letter
    special_endings = ['dzs', 'cs', 'dz', 'gy', 'ly', 'ny', 'sz', 'ty', 'zs']
    if user_inputs:
        last_word = user_inputs[-1]
        check_singular = True

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

        if check_singular and last_word[-1] != text[0]:
            return False

    # Check if the word matches this regex
    pattern = re.compile(r'^[a-zA-ZöüóéőáűúíÖÜÓÉŐÁŰÚÍ]+(-[a-zA-ZöüóéőáűúíÖÜÓÉŐÁŰÚÍ]+)?$')
    return bool(pattern.match(text) and text in valid_words)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form['user_input']

        if check_validity(user_input):
            user_inputs.append(user_input)

    return render_template('index.html', user_inputs=user_inputs)


if __name__ == '__main__':
    app.run()
