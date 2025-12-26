from deep_translator import GoogleTranslator

def translate_to_english(text: str) -> str:
    if not text.strip():
        return text
    return GoogleTranslator(source="auto", target="en").translate(text)
