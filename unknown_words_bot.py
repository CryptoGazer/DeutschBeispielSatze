import os
import re
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

IS_STARTED = False
SENTENCES_WORDS_INPUT = False
DIFFERENCE_WORDS_INPUT = False
MEANING_WORD_INPUT = False

REQUESTED_DIFFERENCE = ""
REQUESTED_WORD = ""

main_commands_keyboard_markup = ReplyKeyboardMarkup(resize_keyboard=True)
main_commands_keyboard_markup.add("/start", "/wordsInput", "/difference", "/description", "/meaning")

words_numbers_keyboard_markup = ReplyKeyboardMarkup(resize_keyboard=True)
words_numbers_keyboard_markup.add("/returnBack", '1', '2', '3', '4', '5', '6', '7', '8', '9',
                                  '10')  # Then I'll add more (up to 10)

return_back_keyboard_markup = ReplyKeyboardMarkup(resize_keyboard=True)
return_back_keyboard_markup.add("/returnBack")


def form_underlined_tags(response_words_dict: dict, input_words: list) -> str:
    response_words = response_words_dict.get("choices")[0].get("message").get("content").split()
    pure_response_words = [re.sub(r"[^\w\s]", '', response_word) for response_word in response_words]
    if len(input_words) == 1:
        for i, response_word in enumerate(pure_response_words):
            if response_word.lower() == input_words[0].lower():
                response_words[i] = f"<u>{response_word}</u>"
    else:
        for i, response_word in enumerate(pure_response_words):
            for word in input_words:
                if response_word.lower() == word.lower():
                    response_words[i] = f"<u>{response_word}</u>"
    return ' '.join(response_words)


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
                {"role": "system", "content": f"Schrieben Sie bitte nur einen Satz mit dem Wort: \"{word}\""}
            ]
        )
    else:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Schrieb bitte {sentences_number} Sätze mit dem Wort: \"{word}\". "
                                              f"Numerieren Sie diese Sätze bitte auch und beginnen mit einer neuen Linie!"}
            ]
        )
    return response.get("choices")[0].get("message").get("content")


def get_difference_response(words: str) -> str:
    sep_words = words.split(',')
    if len(sep_words) > 10:
        return "Das Bot kann mehr als 10 Wörter nicht vergleichen!\n" \
               "Versuchen Sie bitte noch einmal und berücksichtigen Sie bitte die Anzahl der Sätze!"
    if len(sep_words) == 1:
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
                {"role": "system", "content": f"Erklären Sie mir bitte den Unterschied zwischen: \"<b>{words}</b>\"?"}
            ]
        )

    return form_underlined_tags(response, sep_words)


def get_single_word_meaning(word: str) -> str:
    if len(word.split()) == 1:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Schreiben Sie mir bitte die Bedeutung des Worts \"<b>{word}\"</b>"}
            ]
        )
    else:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Schreiben Sie mir bitte die Bedeutung der Aussage \"<b>{word}\"</b>"}
            ]
        )
    return response.get("choices")[0].get("message").get("content")


async def on_startup(_) -> None:
    print("\n...\n\tHere we go\n...\n")


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    global IS_STARTED
    if not IS_STARTED:
        IS_STARTED = True
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
                         reply_markup=return_back_keyboard_markup)
    SENTENCES_WORDS_INPUT = True


@dp.message_handler(commands=["difference"])
async def difference_command(message: types.Message):
    global DIFFERENCE_WORDS_INPUT

    await message.answer("Bitte, tragen Sie <b>ein oder mehr (≤10)</b> Wörter, das/die Sie <b>vergleichen</b> "
                         "und dessen <b>Bedeutungen</b> Sie verstehen möchten:",
                         parse_mode="HTML",
                         reply_markup=return_back_keyboard_markup)
    DIFFERENCE_WORDS_INPUT = True


@dp.message_handler(commands=["meaning"])
async def meaning_command(message: types.Message):
    global MEANING_WORD_INPUT
    await message.answer(
        "Schreiben Sie bitte ein <b>unbekanntes Wort</b> oder eine <b>unbekannte Aussage</b> ein:",
        parse_mode="HTML",
        reply_markup=return_back_keyboard_markup
    )
    MEANING_WORD_INPUT = True


@dp.message_handler(commands="returnBack")
async def return_back_command(message: types.Message):
    global SENTENCES_WORDS_INPUT
    global DIFFERENCE_WORDS_INPUT
    global MEANING_WORD_INPUT

    SENTENCES_WORDS_INPUT = False
    DIFFERENCE_WORDS_INPUT = False
    MEANING_WORD_INPUT = False

    await message.answer(
        "Sie werden zum <b>Hauptmenu</b> zurückgekehrt...",
        parse_mode="HTML",
        reply_markup=main_commands_keyboard_markup
    )


@dp.message_handler(text="returnBack")
async def return_back_command_sentence(message: types.Message):
    await message.answer(
        "Sie werden zum <b>Hauptmenu</b> zurückgekehrt...",
        parse_mode="HTML",
        reply_markup=main_commands_keyboard_markup
    )


