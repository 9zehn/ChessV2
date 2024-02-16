from typing import List, Any
import pygame
import math
from helper import *

# Some global vars
move_track = []
tiles = []
size = 0
dimension = 800
pieces = []
white_color = (237, 237, 228)
brown_color = (87, 47, 3)
green_color = (107, 201, 107)
red_color = (170, 33, 9)
check = False
# Need a King reference
king_w = None
king_b = None
checkmate = False


# Class for piece display and dynamic movement
class Tile:
    def __init__(self, pos_x, pos_y, piece, screen, color, init_color, transp):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.piece = piece
        self.screen = screen
        self.color = color
        self.init_color = init_color
        self.transp = transp
        self.rect = pygame.Rect((pos_x, pos_y), (dimension / 8, dimension / 8))
        self.select = False

    def display_piece(self):
        pygame.draw.rect(self.screen, self.color, (self.pos_x, self.pos_y, dimension / 8, dimension / 8))
        if self.select:
            self.transp.fill(0)
            pygame.draw.rect(self.transp, (154,205,50,85), (self.pos_x, self.pos_y, dimension / 8, dimension / 8))
            self.screen.blit(self.transp,(0,0))
        if self.piece:
            self.screen.blit(self.piece.image, (self.pos_x + 2, self.pos_y + 3))

    def display_motion(self, x, y):
        pygame.draw.rect(self.screen, self.color, (self.pos_x, self.pos_y, dimension / 8, dimension / 8))
        if self.piece:
            self.screen.blit(self.piece.image, (x, y))


class Piece:
    def __init__(self, bw, type, pos_x, pos_y, image, has_moved=0, tile=None):
        self.bw = bw
        self.type = type
        self.pos_x = pos_x
        self.pos_y = pos_y
        img = pygame.image.load(image).convert()
        self.image = pygame.transform.rotozoom(img, 0, 0.75)
        self.has_moved = has_moved
        self.tile = tile


# Generates all the pieces for game start
def create_pieces():
    pieces_list = [Piece("b", "r", 0, 0, "pieces/black-rook.png"),
                   Piece("b", "n", 1, 0, "pieces/black-knight.png"),
                   Piece("b", "b", 2, 0, "pieces/black-bishop.png"),
                   Piece("b", "q", 3, 0, "pieces/black-queen.png"),
                   Piece("b", "k", 4, 0, "pieces/black-king.png"),
                   Piece("b", "b", 5, 0, "pieces/black-bishop.png"),
                   Piece("b", "n", 6, 0, "pieces/black-knight.png"),
                   Piece("b", "r", 7, 0, "pieces/black-rook.png"),
                   Piece("w", "r", 0, 7, "pieces/white-rook.png"),
                   Piece("w", "n", 1, 7, "pieces/white-knight.png"),
                   Piece("w", "b", 2, 7, "pieces/white-bishop.png"),
                   Piece("w", "q", 3, 7, "pieces/white-queen.png"),
                   Piece("w", "k", 4, 7, "pieces/white-king.png"),
                   Piece("w", "b", 5, 7, "pieces/white-bishop.png"),
                   Piece("w", "n", 6, 7, "pieces/white-knight.png"),
                   Piece("w", "r", 7, 7, "pieces/white-rook.png")]

    global king_w
    king_w = pieces_list[12]
    global king_b
    king_b = pieces_list[4]

    pawn_count = 1
    for i in range(8):
        pieces_list.append(Piece("b", "p", pawn_count, 1, "pieces/black-pawn.png"))
        pawn_count += 1

    pawn_count = 1
    for i in range(8):
        pieces_list.append(Piece("w", "p", pawn_count, 6, "pieces/white-pawn.png"))
        pawn_count += 1

    return pieces_list


# Fill board with tiles and pieces
def fill_board(screen, pieces_list):
    i = 0
    for tile in tiles[0]:
        tile.piece = pieces_list[i]
        pieces_list[i].tile = tile
        i += 1

    for tile in tiles[7]:
        tile.piece = pieces_list[i]
        pieces_list[i].tile = tile
        i += 1

    for tile in tiles[1]:
        tile.piece = pieces_list[i]
        pieces_list[i].tile = tile
        i += 1

    for tile in tiles[6]:
        tile.piece = pieces_list[i]
        pieces_list[i].tile = tile
        i += 1


