import pygame

# Make global so queen can use these too
bishop_moves = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
rook_moves = [(1, 0), (0, 1), (0, -1), (-1, 0)]
knight_moves = [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)]
king_moves = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]


def is_on_board(pos_x, pos_y):
    if (0 <= pos_x <= 7) and (0 <= pos_y <= 7):
        return True
    else:
        return False


def check_help(array, moves, tile, pos_x, pos_y, x, y):
    if is_on_board(pos_x + x, pos_y + y):
        if array[pos_y + y][pos_x + x].piece is None:
            moves.append(array[pos_y + y][pos_x + x])
            check_help(array, moves, tile, pos_x + x, pos_y + y, x, y)
        else:
            if array[pos_y + y][pos_x + x].piece.bw != tile.piece.bw:
                moves.append(array[pos_y + y][pos_x + x])


def check_moves_knight(array, tile):
    knight = tile.piece
    pos_x = int(tile.pos_x / 100)
    pos_y = int(tile.pos_y / 100)
    moves = []

    for (x, y) in knight_moves:
        if is_on_board(pos_x + x, pos_y + y):
            if array[pos_y + y][pos_x + x].piece is None:
                moves.append(array[pos_y + y][pos_x + x])
            else:
                if knight.bw != array[pos_y + y][pos_x + x].piece.bw:
                    moves.append(array[pos_y + y][pos_x + x])

    return moves


def check_moves_bishop(array, tile):
    bishop = tile.piece
    pos_x = int(tile.pos_x / 100)
    pos_y = int(tile.pos_y / 100)
    moves = []

    for (x, y) in bishop_moves:
        check_help(array, moves, tile, pos_x, pos_y, x, y)

    return moves


def check_moves_rook(array, tile):
    pos_x = int(tile.pos_x / 100)
    pos_y = int(tile.pos_y / 100)
    moves = []

    for (x, y) in rook_moves:
        check_help(array, moves, tile, pos_x, pos_y, x, y)

    return moves


def check_moves_queen(array, tile):
    pos_x = int(tile.pos_x / 100)
    pos_y = int(tile.pos_y / 100)
    moves = []

    for (x, y) in rook_moves:
        check_help(array, moves, tile, pos_x, pos_y, x, y)
    for (x, y) in bishop_moves:
        check_help(array, moves, tile, pos_x, pos_y, x, y)

    return moves


def check_moves_pawn(array, tile):
    pawn = tile.piece
    color = pawn.bw
    pos_x = int(tile.pos_x / 100)
    pos_y = int(tile.pos_y / 100)
    moves = []
    direction = 1
    if color == "w":
        direction = -1
    if array[pos_y + direction][pos_x].piece is None:
        moves.append(array[pos_y + direction][pos_x])
    if pawn.has_moved == 0 and array[pos_y + 2 * direction][pos_x].piece is None and \
            array[pos_y + 1 * direction][pos_x].piece is None:
        moves.append(array[pos_y + 2 * direction][pos_x])
    # Check if pawn can take
    if is_on_board(pos_x + 1, pos_y + direction):
        if array[pos_y + direction][pos_x + 1].piece is not None and \
                array[pos_y + direction][pos_x + 1].piece.bw != color:
            moves.append(array[pos_y + direction][pos_x + 1])
    if is_on_board(pos_x - 1, pos_y + direction):
        if array[pos_y + direction][pos_x - 1].piece is not None and \
                array[pos_y + direction][pos_x - 1].piece.bw != color:
            moves.append(array[pos_y + direction][pos_x - 1])

    return moves


def check_moves_king(array, tile):
    king = tile.piece
    pos_x = int(tile.pos_x / 100)
    pos_y = int(tile.pos_y / 100)

    moves = []
    for (x, y) in king_moves:
        if is_on_board(pos_x + x, pos_y + y):
            tile = array[pos_y + y][pos_x + x]
            if tile.piece is None or king.bw != tile.piece.bw:
                if check_legal_king(array, pos_x + x, pos_y + y, king.bw):
                    moves.append(tile)

    return moves


def check_castle(array, tile, moves):
    king = tile.piece
    if king.has_moved == 1:
        return moves
    rook_q = array[king.pos_y][king.pos_x - 4]
    rook_k = array[king.pos_y][king.pos_x + 3]

    if rook_q.piece is None or rook_q.piece.has_moved == 1:
        rook_q = None
    elif array[king.pos_y][king.pos_x - 2].piece is None and array[king.pos_y][king.pos_x - 1].piece is None and \
            array[king.pos_y][king.pos_x - 3].piece is None:
        if check_legal_king(array, king.pos_x - 2, king.pos_y, king.bw) and \
                check_legal_king(array, king.pos_x - 1, king.pos_y, king.bw) and \
                check_legal_king(array, king.pos_x, king.pos_y, king.bw):
            moves.append(array[king.pos_y][king.pos_x - 2])

    if rook_k.piece is None or rook_k.piece.has_moved == 1:
        rook_k = None
    elif array[king.pos_y][king.pos_x + 1].piece is None and array[king.pos_y][king.pos_x + 2].piece is None:
        if check_legal_king(array, king.pos_x + 2, king.pos_y, king.bw) and \
                check_legal_king(array, king.pos_x + 1, king.pos_y, king.bw) and \
                check_legal_king(array, king.pos_x, king.pos_y, king.bw):
            moves.append(array[king.pos_y][king.pos_x + 2])

    return moves


