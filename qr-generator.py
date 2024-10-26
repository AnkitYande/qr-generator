import math
import sys
from PIL import Image, ImageDraw
from lookup_table import *
from character_capacity import capacity_table
from ec_table import ec_blocks_table

def create_qr_matrix(size):
    return [[None] * size for _ in range(size)]

def add_dark_module(matrix):
    matrix[-8][8] = 1

def add_format_info(matrix):
    for i in range(0,9):
        if i != 6:
            matrix[8][i] = 2
            matrix[i][8] = 2
    for i in range(len(matrix)-8,len(matrix)):
        matrix[8][i] = 2
    for i in range(len(matrix)-7,len(matrix)):
        matrix[i][8] = 2

def add_version_info(matrix):
    for i in range(len(matrix) -11, len(matrix) -8 ):
        for j in range(0,6):
            matrix[i][j] = 3
            matrix[j][i] = 3

def add_finder_patterns(qr_matrix, qr_size):
    add_finder_pattern(qr_matrix, [0,0], [1,1])
    add_finder_pattern(qr_matrix, [qr_size-8,0], [0,1])
    add_finder_pattern(qr_matrix, [0,qr_size-8], [1,0])

def add_finder_pattern(matrix, top_left, pad):
    """Add a 7x7 finder pattern to the matrix at the given top-left position."""
    """pad is used for separators"""
    pattern = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 0, 0, 0, 0, 0, 1, 0],
        [0, 1, 0, 1, 1, 1, 0, 1, 0],
        [0, 1, 0, 1, 1, 1, 0, 1, 0],
        [0, 1, 0, 1, 1, 1, 0, 1, 0],
        [0, 1, 0, 0, 0, 0, 0, 1, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]
    for r in range(8):
        for c in range(8):
            matrix[top_left[0] + r][top_left[1] + c] = pattern[r+pad[0]][c+pad[1]]

def add_alignment_patterns(matrix, qr_version):
    start = alignment_pattern_locations[qr_version]["starting_number"]
    end = len(matrix)
    step = alignment_pattern_locations[qr_version]["increment"]
    
    for i in range(start, end-8, step):
        add_alignment_pattern(matrix, [i,6])
    for i in range(start, end-8, step):
        add_alignment_pattern(matrix, [6,i])

    for i in range(start, end, step):
        for j in range(start, end, step):
            add_alignment_pattern(matrix, [i,j])

def add_alignment_pattern(matrix, top_left):
    """Add a 5x5 alignment pattern to the matrix at the given top-left position."""
    pattern = [
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 1, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1]
    ]
    for r in range(5):
        for c in range(5):
            matrix[top_left[0] - 2 + r][top_left[1] - 2 + c] = pattern[r][c]

def add_timing_patterns(matrix):
    for i in range (7, len(matrix)-7):
        matrix[6][i] = i%2==0
        matrix[i][6] = i%2==0

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
            if matrix[r][c] == 2:
                draw.rectangle(
                    [c * scale, r * scale, (c+1) * scale, (r+1) * scale], fill='green'
                )
            if matrix[r][c] == 3:
                draw.rectangle(
                    [c * scale, r * scale, (c+1) * scale, (r+1) * scale], fill='purple'
                )

    img.save('qr_code.png')


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

def addPadding(data, version, ec_level):
    padding = ""
    data_len = len(data)
    block_arr = ec_blocks_table[version][ec_level]
    required_bits = (block_arr[0] * block_arr[1] + block_arr[2] * block_arr[3]) * 8
    
    # Add terminator (up to 4 bits)
    terminator_bits = min(required_bits - data_len, 4)
    padding += '0' * terminator_bits
    data_len += terminator_bits
    
    # Pad with 0s to make the bit string length a multiple of 8
    padding_bits = (8 - (data_len % 8)) % 8
    padding += '0' * padding_bits
    data_len += padding_bits

    # Pad with alternating bytes (236 -> '11101100', 17 -> '00010001')
    pad_bytes = ['11101100', '00010001']
    pad_index = 0
    while data_len < required_bits:
        padding += pad_bytes[pad_index]
        data_len += 8
        pad_index = (pad_index + 1) % 2  # Alternate between 236 and 17
    
    return padding


def getUserInput():
    print("QR Code Generation (Version 1-26)")
    message = input("Enter your message: ")
    encoding = int(input("What encoding mode would you like:\n 1) Numeric Mode\n 2) Alphanumeric Mode\n 3) Byte Mode\n"))
    error_correction = input("What error correction level would you like:\n L) 7% error correction\n M) 15% error correction\n Q) 25% error correction\n H) 25% error correction\n").upper()

    match encoding:
        case 1: encoded_message = encode_numeric(message)
        case 2: encoded_message = encode_alphanumeric(message)
        case 3: encoded_message = list(map(lambda char: format(ord(char), '08b'), message))
        case _:
            print("Please chose a valid encoding method")
            sys.exit()

    mode = mode_table[encoding]

    qr_version = 1
    while True :
        if(capacity_table[qr_version][error_correction][encoding] > len(message) ):
            break
        qr_version += 1

    char_count_code = getCharacterCountIndicator(qr_version, message, encoding)
    

    print("Version " + str(qr_version) + ")", mode, char_count_code, encoded_message)
    bit_string = mode + char_count_code + "".join(encoded_message)

    padding = addPadding(bit_string, qr_version, error_correction)
    print(bit_string+padding)

    global qr_matrix
    qr_size = (((qr_version-1)*4)+21)
    qr_matrix = create_qr_matrix(qr_size)

    add_finder_patterns(qr_matrix, qr_size)
    add_alignment_patterns(qr_matrix, qr_version)
    add_timing_patterns(qr_matrix)
    add_dark_module(qr_matrix)
    add_format_info(qr_matrix)
    if(qr_version >= 7): 
        add_version_info(qr_matrix)


# Main logic
qr_matrix = []

def main():
    getUserInput()
    draw_qr(qr_matrix)


if __name__=="__main__":
    main()

