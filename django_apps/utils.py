from googletrans import Translator


# TODO Create translator instance only once
translator = Translator()


def translate_lv_to_eng(text_lv: str) -> str:
    """
    Translate a text from Latvian to English.

    Args:
        text_lv (str): The text to be translated from Latvian.

    Returns:
        str: The translated text in English.
    """
    return translator.translate(
        text_lv,
        src='lv',
        dest='en'
    ).text
