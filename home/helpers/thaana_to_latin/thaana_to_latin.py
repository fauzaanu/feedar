# taken from dh2en from a js library that doesnt actually work



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


    with open("../latin_fails/latin_to_thaana.txt", "w", encoding='utf-8') as f:
        f.write(text)

    return text


def latin_to_thaana(text):
    """
    Takes latin and converts it to thaana
    """
    # for key, value in alif_compounds.items():
    #     text = text.replace(value, key)
    #     print(text)
    # for key, value in sukun_words.items():
    #     text = text.replace(value, key)
    #     print(text)
    for key, value in punctuations.items():
        text = text.replace(value, key)
        print(text)
    for key, value in consonants_l.items():
        text = text.replace(value, key)
        print(text)
    for key, value in vowels.items():
        text = text.replace(value, key)
        print(text)
    for key, value in alif_remaining.items():
        text = text.replace(key,value)
        print(text)

    with open("../latin_fails/thaana_to_latin.txt", "w", encoding='utf-8') as f:
        f.write(text)

    return text


# letting copilot do it first
if __name__ == "__main__":
    print(
        latin_to_thaana("akuru liyaane goiy")
    )
