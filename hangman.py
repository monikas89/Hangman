import PySimpleGUI as sg
import pandas as pd
import os
import random

ALPHABET = "abcdefghijklmnopqrstuvwxyz".upper()
MAX_WORD_LENGTH = 20
MAX_CATEGORIES = 12


class Hangman:

    good_answer = 0
    answer = 0

    def __init__(self, csv_folder, column_name, images_folder):
        self.csv_folder = csv_folder
        self.column_name = column_name
        self.images_folder = images_folder
        self.path_pictures = self.get_path()
        self.dictionary_categories = self.load_categories()

    # choosing files from folder: csv_folder with not empty column: column_name [candidates for categories in game]
    def load_categories(self):
        name_files = []
        for file in os.listdir(os.path.join('.', self.csv_folder)):
            if file.endswith('.csv'):
                name_files.append(file)

        dictionary_categories = {}
        for file in name_files:
            try:
                category_df = pd.read_csv(os.path.join('.', self.csv_folder, file),
                                          usecols=[self.column_name])  
                category_df = category_df[category_df[self.column_name].str.len() < MAX_WORD_LENGTH]
                for word in category_df[self.column_name]:
                    for letter in word:
                        if letter.upper() in ALPHABET:
                            break
                    else:
                        conditional = category_df[self.column_name] == word
                        category_df.drop(category_df[conditional].index, inplace=True)
                if len(category_df) > 0:
                    potential_category = file.split('.csv')
                    dictionary_categories[potential_category[0].replace('_', " ").title()] = category_df
                    if len(dictionary_categories) == MAX_CATEGORIES:
                        print("The limit of categories is {}. {} files have been selected".format(MAX_CATEGORIES,
                                                                                                  MAX_CATEGORIES))
                        break
                else:
                    print("Column {} in file {} is empty".format(self.column_name, file))
            except ValueError:
                print("File {} don't have column {}. It can't be used as category".format(file, self.column_name))
            except AttributeError:
                print('Type data of {} in file {} must be object'.format(self.column_name, file))
        return dictionary_categories

    # download PNG files from images_folder
    def get_path(self):
        dictionary_images = {}
        i = 0
        for file in os.listdir(os.path.join('.', self.images_folder)):
            if file.endswith('.png'):
                dictionary_images[i] = os.path.join('.', self.images_folder, file)
                i += 1
        return dictionary_images

    def initialize_layout(self):
        sg.theme('lightBlue')
        categories = list(self.dictionary_categories.keys())
        layout = [[sg.Text('Please choose one category:'), sg.Push(), sg.Text("", key='Text_win/lose')],
                  [sg.Button('{}'.format(category), button_color='blue') for category in categories[:4]],
                  [sg.Button('{}'.format(category), button_color='blue') for category in categories[4:8]],
                  [sg.Button('{}'.format(category), button_color='blue')
                   for category in categories[8:MAX_CATEGORIES]],
                  [sg.Text(' ', size=(2, 1), key='_{}'.format(i), font='bold') for i in range(0, MAX_WORD_LENGTH)],
                  [sg.Text("Try to guess:", key='Text_word'),
                   sg.Input(key='Input_word', disabled=True), sg.Button('Check', disabled=True)],
                  [sg.Image(self.path_pictures[0], key="Image")],
                  [sg.Button('{}'.format(letter), disabled=True, button_color='blue', size=(3, 1))
                   for letter in ALPHABET[:13]],
                  [sg.Button('{}'.format(letter), disabled=True, button_color='blue', size=(3, 1))
                   for letter in ALPHABET[13:]],
                  [sg.Text('Your score: {}/{}'.format(Hangman.good_answer, Hangman.answer), key='Score'),
                   sg.Push(), sg.Button('New game', disabled=True), sg.Button('Quit')]]
        return layout

    # the method is performed when all the correct letters are picked
    def win(self, current_word, window):   
        window['Text_win/lose'].update("You win! :) ")
        Hangman.good_answer += 1
        Hangman.answer += 1
        window['Score'].update('Your score:{}/{}'.format(self.good_answer, self.answer))
        window['Image'].update(self.path_pictures[len(self.path_pictures) - 1])
        window['Input_word'].update(disabled=True)
        window['Check'].update(disabled=True)
        window['New game'].update(disabled=False)
        for letter in ALPHABET:
            window[letter].update(disabled=True, button_color='white')
        for index in range(0, len(current_word)):
            window['_{}'.format(index)].update(current_word[index].upper(), text_color='green')

    # the method is performed when a man is hanged
    def fail(self, current_word, window):
        window['Input_word'].update(disabled=True)
        window['Text_win/lose'].update("You lose ;( ")
        window['New game'].update(disabled=False)
        Hangman.answer += 1
        window['Score'].update('Your score:{}/{}'.format(self.good_answer, self.answer))
        window['Check'].update(disabled=True)
        for letter in ALPHABET:
            window[letter].update(disabled=True)
        for i in range(0, len(list(current_word))):
            window['_{}'.format(i)].update(current_word[i].upper(), text_color='red')

    @staticmethod
    def create_underscores(word):
        word_underscores = ''
        count_letter = 0
        for element in list(word):
            if element.upper() in ALPHABET:
                word_underscores += '_'
                count_letter += 1
            else:
                word_underscores += element.upper()
        return word_underscores, count_letter

    def start_game(self):
        if len(self.dictionary_categories) == 0:
            print('No candidates for categories in {}.'.format(self.csv_folder))
        elif len(self.path_pictures) < 3:
            print('Not enough images in folder \'{}\'.'.format(self.images_folder))
        else:
            window = sg.Window('Hangman', self.initialize_layout(), element_justification='c')
            point_for_good_letter = 0
            number_image = 0
            while True:
                event, values = window.read()
                for category in self.dictionary_categories:
                    if event == '{}'.format(category):
                        current_category = category
                        # drawing a word from a selected category
                        number = random.choice(self.dictionary_categories[current_category].index)
                        current_word = self.dictionary_categories[current_category].loc[number][self.column_name]
                        current_word_underscores, count_alphabet_letter = Hangman.create_underscores(current_word)
                        window[current_category].update(disabled=True, button_color='white')
                        for category in self.dictionary_categories:
                            if category != current_category:
                                window['{}'.format(category)].update(disabled=True)
                        for i in range(0, len(current_word)):
                            window['_{}'.format(i)].update(current_word_underscores[i], text_color='green')
                        for letter in ALPHABET:
                            window[letter].update(disabled=False, button_color='Blue')
                        window['Input_word'].update('', disabled=False)
                        window['Check'].update(disabled=False)

                for letter in ALPHABET:
                    if event == '{}'.format(letter):
                        if letter.upper() in current_word.upper():
                            window[letter].update(disabled=True, button_color='white')
                            for i in range(0, len(list(current_word))):
                                if current_word[i].upper() == letter.upper():
                                    window['_{}'.format(i)].update(letter.upper(), text_color='green')
                                    point_for_good_letter += 1
                                    if point_for_good_letter == count_alphabet_letter:
                                        Hangman.win(self, current_word, window)
                        else:
                            window[letter].update(disabled=True, button_color='white')
                            number_image += 1
                            window['Image'].update(self.path_pictures[number_image])
                            if number_image == len(self.path_pictures) - 2:
                                Hangman.fail(self, current_word, window)

                if event == 'Check':
                    if values['Input_word'].upper() == current_word.upper():
                        window['Input_word'].update('')
                        Hangman.win(self, current_word, window)

                    else:
                        number_image += 1
                        window['Image'].update(self.path_pictures[number_image])
                        if number_image == len(self.path_pictures) - 2:
                            Hangman.fail(self, current_word, window)

                if event == 'New game':
                    # remove from database the guessed word
                    conditional_two = self.dictionary_categories[current_category]['Name'] == current_word
                    self.dictionary_categories[current_category].drop(self.dictionary_categories[current_category]
                                                                      [conditional_two].index, inplace=True)
                    for category in self.dictionary_categories:
                        window['{}'.format(category)].update(disabled=False, button_color='blue')
                        if len(self.dictionary_categories[category]) == 0:
                            window['{}'.format(category)].update(disabled=True, button_color='blue')
                    point_for_good_letter = 0
                    window['Text_win/lose'].update('')
                    for i in range(0, MAX_WORD_LENGTH):
                        window['_{}'.format(i)].update(' ', text_color='black')
                    number_image = 0
                    window['Image'].update(self.path_pictures[number_image])
                    for letter in ALPHABET:
                        window[letter].update(disabled=True, button_color='blue')
                    window['Input_word'].update('', disabled=True)
                    window['Check'].update(disabled=True)
                    window['New game'].update(disabled=True)

                if event == sg.WIN_CLOSED or event == 'Quit':
                    break
            window.close()


def main():
    game_app = Hangman('csv_files', 'Name', 'png_files')
    game_app.start_game()


if __name__ == '__main__':
    main()
