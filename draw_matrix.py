from PIL import Image, ImageDraw

#########################################################################
#               Protect Patterns that should not be Masked              #
#########################################################################
def protect_reserved_areas(qr_matrix):
    size = len(qr_matrix)
    for r in range(size):
        for c in range(size):
            if(qr_matrix[r][c] == 0): qr_matrix[r][c] = 4
            if(qr_matrix[r][c] == 1): qr_matrix[r][c] = 5

def unprotect_reserved_areas(qr_matrix):
    size = len(qr_matrix)
    for r in range(size):
        for c in range(size):
            if qr_matrix[r][c] == 4: qr_matrix[r][c] = 0
            if qr_matrix[r][c] == 5: qr_matrix[r][c] = 1

#########################################################################
#                       Turn Matrix into PNG Image                      #
#########################################################################
def draw_matrix(matrix, scale=10, show_outline = False, output='qr_code.png'):
    """Render the QR matrix to an image."""
    size = len(matrix)
    img = Image.new('RGB', (size * scale, size * scale), 'white')
    draw = ImageDraw.Draw(img)
    
    outline_color = 'black' if show_outline else None

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