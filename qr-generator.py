import math
import sys
from copy import deepcopy
import reedsolo
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
    if qr_version == 1: return

    start = alignment_pattern_locations[qr_version]["starting_number"]
    end = len(matrix)
    step = alignment_pattern_locations[qr_version]["increment"]
    # print("start", start, "end", end, "step", step)
    
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

def protect_reserved_areas(qr_matrix):
    size = len(qr_matrix)
    for r in range(size):
        for c in range(size):
            if(qr_matrix[r][c] == 0): qr_matrix[r][c] = 4
            if(qr_matrix[r][c] == 1): qr_matrix[r][c] = 5
    return qr_matrix

def unprotect_reserved_areas(qr_matrix):
    size = len(qr_matrix)
    for r in range(size):
        for c in range(size):
            if qr_matrix[r][c] == 4: qr_matrix[r][c] = 0
            if qr_matrix[r][c] == 5: qr_matrix[r][c] = 1
    return qr_matrix

def draw_qr(matrix, scale=10, show_outline = False, output='qr_code.png'):
    """Render the QR matrix to an image."""
    size = len(matrix)
    img = Image.new('RGB', (size * scale, size * scale), 'white')
    draw = ImageDraw.Draw(img)
    
    outline_color = 'black' if show_outline else None  # Outline only if show_outline is True

    for r in range(size):
        for c in range(size):
            if matrix[r][c] is None:
                draw.rectangle(
                    [c * scale, r * scale, (c+1) * scale, (r+1) * scale],
                    fill='blue',
                    outline=outline_color
                )
            if matrix[r][c] == 0:
                draw.rectangle(
                    [c * scale, r * scale, (c+1) * scale, (r+1) * scale],
                    fill='white',
                    outline=outline_color
                )
            if matrix[r][c] == 1:
                draw.rectangle(
                    [c * scale, r * scale, (c+1) * scale, (r+1) * scale],
                    fill='black',
                    outline=outline_color
                )
            if matrix[r][c] == 2:
                draw.rectangle(
                    [c * scale, r * scale, (c+1) * scale, (r+1) * scale],
                    fill='green',
                    outline=outline_color
                )
            if matrix[r][c] == 3:
                draw.rectangle(
                    [c * scale, r * scale, (c+1) * scale, (r+1) * scale],
                    fill='purple',
                    outline=outline_color
                )
            if matrix[r][c] == 4:
                draw.rectangle(
                    [c * scale, r * scale, (c+1) * scale, (r+1) * scale],
                    fill='#dddddd',
                    outline=outline_color
                )
            if matrix[r][c] == 5:
                draw.rectangle(
                    [c * scale, r * scale, (c+1) * scale, (r+1) * scale],
                    fill='#222222',
                    outline=outline_color
                )

    img.save(output)


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
        # print(group, encoding_format, encoded_val)
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

