# taken from dh2en from a js library that doesnt actually work
# todo: make it work

vowels = {
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

sukun_words = {
    "އް": "h",
    "ސް": "s",
    "ން": "n",
    "ށް": "h",
    "ތް": "iy",
}

alif_compounds = {
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

consonants = {
    "ހ": "h",
    "ށ": "sh",
    "ނ": "n",
    "ރ": "r",
    "ބ": "b",
    "ޅ": "lh",
    "ކ": "k",
    "އ": "",
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

punctuations = {
    "]": "[",
    "[": "]",
    "\\": "\\",
    "\'": "\'",
    "،": ",",
    ".": ".",
    "/": "/",
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


def thaana_to_latin(text):
    """
    Takes thaana and converts it to latin
    """
    for key, value in sukun_words.items():
        text = text.replace(key, value)
    print("After the dv2en processing it looks like this: ", text)
    for key, value in vowels.items():
        text = text.replace(key, value)
    for key, value in alif_compounds.items():
        text = text.replace(key, value)
    for key, value in consonants.items():
        text = text.replace(key, value)
    for key, value in punctuations.items():
        text = text.replace(key, value)


    with open("latin_to_thaana.txt", "w",encoding='utf-8') as f:
        f.write(text)

    return text


def latin_to_thaana(text):
    """
    Takes latin and converts it to thaana
    """

    for key, value in consonants.items():
        text = text.replace(value, key)
    print("Consonants: ", text)

    for key, value in sukun_words.items():
        text = text.replace(value, key)

    print("Sukun: ", text)
    for key, value in vowels.items():
        text = text.replace(value, key)

    print("Vowels: ", text)
    for key, value in alif_compounds.items():
        text = text.replace(value, key)

    print("Alif Compounds: ", text)


    for key, value in punctuations.items():
        text = text.replace(value, key)

    print("punctuations: ", text)

    with open("thaana_to_latin.txt", "w",encoding='utf-8') as f:
        f.write(text)

    return text


# letting copilot do it first
if __name__ == "__main__":
    print(latin_to_thaana(
        "akuru")
    )
