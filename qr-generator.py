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
        res.append(format(int(group), '010b'))
        number = number[3:]
    return res

def getUserInput():
    message = input("Enter your message: ")
    encoding = int(input("What encoding mode would you like:\n 1)Numeric Mode\n 2)Alphanumeric Mode\n 3)Byte Mode\n"))

    match encoding:
        case 1:
            encoded_message = encode_numeric(message)
        case 2:
            encoded_message = list(map(lambda char: alphanumeric_tabel[char], message.upper()))
        case 3:
            encoded_message = list(map(lambda char: format(ord(char), '08b'), message))
        case _:
            print("Please chose a valid encoding method")
            sys.exit()

    mode = mode_table[encoding]

    print(mode, encoded_message)

            


def main():
    getUserInput()
    draw_qr(qr_matrix)


if __name__=="__main__":
    main()

