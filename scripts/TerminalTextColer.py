import os

class ColTerm:
    HEADER = '\033[95m'      # Цвет текста: Розовый
    OKBLUE = '\033[94m'      # Цвет текста: Синий
    OKGREEN = '\033[92m'     # Цвет текста: Зеленый
    WARNING = '\033[93m'     # Цвет текста: Желтый
    ORANGE = '\033[38;5;208m'# ANSI код для оранжевого цвета
    FAIL = '\033[91m'        # Цвет текста: Красный
    ENDC = '\033[0m'         # Сброс цвета к стандартному
    BG_BLUE = '\033[44m'     # Фон: Синий
    BG_GREEN = '\033[42m'    # Фон: Зеленый
    BG_YELLOW = '\033[43m'   # Фон: Желтый


# Тексты заголовков
def terminal_print_header(text, color='\033[95m', total_length=32, space_length=8, hash_char='#', s='', f=''):
    text_colored = f' {color}{text}\033[0m '
    hash_length = (total_length - len(text)) // 2
    ender = hash_length + 1 if (hash_length * 2 + len(text)) % 2 == 1 else hash_length
    # Собираем строку
    formatted_text = f"{s}{space_length * ' '}{hash_char * hash_length}{text_colored}{hash_char * ender}{f}"
    return print(formatted_text)

def highlight_last_path_component(path, color_code):
    parts = path.split(os.sep)
    if len(parts) > 1:
        parts[-1] = f'{color_code}{parts[-1]}{ColTerm.ENDC}'
    return os.sep.join(parts)