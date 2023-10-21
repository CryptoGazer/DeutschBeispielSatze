import os
import json

import openai
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup

OPENAI_TOKEN = os.environ["OPENAI_API_KEY_FOR_KEYWORD_BOT"]
TG_TOKEN = os.environ["TG_KEYWORD_BOT"]
openai.api_key = OPENAI_TOKEN

# response = openai.ChatCompletion.create(
#     model="gpt-3.5-turbo",
#     messages=[
#         {"role": "system", "content": "Schrieb bitte ein Satz mit dem Wort: \"Sehenswürdigkeit\""}
#     ]
# )
#
# text_response = response.get("choices")[0].get("message").get("content")
# print(text_response)

bot = Bot(TG_TOKEN)
dp = Dispatcher(bot)

SENTENCES_WORDS_INPUT = False
DIFFERENCE_WORDS_INPUT = False

REQUESTED_DIFFERENCE = ""
REQUESTED_WORD = ""

main_commands_keyboard_markup = ReplyKeyboardMarkup(resize_keyboard=True)
main_commands_keyboard_markup.add("/start", "/wordsInput", "/difference", "/description")

words_numbers_keyboard_markup = ReplyKeyboardMarkup(resize_keyboard=True)
words_numbers_keyboard_markup.add('1', '2', '3', '4', '5', '6', '7', '8', '9', '10')  # Then I'll add more (up to 10)


def get_description() -> str:
    return "<b>Dieses Bot generiert [1 - 10] Sätze mit den Wörter, die Ihnen unbekannt sind.\n" \
           "Darüber hinaus, kann man nach dem Unterschied zwischen [1 - 10] Wörtern fragen.</b>\n" \
           "<u>Sie können alle Befehle unten sehen:</u>\n\n" \
           "/start - initialisiert dieses Bot.\n" \
           "/wordsInput - mit diesem Befehl sollte man <u>zuerst</u> <b>ein unbekanntes Wort eintragen</b>.\n" \
           "<u>Dann</u> schreibt man, <b>wie viel Sätze</b> dieses Bot generieren muss: <b>[1 - 10]</b>.\n" \
           "/difference - mit diesem Befehl sollte man <b>[1 - 10] unterschiedliche Wörter</b>\n" \
           "<u>(oder Aussagen)</u> einschreiben. Bitte, <b>achten</b> Sie darauf, dass <b>alle Wörter\n" \
           "mit KOMMA mit EINEN LEERZEICHNEN (\",\") getrennt werden sollten </b>. Dann, bekommen Sie die\n" \
           "Erklärung, warum diese Wörter sich so voneinander unterscheiden.\n" \
           "/description - die Botsbeschreibung."


def get_words_input_response(word: str, sentences_number: int) -> str:
    try:
        int(sentences_number)
    except ValueError:
        return "Sie haben keinen Nummer eingeschrieben! Versuchen Sie bitte noch einmal!"
    if sentences_number not in range(1, 11):
        return f"Sie haben {sentences_number} Wörter eingetragen.\n" \
               f"Das ist mehr als 10, deswegen sollten Sie noch einmal beantragen!"

    if sentences_number == 1:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Schrieben Sie bitte einen Satz mit dem Wort: \"{word}\". "
                                              f"Numerieren Sie diese Sätze bitte auch!"}
            ]
        )
    else:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Schrieb bitte {sentences_number} Sätze mit dem Wort: \"{word}\". "
                                              f"Numerieren Sie diese Sätze bitte auch!"}
            ]
        )
    return response.get("choices")[0].get("message").get("content")


def get_difference_response(words: str) -> str:
    if len(words.split(',')) > 10:
        return "Das Bot kann mehr als 10 Wörter nicht vergleichen!\n" \
               "Versuchen Sie bitte noch einmal und berücksichtigen Sie bitte die Anzahl der Sätze!"
    if len(words.split(',')) == 1:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Schreiben Sie mir bitte, was: \"{words}\" bedeutet?"}
            ]
        )
    else:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Erklaären Sie mir bitte den Unterschied zwischen: \"{words}\"?"}
            ]
        )
    return response.get("choices")[0].get("message").get("content")


async def on_startup(_) -> None:
    print("\n...\n\tHere we go\n...\n")


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.answer("<b>Herzlich willkommen zu diesem Bot!</b>\n"
                         "Hier können Sie die Erklärungen verschiedenen Wörter erfahren!",
                         parse_mode="HTML", reply_markup=main_commands_keyboard_markup)
    await message.answer(get_description(),
                         parse_mode="HTML")


@dp.message_handler(commands=["description"])
async def description_command(message: types.Message):
    await message.answer(get_description(),
                         parse_mode="HTML",
                         reply_markup=main_commands_keyboard_markup)


@dp.message_handler(commands=["wordsInput"])
async def words_input_command(message: types.Message):
    global SENTENCES_WORDS_INPUT

    await message.answer("Bitte, tragen Sie <b>ein Wort oder eine Aussage</b> ein, die Ihnen unbekannt sind:",
                         parse_mode="HTML",
                         reply_markup=main_commands_keyboard_markup)
    SENTENCES_WORDS_INPUT = True


