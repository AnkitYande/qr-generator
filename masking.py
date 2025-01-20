import math
from copy import deepcopy
import os
import shutil

from draw_matrix import *

def create_dir(dir_name):
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)
    os.makedirs(dir_name)


def find_best_mask(old_matrix):
    create_dir("masking")
    bestIdx = -1
    bestScore = math.inf
    for i in range(0,8):
        temp_matrix = deepcopy(old_matrix)
        apply_mask(temp_matrix, i)
        unprotect_reserved_areas(temp_matrix)
        draw_matrix(temp_matrix, show_outline=True, output='masking/qr_code_'+str(i)+'.png')
        score = eval_mask(temp_matrix)
        if(score < bestScore):
            bestScore = score
            bestIdx = i
    
    print("bestIdx", bestIdx)
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