def update_tiles():
    for row in tiles:
        for obj in row:
            obj.display_piece()


def create_tiles(screen, length, width,transp):
    x = y = pos = 0
    black = (0, 0, 0)
    brown = (87, 47, 3)

    for i in range(8):
        column = []
        for j in range(8):
            if j == 0:
                x = 0
            if (j % 2 == 0 and i % 2 == 0) or (j % 2 != 0 and i % 2 != 0):
                tile = Tile(x, y, None, screen, white_color, white_color,transp)
            else:
                tile = Tile(x, y, None, screen, brown_color, brown_color,transp)

            column.append(tile)
            x += length

        tiles.append(column)
        y += width


def move(pcs, tile1, tile2,screen,transp,move_sound,capture_sound):
    if tile2.piece is not None:
        pcs.remove(tile2.piece)
        pygame.mixer.Sound.play(capture_sound)
    else:
        pygame.mixer.Sound.play(move_sound)

    tile2.piece = tile1.piece
    tile2.piece.tile = tile2
    tile1.piece = None
    if tile2.piece.type == "p" and (tile2.pos_y == 0 or tile2.pos_y == 700):
        pawn_promotion(screen,tile2,pcs,transp)
    else:
        tile2.piece.pos_x = int(tile2.pos_x / 100)
        tile2.piece.pos_y = int(tile2.pos_y / 100)
    tile2.piece.has_moved = 1


def check_select(screen, pos):
    for row in tiles:
        for obj in row:
            if obj.rect.collidepoint(pos):
                return obj


def check_legal_moves(tile):
    moves = []
    legit_moves = []
    if tile.piece.type == "p":
        moves = check_moves_pawn(tiles, tile).copy()
    elif tile.piece.type == "b":
        moves = check_moves_bishop(tiles, tile).copy()
    elif tile.piece.type == "k":
        moves = check_moves_king(tiles, tile).copy()
        moves = check_castle(tiles, tile, moves).copy()
    elif tile.piece.type == "r":
        moves = check_moves_rook(tiles, tile).copy()
    elif tile.piece.type == "q":
        moves = check_moves_queen(tiles, tile).copy()
    elif tile.piece.type == "n":
        moves = check_moves_knight(tiles, tile).copy()

    if tile.piece.type == "k":
        return moves

    for move in moves:
        if move_is_legal(tile, move):
            legit_moves.append(move)
    return legit_moves


def move_is_legal(tile, move_tile):
    retval = True
    temp_tile = tile.piece
    temp_move = move_tile.piece
    move_tile.piece = tile.piece
    tile.piece = None
    king = king_b if temp_tile.bw == "b" else king_w
    if not check_legal_king(tiles, king.pos_x, king.pos_y, king.bw):
        retval = False
    tile.piece = temp_tile
    move_tile.piece = temp_move
    return retval


def check_for_check(bw):
    if bw == "w":
        if not check_legal_king(tiles, king_w.pos_x, king_w.pos_y, bw):
            return True
    elif bw == "b":
        if not check_legal_king(tiles, king_b.pos_x, king_b.pos_y, bw):
            return True


def display_check(bw):
    if bw == "w":
        tile = tiles[int(king_w.pos_y)][int(king_w.pos_x)]
        tile.color = red_color
    if bw == "b":
        tile = tiles[int(king_b.pos_y)][int(king_b.pos_x)]
        tile.color = red_color
    return tile


def display_legal_moves(screen, list_moves):
    for tile in list_moves:
        pygame.draw.circle(screen, green_color, (tile.pos_x + 50, tile.pos_y + 50), 15)


def check_mate(pcs, bw):
    for piece in pcs:
        if piece.bw == bw:
            if len(check_legal_moves(piece.tile)) > 0:
                return False
    return True