def move_castle(array, pieces, king, king_move):
    x = king.piece.pos_x
    y = king.piece.pos_y
    i = -1
    r = 4

    if king_move.pos_x > king.pos_x:
        i = 1
        r = 3
    king.piece.pos_x += i * 2
    king.piece.has_moved = 1
    king_move.piece = king.piece
    king_move.piece.tile = king_move
    king.piece = None
    array[y][x + i].piece = array[y][x + i * r].piece
    array[y][x + i].piece.pos_x = int(array[y][x + i].pos_x)
    array[y][x + i].piece.tile = array[y][x + i]
    array[y][x + i * r].piece = None


def check_legal_king(array, pos_x, pos_y, bw):
    for (x, y) in bishop_moves:
        if not check_help_king(array, bw, pos_x, pos_y, x, y, "b", "q"):
            return False

    for (x, y) in rook_moves:
        if not check_help_king(array, bw, pos_x, pos_y, x, y, "r", "q"):
            return False
    for (x, y) in knight_moves:
        if is_on_board(pos_x + x, pos_y + y):
            piece = array[pos_y + y][pos_x + x].piece
            if piece is None:
                continue
            elif bw != piece.bw and piece.type == "n":
                return False

    # Check Pawns
    direction = -1 if bw == "w" else 1
    if is_on_board(pos_x + 1, pos_y + direction) and \
            array[pos_y + direction][pos_x + 1].piece is not None:
        piece = array[pos_y + direction][pos_x + 1].piece
        if piece.bw != bw and piece.type == "p":
            return False

    # Check other pawn
    if is_on_board(pos_x - 1, pos_y + direction) and \
            array[pos_y + direction][pos_x - 1].piece is not None:
        piece = array[pos_y + direction][pos_x - 1].piece
        if piece.bw != bw and piece.type == "p":
            return False

    # Check other King
    for (x, y) in king_moves:
        if is_on_board(pos_x + x, pos_y + y) and \
                array[pos_y + y][pos_x + x].piece is not None:
            kng = array[pos_y + y][pos_x + x].piece
            if kng.type == "k" and kng.bw != bw:
                return False

    return True


def check_help_king(array, bw, pos_x, pos_y, x, y, p_type, opt="0"):
    if is_on_board(pos_x + x, pos_y + y):
        piece = array[pos_y + y][pos_x + x].piece
        if piece is None:
            return check_help_king(array, bw, pos_x + x, pos_y + y, x, y, p_type, opt)
        elif piece.type == "k":
            return check_help_king(array, bw, pos_x + x, pos_y + y, x, y, p_type, opt)
        elif piece.bw != bw and (piece.type == p_type or piece.type == opt):
            return False
        else:
            return True
    return True


def convert_coordinates(tile1, tile2):
    l = ["a", "b", "c", "d", "e", "f", "g", "h"]
    lit_x1 = l[int(tile1.pos_x / 100)]
    num_y1 = -int(tile1.pos_y / 100) + 8
    lit_x2 = l[int(tile2.pos_x / 100)]
    num_y2 = -int(tile2.pos_y / 100) + 8
    output = ""

    if tile1.piece.type != "p":
        output = tile1.piece.type.upper()
    if tile2.piece is not None:
        if tile1.piece.type == "p":
            output += lit_x1
        output += "x"
    output += lit_x2 + str(num_y2)

    return output


def print_headline(screen):
    pygame.font.init()
    font = pygame.font.SysFont("Palatino Linotype", 55)
    text = font.render("Moves", True, (200, 200, 200))
    screen.blit(text, (890, 40))

    font = pygame.font.SysFont("Sans", 12)
    text = font.render("Copyright  |  SeaLion Dev © 2023", True, (200, 200, 200))
    screen.blit(text, (860, 772))


def display_promotion(screen, transp, tile):
    image_list = ["pieces/black-queen.png", "pieces/black-rook.png", "pieces/black-knight.png",
                  "pieces/black-bishop.png", "pieces/white-queen.png", "pieces/white-rook.png",
                  "pieces/white-knight.png", "pieces/white-bishop.png"]
    # Transparent screen
    pygame.draw.rect(transp, (255, 255, 255, 80), (0, 0, 800, 800))
    screen.blit(transp, (0, 0))
    index = 4

    pos_y = tile.pos_y

    if tile.piece.bw == "b":
        pos_y = tile.pos_y - 300
        index = 0

    # Background for select
    pygame.draw.rect(screen, (255, 255, 255), (tile.pos_x, pos_y, 100, 400))
    for i in range(4):
        img = pygame.image.load(image_list[index]).convert()
        image = pygame.transform.rotozoom(img, 0, 0.75)
        screen.blit(image, (tile.pos_x, pos_y))
        pos_y += 100
        index += 1

    pygame.display.update()


def position_to_string(tiles):
    moves = ""
    index = 0
    for row in tiles:
        for tile in row:
            if tile.piece is None:
                index +=1
            else:
                if index != 0:
                    moves += str(index)
                index = 0
                type = tile.piece.type if tile.piece.bw == "b" else tile.piece.type.upper()
                moves += type
        moves += "/"
        index = 0
    return moves