@dp.message_handler(commands=["difference"])
async def difference_command(message: types.Message):
    global DIFFERENCE_WORDS_INPUT

    await message.answer("Bitte, tragen Sie <b>ein oder mehr (≤10)</b> Wörter, das/die Sie <b>vergleichen</b> "
                         "und dessen <b>Bedeutungen</b> Sie verstehen möchten:",
                         parse_mode="HTML",
                         reply_markup=main_commands_keyboard_markup)
    DIFFERENCE_WORDS_INPUT = True


@dp.message_handler(text='1')
async def one_sentence(message: types.Message):
    await message.answer(
        "Schreiben Sie jetzt bitte <b>nichts</b> und <b>warten</b> Sie bitte <b>auf das Ende des Programmes!</b>",
        parse_mode="HTML")
    await message.answer(get_words_input_response(REQUESTED_WORD, 1))


@dp.message_handler(text='2')
async def one_sentence(message: types.Message):
    await message.answer(
        "Schreiben Sie jetzt bitte <b>nichts</b> und <b>warten</b> Sie bitte <b>auf das Ende des Programmes!</b>",
        parse_mode="HTML")
    await message.answer(get_words_input_response(REQUESTED_WORD, 2))


@dp.message_handler(text='3')
async def one_sentence(message: types.Message):
    await message.answer(
        "Schreiben Sie jetzt bitte <b>nichts</b> und <b>warten</b> Sie bitte <b>auf das Ende des Programmes!</b>",
        parse_mode="HTML")
    await message.answer(get_words_input_response(REQUESTED_WORD, 3))


@dp.message_handler(text='4')
async def one_sentence(message: types.Message):
    await message.answer(
        "Schreiben Sie jetzt bitte <b>nichts</b> und <b>warten</b> Sie bitte <b>auf das Ende des Programmes!</b>",
        parse_mode="HTML")
    await message.answer(get_words_input_response(REQUESTED_WORD, 4))


@dp.message_handler(text='5')
async def one_sentence(message: types.Message):
    await message.answer(
        "Schreiben Sie jetzt bitte <b>nichts</b> und <b>warten</b> Sie bitte <b>auf das Ende des Programmes!</b>",
        parse_mode="HTML")
    await message.answer(get_words_input_response(REQUESTED_WORD, 5))


@dp.message_handler(text='6')
async def one_sentence(message: types.Message):
    await message.answer(
        "Schreiben Sie jetzt bitte <b>nichts</b> und <b>warten</b> Sie bitte <b>auf das Ende des Programmes!</b>",
        parse_mode="HTML")
    await message.answer(get_words_input_response(REQUESTED_WORD, 6))


@dp.message_handler(text='7')
async def one_sentence(message: types.Message):
    await message.answer(
        "Schreiben Sie jetzt bitte <b>nichts</b> und <b>warten</b> Sie bitte <b>auf das Ende des Programmes!</b>",
        parse_mode="HTML")
    await message.answer(get_words_input_response(REQUESTED_WORD, 7))


@dp.message_handler(text='8')
async def one_sentence(message: types.Message):
    await message.answer(
        "Schreiben Sie jetzt bitte <b>nichts</b> und <b>warten</b> Sie bitte <b>auf das Ende des Programmes!</b>",
        parse_mode="HTML")
    await message.answer(get_words_input_response(REQUESTED_WORD, 8))


@dp.message_handler(text='9')
async def one_sentence(message: types.Message):
    await message.answer(
        "Schreiben Sie jetzt bitte <b>nichts</b> und <b>warten</b> Sie bitte <b>auf das Ende des Programmes!</b>",
        parse_mode="HTML")
    await message.answer(get_words_input_response(REQUESTED_WORD, 9))


@dp.message_handler(text='10')
async def one_sentence(message: types.Message):
    await message.answer(
        "Schreiben Sie jetzt bitte <b>nichts</b> und <b>warten</b> Sie bitte <b>auf das Ende des Programmes!</b>",
        parse_mode="HTML")
    await message.answer(get_words_input_response(REQUESTED_WORD, 10))


@dp.message_handler()
async def echo(message: types.Message):
    global SENTENCES_WORDS_INPUT
    global DIFFERENCE_WORDS_INPUT
    global REQUESTED_WORD
    global REQUESTED_DIFFERENCE

    print(f"Words input: {SENTENCES_WORDS_INPUT}")
    print(message.text)
    print(REQUESTED_WORD)
    print(f"Difference input: {DIFFERENCE_WORDS_INPUT}")

    if SENTENCES_WORDS_INPUT:
        SENTENCES_WORDS_INPUT = False
        REQUESTED_WORD = message.text
        await message.answer("Bitte, schreiben Sie bitte nun, <b>wie viel Sätze</b> dieses Bot generieren muss:",
                             parse_mode="HTML",
                             reply_markup=words_numbers_keyboard_markup)

    if DIFFERENCE_WORDS_INPUT:
        DIFFERENCE_WORDS_INPUT = False
        REQUESTED_DIFFERENCE = message.text
        await message.answer(
            "Schreiben Sie jetzt bitte <b>nichts</b> und <b>warten</b> Sie bitte <b>auf das Ende des Programmes!</b>",
            parse_mode="HTML")
        await message.answer(get_difference_response(REQUESTED_DIFFERENCE))


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
