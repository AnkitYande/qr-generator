import sys

from lookup_tables.lookup_table import *
from lookup_tables.character_capacity_table import capacity_table
from lookup_tables.ec_table import ec_blocks_table

from draw_matrix import *
from add_qr_patterns import *
from error_correction import *
from encode_data import *
from masking import *

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

def getQRVersion(error_correction_level, encoding, message):
    qr_version = 1
    while True :
        if(capacity_table[qr_version][error_correction_level][encoding] > len(message) ):
            break
        qr_version += 1
    return qr_version

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

def place_data_bits(qr_matrix, data_bits):
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

# Interweaves data and calculates error correction 
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


def main():
    print("QR Code Generation (Version 1-26)")
    message = input("Enter your message: ")
    encoding = int(input("What encoding mode would you like:\n 1) Numeric Mode\n 2) Alphanumeric Mode\n 3) Byte Mode\n"))
    error_correction_level = input("What error correction level would you like:\n L) 7% error correction\n M) 15% error correction\n Q) 25% error correction\n H) 30% error correction\n").upper()

    match encoding:
        case 1: encoded_message = encode_numeric(message)
        case 2: encoded_message = encode_alphanumeric(message)
        case 3: encoded_message = encode_byte(message)
        case _:
            print("Please chose a valid encoding method")
            sys.exit()

    mode_code = mode_table[encoding]
    qr_version = getQRVersion(error_correction_level, encoding, message)
    char_count_code = getCharacterCountIndicator(qr_version, message, encoding)
    print("Generating Version " + str(qr_version) + " QR Code")

    if(qr_version > 26): print("Sorry, yor message is too long. This generator only supports QR codes up to Size 26")

    # Encode and Structure Data
    bit_string = mode_code + char_count_code + "".join(encoded_message)
    padding = addPadding(bit_string, qr_version, error_correction_level)
    bit_string+=padding
    bit_string = structureMessage(bit_string, qr_version, error_correction_level)

    # Create matrix to store QR code
    qr_size = (((qr_version-1)*4)+21)
    qr_matrix = [[None] * qr_size for _ in range(qr_size)]

    # Add Patterns
    add_finder_patterns(qr_matrix, qr_size)
    add_alignment_patterns(qr_matrix, qr_version)
    add_timing_patterns(qr_matrix)
    add_dark_module(qr_matrix)
    reserve_format_info(qr_matrix)
    if(qr_version >= 7): reserve_version_info(qr_matrix)

    # Protect Patterns
    protect_reserved_areas(qr_matrix)

    # Add data
    place_data_bits(qr_matrix, bit_string)

    # Find best mask
    mask = find_best_mask(qr_matrix)
    apply_mask(qr_matrix, mask)

    # Unprotect Patterns
    unprotect_reserved_areas(qr_matrix)

    # Add Format Data
    format_string = format_information_bits[error_correction_level][mask]
    place_format_bits(qr_matrix, format_string)

    # Add Version Data
    if(qr_version >= 7): 
        version_string = version_information_bits[qr_version]
        place_version_bits(qr_matrix, version_string)

    # Draw final QR Code
    print("Final Data", qr_matrix)
    draw_matrix(qr_matrix)


if __name__=="__main__":
    main()

