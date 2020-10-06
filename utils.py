import settings

from clarifai.rest import ClarifaiApp
from emoji import emojize
from pprint import PrettyPrinter
from telegram import ReplyKeyboardMarkup, KeyboardButton
from random import randint, choice

def play_random_numbers(user_number):
    bot_number = randint(user_number - 10, user_number + 10)
    if user_number > bot_number:
      message = f'Ваше числов {user_number}, моё {bot_number}, вы выиграли'
    elif user_number == bot_number:
      message = f'Ваше числов {user_number}, моё {bot_number}, ничья'
    else:
      message = f'Ваше числов {user_number}, моё {bot_number}, вы проиграли'
    return message

def get_smile(user_data):
    if 'emoji' not in user_data:
      smile = choice(settings.USER_EMOJI)
      return emojize(smile, use_aliases=True)
    return user_data['emoji']

def main_keyboard():
    return ReplyKeyboardMarkup([
        ['Получить мемасик', KeyboardButton(text='Мои координаты', request_location=True)]
    ])

def is_cat(file_name):
  app = ClarifaiApp(api_key=settings.CLARIFAI_API_KEY)
  model = app.public_models.general_model
  response = model.predict_by_filename(file_name, max_concepts=5)
  if response['status']['code'] == 10000:
    for concept in response['outputs'][0]['data']['concepts']:
      if concept['name']=='people':
        return True
  return False

if __name__ == '__main__':
  print(is_cat('images/python_meme_1.jpeg'))
