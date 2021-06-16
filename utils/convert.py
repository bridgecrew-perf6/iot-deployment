def snake_to_camel(word: str):
    return "".join(x.capitalize() or "_" for x in word.split("_"))