def eval_mask(qr_matrix):
    
    size = len(qr_matrix)

    def penalty_rule_1():
        penalty1 = 0

        # Check rows for penalties
        for row in qr_matrix:
            i, j = 0, 0
            while j < size:
                if row[i] != row[j] or j == size - 1:
                    consecutive = j - i if row[i] != row[j] else j - i + 1
                    if consecutive >= 5:
                        penalty1 += 3 + (consecutive - 5)
                    i = j
                j += 1
        temp = penalty1

        # Check columns for penalties
        for col in range(size):
            i, j = 0, 0
            while j < size:
                if qr_matrix[i][col] != qr_matrix[j][col] or j == size - 1:
                    consecutive = j - i if qr_matrix[i][col] != qr_matrix[j][col] else j - i + 1
                    if consecutive >= 5:
                        penalty1 += 3 + (consecutive - 5)
                    i = j
                j += 1

        # print("penalty1:", penalty1)
        return penalty1
    
    def penalty_rule_2():
        penalty2 = 0

        for i in range(size - 1):
            for j in range(size - 1):
                # Check if the 2x2 block starting at (i, j) is of the same color
                if (qr_matrix[i][j] == qr_matrix[i + 1][j] and
                    qr_matrix[i][j] == qr_matrix[i][j + 1] and
                    qr_matrix[i][j] == qr_matrix[i + 1][j + 1]):
                    penalty2 += 3

        # print("penalty2:", penalty2)
        return penalty2

    def penalty_rule_3():
        penalty3 = 0

        pattern_1 = [1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0]
        pattern_2 = [0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1]

        def check_pattern(seq):
            nonlocal penalty3
            for i in range(len(seq) - 10):
                if seq[i:i+11] == pattern_1 or seq[i:i+11] == pattern_2:
                    penalty3 += 40

        # Check rows
        for row in qr_matrix:
            check_pattern(row)

        # Check columns (transpose logic)
        for col_idx in range(size):
            col = [qr_matrix[row_idx][col_idx] for row_idx in range(size)]
            check_pattern(col)

        # print("penalty3:", penalty3)
        return penalty3

    def penalty_rule_4():
        # Step 1: Count the total number of modules
        total_modules = size * size
        
        # Step 2: Count the dark modules (1 represents dark)
        dark_modules = sum(1 for row in qr_matrix for cell in row if cell == 1)
        
        # Step 3: Calculate the percentage of dark modules
        dark_percentage = (dark_modules / total_modules) * 100
        
        # Step 4: Find the previous and next multiples of five
        prev_multiple_of_five = (dark_percentage // 5) * 5
        next_multiple_of_five = prev_multiple_of_five + 5 if dark_percentage % 5 != 0 else prev_multiple_of_five
        
        # Step 5: Calculate the differences from 50 and take the absolute value
        diff_prev = abs(prev_multiple_of_five - 50)
        diff_next = abs(next_multiple_of_five - 50)
        
        # Step 6: Divide the differences by 5
        penalty_prev = diff_prev // 5
        penalty_next = diff_next // 5
        
        # Step 7: Take the smallest of the two numbers and multiply by 10
        penalty4= min(penalty_prev, penalty_next) * 10
        
        # print("penalty4:", penalty4)
        return int(penalty4)
    
    penalty1 = penalty_rule_1()
    penalty2 = penalty_rule_2()
    penalty3 = penalty_rule_3()
    penalty4 = penalty_rule_4()
    penalty = penalty1 + penalty2 + penalty3 + penalty4
    print("Penalty", penalty)
    return penalty    


def find_best_mask(old_matrix):
    global qr_matrix
    bestIdx = -1
    bestScore = math.inf
    for i in range(0,8):
        temp_matrix = deepcopy(old_matrix)
        temp_matrix = apply_mask(temp_matrix, i)
        temp_matrix = unprotect_reserved_areas(temp_matrix)
        draw_qr(temp_matrix, show_outline=True, output='qr_code_'+str(i)+'.png')
        score = eval_mask(temp_matrix)
        if(score < bestScore):
            bestScore = score
            bestIdx = i
    
    print("bestIdx", bestIdx)
    temp_matrix = deepcopy(old_matrix)
    temp_matrix = apply_mask(temp_matrix, bestIdx)
    temp_matrix = unprotect_reserved_areas(temp_matrix)
    qr_matrix = temp_matrix
    return bestIdx


def apply_mask(qr_matrix, maskVersion):
   
    size = len(qr_matrix)
    for r in range(size):
        for c in range(size):

            if not (qr_matrix[r][c] == 0 or qr_matrix[r][c] == 1):
                continue

            match maskVersion:
                case 0:
                    if ((r+c) % 2) == 0:
                        qr_matrix[r][c] = int(not qr_matrix[r][c])
                case 1:
                    if (r % 2) == 0 :
                        qr_matrix[r][c] = int(not qr_matrix[r][c])
                case 2:
                    if (c % 3) == 0 :
                        qr_matrix[r][c] = int(not qr_matrix[r][c])
                case 3:
                    if ((r+c) % 3) == 0 :
                        qr_matrix[r][c] = int(not qr_matrix[r][c])
                case 4:
                    if ((r//2 + c//3) % 2) == 0 :
                        qr_matrix[r][c] = int(not qr_matrix[r][c])
                case 5:
                    if (((r * c) % 2) + ((r * c) % 3)) == 0:
                        qr_matrix[r][c] = int(not qr_matrix[r][c])
                case 6:
                    if (((r * c) % 2) + ((r * c) % 3)) % 2 == 0:
                        qr_matrix[r][c] = int(not qr_matrix[r][c])
                case 7:
                    if (((r + c) % 2) + ((r * c) % 3)) % 2 == 0:
                        qr_matrix[r][c] = int(not qr_matrix[r][c])
                case _:
                    print("ERROR: mask version not provided")
                    return
    
    return qr_matrix


def place_data_bits(data_bits):
    global qr_matrix
    rows = len(qr_matrix)
    cols = len(qr_matrix[0])
    direction = -1  # -1 for up, 1 for down
    bit_index = 0

    for col in range(cols - 1, -1, -2):
        # Skip the vertical timing pattern
        if col == 6:
            col -= 1

        # Process the two-column segment
        current_col_range = [col, col - 1] if col - 1 >= 0 else [col]
        for row in range(rows - 1, -1, -1) if direction == -1 else range(rows):
            for current_col in current_col_range:
                if bit_index >= len(data_bits):  # Stop if all bits are placed
                    return
                if qr_matrix[row][current_col] is None:  # Place bit only in unpopulated modules
                    qr_matrix[row][current_col] = int(data_bits[bit_index])
                    bit_index += 1

        # Reverse direction after processing one set of columns
        direction *= -1

def place_format_bits(format_bits):
    global qr_matrix
    rows = len(qr_matrix) - 1
    cols = len(qr_matrix[0]) - 1

    for i in range(0,7):
        qr_matrix[8][i if i <= 5 else i+1] = int(format_bits[i])
        qr_matrix[rows-i][8] = int(format_bits[i])
    
    for i in range(7,15):
        qr_matrix[8][cols-14+i] = int(format_bits[i])
        qr_matrix[14-i if i >=9 else 15-i][8] = int(format_bits[i])

# def encode_format_string(format_string):

#     data = format_string + '0' * 10
#     format_string = list(format_string)

#     # x^10 + x^8 + x^5 + x^4 + x^2 + x + 1
#     generator_polynomial = [1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1]

#     remainder = divide_polynomial(data, generator_polynomial)

#     # Left Pad the remainder to 10 bits
#     while len(remainder) < 10:
#         remainder.insert(0, 0)

#     combined_string = format_string + remainder
#     result = ''.join(map(str, combined_string))
#     return result


# def divide_polynomial(data, generator):
#     """Perform polynomial division using XOR."""
#     current_data = data[:]  # Copy the data to avoid modifying the input
#     generator_length = len(generator)

#     while len(current_data) >= generator_length:
#         # Pad the generator polynomial with zeros to match the current data length
#         padded_generator = generator + [0] * (len(current_data) - generator_length)
#         print(current_data, padded_generator)
#         if current_data[0] == 1:  # Only divide if the leading bit is 1
#             # Perform XOR operation
#             for i in range(len(current_data)):
#                 current_data[i] ^= padded_generator[i]
#         # Remove the leading bit
#         current_data.pop(0)

#     return current_data

def errorCorrection(message_coefficients, generator_poly_size):

    # 100011101 
    reedsolo.init_tables(0x11d)
    rs = reedsolo.RSCodec(generator_poly_size)
    encoded = rs.encode(bytearray(message_coefficients))

    # separate error correction portion
    error_correction = list(encoded[-generator_poly_size:])

    return error_correction


def structureMessage(data, version, ec_level):
    message_codewords  = [data[i:i+8] for i in range(0, len(data), 8)]
    
    (g1, g1b, g2, g2b, ec_codewords) = ec_blocks_table[version][ec_level]

    g1_arr = []
    g1_ec_arr = []
    for block in range(g1):
        temp = []
        for i in range(g1b):
            word = message_codewords[block*g1b + i]
            temp.append(int(word, 2))
        g1_arr.append(temp)
        g1_ec_arr.append(errorCorrection(temp, ec_codewords))
    # print(g1_arr)
    # print(g1_ec_arr)
    
    g2_arr = []
    g2_ec_arr = []
    for block in range(g2):
        temp = []
        for i in range(g1*g1b, g1*g1b+g2b):
            word = message_codewords[block*g2b + i]
            temp.append(int(word, 2))
        g2_arr.append(temp)
        g2_ec_arr.append(errorCorrection(temp, ec_codewords))
    # print(g2_arr)
    # print(g2_ec_arr)

    combined_arr = g1_arr + g2_arr
    combined_ec_arr = g1_ec_arr + g2_ec_arr

    final_arr = []    
    for i in range(max(g1b, g2b)): 
        for block in combined_arr:
            if i < len(block):
                final_arr.append(block[i])
    for i in range(ec_codewords): 
        for block in combined_ec_arr:
            if i < len(block):
                final_arr.append(block[i])

    # convert to binary string
    final_string = ''.join(bin(num)[2:].zfill(8) for num in final_arr)
    
    # add remainder bits
    final_string += '0' * remainder_bits[version] 
    return final_string

# Main logic
qr_matrix = []

def main():
    print("QR Code Generation (Version 1-26)")
    message = input("Enter your message: ")
    encoding = int(input("What encoding mode would you like:\n 1) Numeric Mode\n 2) Alphanumeric Mode\n 3) Byte Mode\n"))
    error_correction_level = input("What error correction level would you like:\n L) 7% error correction\n M) 15% error correction\n Q) 25% error correction\n H) 25% error correction\n").upper()

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
        if(capacity_table[qr_version][error_correction_level][encoding] > len(message) ):
            break
        qr_version += 1

    char_count_code = getCharacterCountIndicator(qr_version, message, encoding)
    

    print("Generating Version " + str(qr_version) + " QR Code")
    bit_string = mode + char_count_code + "".join(encoded_message)

    padding = addPadding(bit_string, qr_version, error_correction_level)
    bit_string+=padding

    bit_string = structureMessage(bit_string, qr_version, error_correction_level)
    print("bit string:", bit_string)

    global qr_matrix
    qr_size = (((qr_version-1)*4)+21)
    qr_matrix = create_qr_matrix(qr_size)

    add_finder_patterns(qr_matrix, qr_size)
    add_alignment_patterns(qr_matrix, qr_version)
    add_timing_patterns(qr_matrix)
    add_dark_module(qr_matrix)
    add_format_info(qr_matrix)
    if(qr_version >= 7): add_version_info(qr_matrix)

    qr_matrix = protect_reserved_areas(qr_matrix)

    place_data_bits(bit_string)

    mask = find_best_mask(qr_matrix)

    format_string = format_information_bits[error_correction_level][mask]
    print("format string", format_string)
    place_format_bits(format_string)

    qr_matrix = unprotect_reserved_areas(qr_matrix)
    draw_qr(qr_matrix)


if __name__=="__main__":
    main()