@dp.message_handler(text='1')
async def one_sentence(message: types.Message):
    print("this")
    await message.answer(
        "Schreiben Sie jetzt bitte <b>nichts</b> und <b>warten</b> Sie bitte <b>auf das Ende des Programmes!</b>",
        parse_mode="HTML")
    await message.answer(get_words_input_response(REQUESTED_WORD, 1),
                         parse_mode="HTML",
                         reply_markup=main_commands_keyboard_markup)


@dp.message_handler(text='2')
async def one_sentence(message: types.Message):
    await message.answer(
        "Schreiben Sie jetzt bitte <b>nichts</b> und <b>warten</b> Sie bitte <b>auf das Ende des Programmes!</b>",
        parse_mode="HTML")
    await message.answer(get_words_input_response(REQUESTED_WORD, 2),
                         parse_mode="HTML",
                         reply_markup=main_commands_keyboard_markup)


@dp.message_handler(text='3')
async def one_sentence(message: types.Message):
    await message.answer(
        "Schreiben Sie jetzt bitte <b>nichts</b> und <b>warten</b> Sie bitte <b>auf das Ende des Programmes!</b>",
        parse_mode="HTML")
    await message.answer(get_words_input_response(REQUESTED_WORD, 3),
                         reply_markup=main_commands_keyboard_markup)


@dp.message_handler(text='4')
async def one_sentence(message: types.Message):
    await message.answer(
        "Schreiben Sie jetzt bitte <b>nichts</b> und <b>warten</b> Sie bitte <b>auf das Ende des Programmes!</b>",
        parse_mode="HTML")
    await message.answer(get_words_input_response(REQUESTED_WORD, 4),
                         reply_markup=main_commands_keyboard_markup)


@dp.message_handler(text='5')
async def one_sentence(message: types.Message):
    await message.answer(
        "Schreiben Sie jetzt bitte <b>nichts</b> und <b>warten</b> Sie bitte <b>auf das Ende des Programmes!</b>",
        parse_mode="HTML")
    await message.answer(get_words_input_response(REQUESTED_WORD, 5),
                         reply_markup=main_commands_keyboard_markup)


@dp.message_handler(text='6')
async def one_sentence(message: types.Message):
    await message.answer(
        "Schreiben Sie jetzt bitte <b>nichts</b> und <b>warten</b> Sie bitte <b>auf das Ende des Programmes!</b>",
        parse_mode="HTML")
    await message.answer(get_words_input_response(REQUESTED_WORD, 6),
                         reply_markup=main_commands_keyboard_markup)


@dp.message_handler(text='7')
async def one_sentence(message: types.Message):
    await message.answer(
        "Schreiben Sie jetzt bitte <b>nichts</b> und <b>warten</b> Sie bitte <b>auf das Ende des Programmes!</b>",
        parse_mode="HTML")
    await message.answer(get_words_input_response(REQUESTED_WORD, 7),
                         reply_markup=main_commands_keyboard_markup)


@dp.message_handler(text='8')
async def one_sentence(message: types.Message):
    await message.answer(
        "Schreiben Sie jetzt bitte <b>nichts</b> und <b>warten</b> Sie bitte <b>auf das Ende des Programmes!</b>",
        parse_mode="HTML")
    await message.answer(get_words_input_response(REQUESTED_WORD, 8),
                         reply_markup=main_commands_keyboard_markup)


@dp.message_handler(text='9')
async def one_sentence(message: types.Message):
    await message.answer(
        "Schreiben Sie jetzt bitte <b>nichts</b> und <b>warten</b> Sie bitte <b>auf das Ende des Programmes!</b>",
        parse_mode="HTML")
    await message.answer(get_words_input_response(REQUESTED_WORD, 9),
                         reply_markup=main_commands_keyboard_markup)


@dp.message_handler(text='10')
async def one_sentence(message: types.Message):
    await message.answer(
        "Schreiben Sie jetzt bitte <b>nichts</b> und <b>warten</b> Sie bitte <b>auf das Ende des Programmes!</b>",
        parse_mode="HTML")
    await message.answer(get_words_input_response(REQUESTED_WORD, 10),
                         reply_markup=main_commands_keyboard_markup)


@dp.message_handler()
async def echo(message: types.Message):
    global SENTENCES_WORDS_INPUT
    global DIFFERENCE_WORDS_INPUT
    global MEANING_WORD_INPUT
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
        await message.answer(get_difference_response(REQUESTED_DIFFERENCE),
                             parse_mode="HTML",
                             reply_markup=main_commands_keyboard_markup)

    if MEANING_WORD_INPUT:
        MEANING_WORD_INPUT = False
        await message.answer(
            "Schreiben Sie jetzt bitte <b>nichts</b> und <b>warten</b> Sie bitte <b>auf das Ende des Programmes!</b>",
            parse_mode="HTML")
        await message.answer(get_single_word_meaning(message.text),
                             parse_mode="HTML",
                             reply_markup=main_commands_keyboard_markup)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
