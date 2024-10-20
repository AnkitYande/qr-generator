import math
import sys
from PIL import Image, ImageDraw
from lookup_table import *

def create_qr_matrix(size):
    return [[None] * size for _ in range(size)]

def add_finder_pattern(matrix, top_left):
    """Add a 7x7 finder pattern to the matrix at the given top-left position."""
    pattern = [
        [1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 0, 1],
        [1, 0, 1, 1, 1, 0, 1],
        [1, 0, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1]
    ]
    for r in range(7):
        for c in range(7):
            matrix[top_left[0] + r][top_left[1] + c] = pattern[r][c]

def draw_qr(matrix, scale=10):
    """Render the QR matrix to an image."""
    size = len(matrix)
    img = Image.new('RGB', (size * scale, size * scale), 'white')
    draw = ImageDraw.Draw(img)

    for r in range(size):
        for c in range(size):
            if matrix[r][c] == 1:
                draw.rectangle(
                    [c * scale, r * scale, (c+1) * scale, (r+1) * scale], fill='black'
                )
            if matrix[r][c] == None:
                draw.rectangle(
                    [c * scale, r * scale, (c+1) * scale, (r+1) * scale], fill='blue'
                )

    img.save('qr_code.png')

# Main logic
qr_size = 21
qr_matrix = create_qr_matrix(qr_size)

# # Add finder patterns at three corners
# add_finder_pattern(qr_matrix, (0, 0))
# add_finder_pattern(qr_matrix, (0, qr_size - 7))
# add_finder_pattern(qr_matrix, (qr_size - 7, 0))

# # Add more steps here to handle data placement and error correction

# # Draw and save the QR code
# draw_qr(qr_matrix)

def encode_numeric(number):
    res = []
    while len(number) > 0:
        group = number[:3]
        group_num = int(group)
        encoding_format = '010b' if group_num > 99 else '07b' if group_num > 9 else '04b'
        res.append(format(group_num, encoding_format))
        number = number[3:]
    return res

def encode_alphanumeric(str):
    str = str.upper()
    res = []
    while len(str) > 0:
        group = str[:2]
        encoded_val = (alphanumeric_table[group[:1]] * 45 + alphanumeric_table[group[1:]]) if len(group) > 1 else alphanumeric_table[group]
        encoding_format = '011b' if len(group) > 1 else '06b'
        print(group, encoding_format, encoded_val)
        res.append(format(encoded_val, encoding_format))
        str = str[2:]
    return res

def getCharacterCountIndicator(version, message, encoding):
    encoding_format = '08b'
    if version <= 9:
        if encoding == 1: encoding_format = '010b'
        if encoding == 2: encoding_format = '09b'
        if encoding == 3: encoding_format = '08b'
    elif version <= 26:
            if encoding == 1: encoding_format = '012b'
            if encoding == 2: encoding_format = '011b'
            if encoding == 3: encoding_format = '016b'
    elif version <= 40:
            if encoding == 1: encoding_format = '014b'
            if encoding == 2: encoding_format = '013b'
            if encoding == 3: encoding_format = '016b'

    message_len = len(message)
    return format(message_len, encoding_format)


def getUserInput():
    print("QR Code Generation (Version 1-26)")
    message = input("Enter your message: ")
    encoding = int(input("What encoding mode would you like:\n 1) Numeric Mode\n 2) Alphanumeric Mode\n 3) Byte Mode\n"))
    error_correction = input("What error correction level would you like:\n L) 7% error correction\n M) 15% error correction\n Q) 25% error correction\n H) 25% error correction\n").upper()

    match encoding:
        case 1: encoded_message = encode_numeric(message)
        case 2: encoded_message = encode_alphanumeric(message)
        case 3:encoded_message = list(map(lambda char: format(ord(char), '08b'), message))
        case _:
            print("Please chose a valid encoding method")
            sys.exit()

    version = 1
    char_count = getCharacterCountIndicator(version, message, encoding)
    mode = mode_table[encoding]

    print(mode, char_count, encoded_message)

            


def main():
    getUserInput()
    draw_qr(qr_matrix)


if __name__=="__main__":
    main()

