from lookup_tables.lookup_table import *

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

def encode_byte(message):
    return list(map(lambda char: format(ord(char), '08b'), message))