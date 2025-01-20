from lookup_tables.lookup_table import *

#####################################################################
#                   QR Finder Patterns + Separators                 #
#####################################################################
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


#######################################################################
#                        QR Alignment Patterns                        #
#######################################################################
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


########################################################################
#                        QR Additional Patterns                        #
########################################################################
def add_dark_module(matrix):
    matrix[-8][8] = 1

def add_timing_patterns(matrix):
    for i in range (7, len(matrix)-7):
        matrix[6][i] = i%2==0
        matrix[i][6] = i%2==0

#########################################################################
#                     Reserve Format and Version Info                   #
#########################################################################
def reserve_format_info(matrix):
    for i in range(0,9):
        if i != 6:
            matrix[8][i] = 2
            matrix[i][8] = 2
    for i in range(len(matrix)-8,len(matrix)):
        matrix[8][i] = 2
    for i in range(len(matrix)-7,len(matrix)):
        matrix[i][8] = 2

def reserve_version_info(matrix):
    for i in range(len(matrix) -11, len(matrix) -8 ):
        for j in range(0,6):
            matrix[i][j] = 3
            matrix[j][i] = 3