def pawn_promotion(screen, pawn_tile,pcs,transp):
    bw = pawn_tile.piece.bw
    bwtype = "black" if bw == "b" else "white"
    pos = None
    selected_tile = None
    dir = 1
    index = None
    no_decision = True
    display_promotion(screen,transp,pawn_tile)

    if bw == "b":
        dir = -1

    while no_decision:
        pygame.time.delay(30)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                selected_tile = check_select(screen,pos)
                if selected_tile is not None:
                    no_decision = False
                    break
    y1 = pawn_tile.pos_y
    y2 = selected_tile.pos_y

    if (selected_tile == pawn_tile and bw == "w") or (y2 == y1+300*dir and bw == "b"):
        piece = Piece(bw,"q",pawn_tile.pos_x/100,pawn_tile.pos_y/100,"pieces/"+bwtype+"-queen.png")
        print(0)
    elif (y2 == y1 + 100*dir and bw == "w") or (y2 == y1+200*dir and bw == "b"):
        piece = Piece(bw,"r",pawn_tile.pos_x/100,pawn_tile.pos_y/100,"pieces/"+bwtype+"-rook.png")
        print(1)
    elif (y2 == y1 + 300*dir and bw == "w") or (selected_tile == pawn_tile and bw == "b"):
        piece = Piece(bw,"b",pawn_tile.pos_x/100,pawn_tile.pos_y/100,"pieces/"+bwtype+"-bishop.png")
        print(2)
    elif (y2 == y1 + 200*dir and bw == "w") or (y2 == y1+100*dir and bw == "b"):
        piece = Piece(bw,"n",pawn_tile.pos_x/100,pawn_tile.pos_y/100,"pieces/"+bwtype+"-knight.png")
        print(3)

    pcs.append(piece)
    pawn_tile.piece = piece
    piece.tile = pawn_tile


