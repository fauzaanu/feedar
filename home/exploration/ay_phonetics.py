# code converted from : https://github.com/ayarse/Thaana-Transliterater
# turns out this wasnt accurate

import re


def dh2en(input):
    _vowels = {
        "ަ": "a",
        "ާ": "aa",
        "ި": "i",
        "ީ": "ee",
        "ު": "u",
        "ޫ": "oo",
        "ެ": "e",
        "ޭ": "ey",
        "ޮ": "o",
        "ޯ": "oa",
        "ް": ""
    }

    _compounds = {}

    _alif_compounds = {
        "އަ": "a",
        "އާ": "aa",
        "އި": "i",
        "އީ": "ee",
        "އު": "u",
        "އޫ": "oo",
        "އެ": "e",
        "އޭ": "ey",
        "އޮ": "o",
        "އޯ": "oa"
    }

    _consonants = {
        "ހ": "h",
        "ށ": "sh",
        "ނ": "n",
        "ރ": "r",
        "ބ": "b",
        "ޅ": "lh",
        "ކ": "k",
        "އ": "a",
        "ވ": "v",
        "މ": "m",
        "ފ": "f",
        "ދ": "dh",
        "ތ": "th",
        "ލ": "l",
        "ގ": "g",
        "ޏ": "y",
        "ސ": "s",
        "ޑ": "d",
        "ޒ": "z",
        "ޓ": "t",
        "ޔ": "y",
        "ޕ": "p",
        "ޖ": "j",
        "ޗ": "ch",
        "ޙ": "h",
        "ޚ": "kh",
        "ޛ": "z",
        "ޜ": "z",
        "ޝ": "sh"
    }

    _punctuations = {
        "]": "[",
        "[": "]",
        "\\": "\\",
        "\'": "\'",
        "،": ",",
        ".": ".",
        "/": "/",
        "÷": "",
        "}": "{",
        "{": "}",
        "|": "|",
        ":": ":",
        "\"": "\"",
        ">": "<",
        "<": ">",
        "؟": "?",
        ")": ")",
        "(": "("
    }

    def transliterate(input):
        # replace zero width non joiners
        input = re.sub(r'[\u200B-\u200D\uFEFF]', '', input)

        v = ''

        # replace words ending in shaviyani with 'ah'
        input = re.sub(r'(އަށް)\B', 'ah', input, flags=re.IGNORECASE)
        input = re.sub(r'(ށް)\B', 'h', input, flags=re.IGNORECASE)

        # replace thaa sukun with 'i'
        input = re.sub(r'(ތް)\B', 'i', input, flags=re.IGNORECASE)

        # replace words ending in alif sukun with 'eh'
        input = re.sub(r'(އެއް)\B', 'eh', input, flags=re.IGNORECASE)
        input = re.sub(r'(ެއް)\B', 'eh', input, flags=re.IGNORECASE)
        input = re.sub(r'(ިއް)\B', 'ih', input, flags=re.IGNORECASE)

        # replace alif compounds first so they don't get in the way
        for k, v in _alif_compounds.items():
            input = re.sub(k, v, input, flags=re.IGNORECASE)

        # replace words ending in alif sukun with 'ah'
        input = re.sub(r'(ައް)\B', 'ah', input, flags=re.IGNORECASE)

        # replace words ending ai bai fili
        input = re.sub(r'(ައި)\B', 'ai', input, flags=re.IGNORECASE)

        # remaining consonants
        for k, v in _consonants.items():
            input = re.sub(k, v, input)

        # vowels
        for k, v in _vowels.items():
            input = re.sub(k, v, input)

        # capitalize first letter of sentence
        input = re.sub(r'(^\s*\w|[\.\!\?]\s*\w)', lambda c: c.group().upper(), input)

        for k, p in _punctuations.items():
            input = input.replace(k, p)

        print(input)
        return input

    return transliterate(input)


if __name__ == "__main__":
    pass
