# tried a lot of aproaches yet everything failed
# we are going the easy route and borrowing the latin converter from dhivehi.mvs exposed API
import logging
import sqlite3
import urllib
from string import ascii_letters

import requests


def latin_to_thaana(word):
    """
    Convert latin to thaana
    """
    word.encode("utf-8")
    url = "https://dhivehi.xyz/api/latin-thaana/"

    payload = {
        "type": "lt",
        "text": f"{word}"
    }

    # Encode the payload in URL-encoded format
    encoded_payload = urllib.parse.urlencode(payload)

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "PostmanRuntime/7.26.8",
        "Accept": "*/*",
    }

    # Prepare the form data
    data = {'key': 'value'}

    # Encode the form data
    encoded_data = urllib.parse.urlencode(data)
    try:
        response = requests.post(url, data=payload, headers=headers)
        logging.error(f"Converted {word} to thaana")

        return response.text
    except Exception as e:
        with open("failed_words.txt", "w", encoding='utf-8') as f:
            f.write(word)
        logging.error(f"Failed to convert {word} to thaana")
def is_dhivehi_word(word: str):
    """
    Is it a dhivehi word?
    """
    for letter in word:
        if letter in ascii_letters:
            return False

        # \u0780-\u07B1 is the range of dhivehi letters in the thaana unicode block -
        # (https://github.com/hadithmv/hadithmv.github.io/blob/ebc8c9780b9e5d9f9551ea69f06c4a2862301541/js/quranHmv-script.js#L1113)
        if letter not in [chr(i) for i in range(1920, 1970)]:  # 1920 to 1970 is the range of thaana unicode block
            return False
    return True


from dhivehi_nlp import dictionary

all_words = dictionary.get_wordlist()

next_all_words = all_words.copy()
for word in all_words:
    meanings = dictionary.get_definition(word)
    for meaning in meanings:
        words_in_meaning = meaning.split(" ")
        if words_in_meaning:
            for word in words_in_meaning:
                if is_dhivehi_word(word):
                    next_all_words.append(word)

all_words = next_all_words

# remove all duplicates
all_words = list(set(all_words))

# get all the words inside the latin db
db_location = sqlite3.connect("thaana_to_latin/data/latin.sqlite3")
cursor = db_location.cursor()
cursor.execute("SELECT word FROM words")
latin_words = cursor.fetchall()
latin_words = [word[0] for word in latin_words]
cursor.close()
db_location.close()

# remove all the words that are already in the database
all_words = [word for word in all_words if word not in latin_words]


# cursor.execute("CREATE TABLE IF NOT EXISTS words (word TEXT, latin TEXT)")
# db_location.commit()
def search_and_store(word):
    db_location = sqlite3.connect("thaana_to_latin/data/latin.sqlite3")
    cursor = db_location.cursor()

    # does the word exist in the database
    cursor.execute("SELECT * FROM words WHERE word=?", (word,))
    if cursor.fetchone():
        return


    try:
        latin = latin_to_thaana(word)
        if latin:
            cursor.execute("INSERT INTO words (word, latin) VALUES (?, ?)", (word, latin))
            db_location.commit()
            logging.error(f"Inserted word {word} into the database")
    except Exception as e:
        logging.error(f"Error inserting word {word}: {e}")
    finally:
        cursor.close()
        db_location.close()


import multiprocessing.dummy as mp

pool = mp.Pool(100)
pool.map(search_and_store, all_words)
pool.close()
pool.join()
