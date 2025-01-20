import reedsolo

def errorCorrection(message_coefficients, generator_poly_size):

    # 100011101 
    reedsolo.init_tables(0x11d)
    rs = reedsolo.RSCodec(generator_poly_size)
    encoded = rs.encode(bytearray(message_coefficients))

    # separate error correction portion
    error_correction = list(encoded[-generator_poly_size:])

    return error_correction


""" Replaced by format_information_bits table in lookup_tables """

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