# Main method to run the game
def main(l_dim, w_dim):
    # Initialize some variables
    dimension = l_dim
    move_count = 1
    length = width = l_dim / 8
    move_print_x = 825
    move_print_y = 95
    piece_to_move = None
    selected_tile = None
    check_tile = None
    hashtag = ""

    # For move display
    pygame.font.init()
    font = pygame.font.SysFont("Palatino Linotype", 30)

    # Sound
    pygame.mixer.init()
    move_sound = pygame.mixer.Sound("soundfx/move.mp3")
    capture_sound = pygame.mixer.Sound("soundfx/capture.mp3")
    check_sound = pygame.mixer.Sound("soundfx/move-check.mp3")
    castle_sound = pygame.mixer.Sound("soundfx/castle.mp3")

    # Graphics
    background_color = (43, 43, 43)
    screen = pygame.display.set_mode((l_dim + 300, w_dim))
    pygame.display.set_caption("Chess")
    screen.fill(background_color)
    transp = pygame.Surface((800, 800),pygame.SRCALPHA)
    pygame.draw.rect(screen, (80, 80, 80), (815, 90, 270, 730))
    print_headline(screen)

    pieces = create_pieces().copy()

    create_tiles(screen, length, width,transp)

    fill_board(screen, pieces)

    # Init some more vars
    pygame.display.update()
    selected = False
    turn = "w"
    running = True
    checkmate = False
    dragging = False
    selected_tile = None
    move_tile = None
    drag_pos_x = None
    drag_pos_y = None
    drop = False
    move1_select = None
    move2_select = None
    sel_select = None

    legal_moves: List[Any] = []

    # Main loop
    while running:
        pygame.time.delay(1)
        update_tiles()

        if selected:
            display_legal_moves(screen, legal_moves)
        if move_tile:
            move_tile.display_motion(drag_pos_x, drag_pos_y)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False

            # Case 1: Drop after dragging registered
            if event.type == pygame.MOUSEBUTTONUP:
                drop = True
                dragging = False
                move_tile = None

                pos = pygame.mouse.get_pos()
                temp_tile = check_select(screen, pos)
                if not temp_tile in legal_moves:
                    drop = False
                    continue
                selected_tile = temp_tile

            # Case 2: Piece was dragged & dropped
            if (event.type == pygame.MOUSEBUTTONDOWN and not dragging) or drop:

                # Only needed if selected piece was not dropped
                if not drop:
                    pos = pygame.mouse.get_pos()
                    drag_pos_x = pos[0] - 48
                    drag_pos_y = pos[1] - 52
                    selected_tile = check_select(screen, pos)
                    move_tile = selected_tile

                    if sel_select is not None:
                            sel_select.select = False

                    if selected_tile.piece is not None and selected_tile.piece.bw == turn:
                        sel_select = selected_tile
                        selected_tile.select = True
                drop = False

                # Selected tile was outside of board
                if selected_tile is None:
                    continue

                # Selected piece's color is not allowed to move
                if selected_tile is not None and selected_tile.piece is not None and \
                        selected_tile.piece.bw != turn and not selected:
                    dragging = False
                    move_tile = None
                    continue
                dragging = True

                # Player makes the move
                if selected and (selected_tile in legal_moves):
                    dragging = False
                    move_tile = None
                    output = convert_coordinates(piece_to_move, selected_tile)

                    if move1_select is not None:
                        move1_select.select = False
                    if move2_select is not None:
                        move2_select.select = False
                    move1_select = piece_to_move
                    move2_select = selected_tile
                    piece_to_move.select = True
                    selected_tile.select = True
                    sel_select = None

                    # Makes sure that turns alternate
                    turn = "b" if piece_to_move.piece.bw == "w" else "w"

                    # Check if User wants to castle
                    if piece_to_move.piece.type == "k" and (selected_tile.pos_x - piece_to_move.pos_x == 200 \
                                                            or piece_to_move.pos_x - selected_tile.pos_x == 200):
                        move_castle(tiles, pieces, piece_to_move, selected_tile)
                        pygame.mixer.Sound.play(castle_sound)
                    else:
                        move(pieces, piece_to_move, selected_tile,screen,transp,move_sound,capture_sound)

                    # Display the red square for checks
                    check_bool = check_for_check(turn)
                    if check_tile is None and check_bool:
                        pygame.mixer.Sound.play(check_sound)
                        check_tile = display_check(turn)
                        # Check whether it is mate
                        if check_mate(pieces, turn):
                            checkmate = True
                    elif check_tile is not None and check_bool:
                        check_tile.color = check_tile.init_color
                        check_tile = display_check(turn)
                    elif check_tile is not None:
                        check_tile.color = check_tile.init_color
                        check_tile = None
                    legal_moves = []
                    selected = False

                    # Checks for check or checkmate
                    if check_bool:
                        hashtag = "#" if checkmate else "+"
                        check_bool = False
                    else:
                        hashtag = ""

                    # Prints moves
                    if turn == "b":
                        text = font.render(str(move_count) + ". " + output + hashtag,
                                           True, (200, 200, 200))
                        screen.blit(text, (move_print_x, move_print_y))
                    else:
                        text = font.render(" " + output + hashtag, True,
                                           (200, 200, 200))
                        screen.blit(text, (move_print_x + 93, move_print_y))
                        move_count += 1
                        move_print_y += 23

                elif selected_tile.piece is not None:
                    # Fix some glitch that made multiple turns for one side possible
                    if selected_tile.piece.bw != turn:
                        selected = False
                        continue
                    legal_moves = check_legal_moves(selected_tile)
                    piece_to_move = selected_tile
                    selected = True
                else:
                    selected = False

            # Case 4:
            elif event.type == pygame.MOUSEMOTION and dragging and move_tile is not None \
                    and move_tile.piece is not None:
                pos = pygame.mouse.get_pos()
                drag_pos_x = pos[0] - 45
                drag_pos_y = pos[1] - 45

                if move_tile.piece.type == "p" and drag_pos_x > 725:
                    drag_pos_x = 725
                elif move_tile.piece.type == "q" and drag_pos_x > 710:
                    drag_pos_x = 710
                elif drag_pos_x > 713:
                    drag_pos_x = 713

                move_tile = selected_tile


if __name__ == "__main__":
    main(800, 800)
