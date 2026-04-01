"""
Шахматный симулятор - ООП версия
Дополнительные задания: 1,5,6,7,8 (сумма 5 баллов)
доп шахматы - архиепископ, амазон, канцлер
"""

from abc import ABC, abstractmethod
from enum import Enum


class Color(Enum):
    WHITE = "white"
    BLACK = "black"
    
    def opposite(self):
        return Color.BLACK if self == Color.WHITE else Color.WHITE


class MoveType(Enum):
    NORMAL = "normal"
    CAPTURE = "capture"
    CASTLE_KINGSIDE = "castle_kingside"
    CASTLE_QUEENSIDE = "castle_queenside"
    EN_PASSANT = "en_passant"
    PROMOTION = "promotion"


class Move:
    def __init__(self, piece, start_pos, end_pos, move_type=MoveType.NORMAL, captured_piece=None, promotion_piece=None, en_passant_target=None):
        self.piece = piece
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.move_type = move_type
        self.captured_piece = captured_piece
        self.promotion_piece = promotion_piece
        self.was_first_move = not piece.has_moved
        self.old_en_passant = en_passant_target
        self.rook = None
        self.rook_start = None
        self.rook_end = None
    
    def __str__(self):
        cols = 'abcdefgh'
        start = f"{cols[self.start_pos[1]]}{8-self.start_pos[0]}"
        end = f"{cols[self.end_pos[1]]}{8-self.end_pos[0]}"
        piece_name = self.piece.symbol
        move_str = f"{piece_name} {start}->{end}"
        if self.move_type == MoveType.CAPTURE or self.captured_piece:
            move_str += " x"
        if self.move_type == MoveType.PROMOTION:
            move_str += f" ={self.promotion_piece.symbol}"
        return move_str


class Piece(ABC):
    def __init__(self, color, position):
        self._color = color
        self._position = position
        self._has_moved = False
    
    @property
    def color(self):
        return self._color
    
    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, value):
        self._position = value
    
    @property
    def has_moved(self):
        return self._has_moved
    
    @has_moved.setter
    def has_moved(self, value):
        self._has_moved = value
    
    @property
    @abstractmethod
    def symbol(self):
        pass
    
    @property
    @abstractmethod
    def name(self):
        pass
    
    @property
    def value(self):
        return 0
    
    @abstractmethod
    def get_possible_moves(self, board):
        pass
    
    @staticmethod
    def is_valid_position(row, col):
        return 0 <= row < 8 and 0 <= col < 8
    
    def _get_linear_moves(self, board, directions):
        moves = []
        row, col = self._position
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + dr * i, col + dc * i
                if not self.is_valid_position(new_row, new_col):
                    break
                piece = board.get_piece(new_row, new_col)
                if piece is None:
                    moves.append((new_row, new_col))
                elif piece.color != self._color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        return moves


class King(Piece):
    @property
    def symbol(self):
        return 'K' if self._color == Color.WHITE else 'k'
    
    @property
    def name(self):
        return "Король"
    
    @property
    def value(self):
        return 10000
    
    def get_possible_moves(self, board):
        moves = []
        row, col = self._position
        
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), 
                     (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if self.is_valid_position(new_row, new_col):
                piece = board.get_piece(new_row, new_col)
                if piece is None or piece.color != self._color:
                    moves.append((new_row, new_col))
        
        if not self._has_moved and not board.is_square_attacked(row, col, self._color):
            if self._can_castle_kingside(board):
                moves.append((row, col + 2))
            if self._can_castle_queenside(board):
                moves.append((row, col - 2))
        
        return moves
    
    def _can_castle_kingside(self, board):
        row, col = self._position
        rook = board.get_piece(row, 7)
        if not isinstance(rook, Rook) or rook.has_moved or rook.color != self._color:
            return False
        if board.get_piece(row, 5) or board.get_piece(row, 6):
            return False
        if board.is_square_attacked(row, 5, self._color):
            return False
        if board.is_square_attacked(row, 6, self._color):
            return False
        return True
    
    def _can_castle_queenside(self, board):
        row, col = self._position
        rook = board.get_piece(row, 0)
        if not isinstance(rook, Rook) or rook.has_moved or rook.color != self._color:
            return False
        for c in range(1, col):
            if board.get_piece(row, c):
                return False
        if board.is_square_attacked(row, 3, self._color):
            return False
        if board.is_square_attacked(row, 2, self._color):
            return False
        return True


class Queen(Piece):
    @property
    def symbol(self):
        return 'Q' if self._color == Color.WHITE else 'q'
    
    @property
    def name(self):
        return "Ферзь"
    
    @property
    def value(self):
        return 9
    
    def get_possible_moves(self, board):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                     (-1, -1), (-1, 1), (1, -1), (1, 1)]
        return self._get_linear_moves(board, directions)


class Rook(Piece):
    @property
    def symbol(self):
        return 'R' if self._color == Color.WHITE else 'r'
    
    @property
    def name(self):
        return "Ладья"
    
    @property
    def value(self):
        return 5
    
    def get_possible_moves(self, board):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        return self._get_linear_moves(board, directions)


class Bishop(Piece):
    @property
    def symbol(self):
        return 'B' if self._color == Color.WHITE else 'b'
    
    @property
    def name(self):
        return "Слон"
    
    @property
    def value(self):
        return 3
    
    def get_possible_moves(self, board):
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        return self._get_linear_moves(board, directions)


class Knight(Piece):
    @property
    def symbol(self):
        return 'N' if self._color == Color.WHITE else 'n'
    
    @property
    def name(self):
        return "Конь"
    
    @property
    def value(self):
        return 3
    
    def get_possible_moves(self, board):
        moves = []
        row, col = self._position
        
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1)]
        
        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc
            if self.is_valid_position(new_row, new_col):
                piece = board.get_piece(new_row, new_col)
                if piece is None or piece.color != self._color:
                    moves.append((new_row, new_col))
        
        return moves


class Pawn(Piece):
    @property
    def symbol(self):
        return 'P' if self._color == Color.WHITE else 'p'
    
    @property
    def name(self):
        return "Пешка"
    
    @property
    def value(self):
        return 1
    
    def get_possible_moves(self, board):
        moves = []
        row, col = self._position
        
        direction = -1 if self._color == Color.WHITE else 1
        start_row = 6 if self._color == Color.WHITE else 1
        
        new_row = row + direction
        if self.is_valid_position(new_row, col):
            if board.get_piece(new_row, col) is None:
                moves.append((new_row, col))
                
                if row == start_row:
                    new_row2 = row + 2 * direction
                    if board.get_piece(new_row2, col) is None:
                        moves.append((new_row2, col))
        
        for dc in [-1, 1]:
            new_col = col + dc
            if self.is_valid_position(new_row, new_col):
                piece = board.get_piece(new_row, new_col)
                if piece and piece.color != self._color:
                    moves.append((new_row, new_col))
        
        en_passant = board.en_passant_target
        if en_passant:
            ep_row, ep_col = en_passant
            if new_row == ep_row and abs(col - ep_col) == 1:
                moves.append(en_passant)
        
        return moves
    
    def is_promotion_move(self, end_row):
        promotion_row = 0 if self._color == Color.WHITE else 7
        return end_row == promotion_row


class Amazon(Piece):
    @property
    def symbol(self):
        return 'A' if self._color == Color.WHITE else 'a'
    
    @property
    def name(self):
        return "Амазонка"
    
    @property
    def value(self):
        return 12
    
    def get_possible_moves(self, board):
        moves = set()
        row, col = self._position
        
        queen_directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                           (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for move in self._get_linear_moves(board, queen_directions):
            moves.add(move)
        
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc
            if self.is_valid_position(new_row, new_col):
                piece = board.get_piece(new_row, new_col)
                if piece is None or piece.color != self._color:
                    moves.add((new_row, new_col))
        
        return list(moves)


class Archbishop(Piece):
    @property
    def symbol(self):
        return 'M' if self._color == Color.WHITE else 'm'
    
    @property
    def name(self):
        return "Архиепископ"
    
    @property
    def value(self):
        return 7
    
    def get_possible_moves(self, board):
        moves = set()
        row, col = self._position
        
        bishop_directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for move in self._get_linear_moves(board, bishop_directions):
            moves.add(move)
        
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc
            if self.is_valid_position(new_row, new_col):
                piece = board.get_piece(new_row, new_col)
                if piece is None or piece.color != self._color:
                    moves.add((new_row, new_col))
        
        return list(moves)


class Chancellor(Piece):
    @property
    def symbol(self):
        return 'C' if self._color == Color.WHITE else 'c'
    
    @property
    def name(self):
        return "Канцлер"
    
    @property
    def value(self):
        return 8
    
    def get_possible_moves(self, board):
        moves = set()
        row, col = self._position
        
        rook_directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for move in self._get_linear_moves(board, rook_directions):
            moves.add(move)
        
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc
            if self.is_valid_position(new_row, new_col):
                piece = board.get_piece(new_row, new_col)
                if piece is None or piece.color != self._color:
                    moves.add((new_row, new_col))
        
        return list(moves)


class Board:
    def __init__(self):
        self._board = [[None] * 8 for _ in range(8)]
        self._en_passant_target = None
        self._move_history = []
        self._captured_pieces = {Color.WHITE: [], Color.BLACK: []}
    
    @property
    def en_passant_target(self):
        return self._en_passant_target
    
    @property
    def move_history(self):
        return self._move_history
    
    def setup_standard(self):
        self._board[0] = [
            Rook(Color.BLACK, (0, 0)),
            Knight(Color.BLACK, (0, 1)),
            Bishop(Color.BLACK, (0, 2)),
            Queen(Color.BLACK, (0, 3)),
            King(Color.BLACK, (0, 4)),
            Bishop(Color.BLACK, (0, 5)),
            Knight(Color.BLACK, (0, 6)),
            Rook(Color.BLACK, (0, 7))
        ]
        for col in range(8):
            self._board[1][col] = Pawn(Color.BLACK, (1, col))
        
        self._board[7] = [
            Rook(Color.WHITE, (7, 0)),
            Knight(Color.WHITE, (7, 1)),
            Bishop(Color.WHITE, (7, 2)),
            Queen(Color.WHITE, (7, 3)),
            King(Color.WHITE, (7, 4)),
            Bishop(Color.WHITE, (7, 5)),
            Knight(Color.WHITE, (7, 6)),
            Rook(Color.WHITE, (7, 7))
        ]
        for col in range(8):
            self._board[6][col] = Pawn(Color.WHITE, (6, col))
    
    def get_piece(self, row, col):
        if 0 <= row < 8 and 0 <= col < 8:
            return self._board[row][col]
        return None
    
    def set_piece(self, row, col, piece):
        if 0 <= row < 8 and 0 <= col < 8:
            self._board[row][col] = piece
            if piece:
                piece.position = (row, col)
    
    def find_king(self, color):
        for row in range(8):
            for col in range(8):
                piece = self._board[row][col]
                if isinstance(piece, King) and piece.color == color:
                    return (row, col)
        return None
    
    def is_square_attacked(self, row, col, by_color):
        enemy_color = by_color.opposite()
        
        for r in range(8):
            for c in range(8):
                piece = self._board[r][c]
                if piece and piece.color == enemy_color:
                    if isinstance(piece, Pawn):
                        direction = -1 if piece.color == Color.WHITE else 1
                        if r + direction == row and abs(c - col) == 1:
                            return True
                    elif isinstance(piece, King):
                        if abs(r - row) <= 1 and abs(c - col) <= 1:
                            if (r, c) != (row, col):
                                return True
                    else:
                        moves = piece.get_possible_moves(self)
                        if (row, col) in moves:
                            return True
        return False
    
    def is_in_check(self, color):
        king_pos = self.find_king(color)
        if king_pos is None:
            return False
        return self.is_square_attacked(king_pos[0], king_pos[1], color)
    
    def get_legal_moves(self, piece):
        legal_moves = []
        possible_moves = piece.get_possible_moves(self)
        
        for end_pos in possible_moves:
            if self._is_move_legal(piece, end_pos):
                legal_moves.append(end_pos)
        
        return legal_moves
    
    def _is_move_legal(self, piece, end_pos):
        start_pos = piece.position
        captured = self.get_piece(end_pos[0], end_pos[1])
        
        self._board[start_pos[0]][start_pos[1]] = None
        self._board[end_pos[0]][end_pos[1]] = piece
        old_pos = piece.position
        piece._position = end_pos
        
        en_passant_captured = None
        if isinstance(piece, Pawn) and end_pos == self._en_passant_target:
            direction = -1 if piece.color == Color.WHITE else 1
            en_passant_captured = self.get_piece(end_pos[0] - direction, end_pos[1])
            if en_passant_captured:
                self._board[end_pos[0] - direction][end_pos[1]] = None
        
        is_legal = not self.is_in_check(piece.color)
        
        self._board[start_pos[0]][start_pos[1]] = piece
        self._board[end_pos[0]][end_pos[1]] = captured
        piece._position = old_pos
        
        if en_passant_captured:
            direction = -1 if piece.color == Color.WHITE else 1
            self._board[end_pos[0] - direction][end_pos[1]] = en_passant_captured
        
        return is_legal
    
    def make_move(self, start_pos, end_pos, promotion_choice='Q'):
        piece = self.get_piece(start_pos[0], start_pos[1])
        if piece is None:
            return None
        
        captured = self.get_piece(end_pos[0], end_pos[1])
        move_type = MoveType.CAPTURE if captured else MoveType.NORMAL
        
        move = Move(piece, start_pos, end_pos, move_type, captured,
                   en_passant_target=self._en_passant_target)
        
        if isinstance(piece, King) and abs(end_pos[1] - start_pos[1]) == 2:
            if end_pos[1] > start_pos[1]:
                move.move_type = MoveType.CASTLE_KINGSIDE
                move.rook = self.get_piece(start_pos[0], 7)
                move.rook_start = (start_pos[0], 7)
                move.rook_end = (start_pos[0], 5)
            else:
                move.move_type = MoveType.CASTLE_QUEENSIDE
                move.rook = self.get_piece(start_pos[0], 0)
                move.rook_start = (start_pos[0], 0)
                move.rook_end = (start_pos[0], 3)
        
        if isinstance(piece, Pawn) and end_pos == self._en_passant_target:
            move.move_type = MoveType.EN_PASSANT
            direction = -1 if piece.color == Color.WHITE else 1
            move.captured_piece = self.get_piece(end_pos[0] - direction, end_pos[1])
        
        if isinstance(piece, Pawn) and piece.is_promotion_move(end_pos[0]):
            move.move_type = MoveType.PROMOTION
            move.promotion_piece = self._create_promotion_piece(
                piece.color, end_pos, promotion_choice)
        
        self._execute_move(move)
        
        self._en_passant_target = None
        if isinstance(piece, Pawn) and abs(end_pos[0] - start_pos[0]) == 2:
            direction = -1 if piece.color == Color.WHITE else 1
            self._en_passant_target = (start_pos[0] + direction, start_pos[1])
        
        self._move_history.append(move)
        
        return move
    
    def _execute_move(self, move):
        self._board[move.start_pos[0]][move.start_pos[1]] = None
        
        if move.promotion_piece:
            self._board[move.end_pos[0]][move.end_pos[1]] = move.promotion_piece
            move.promotion_piece._position = move.end_pos
        else:
            self._board[move.end_pos[0]][move.end_pos[1]] = move.piece
            move.piece._position = move.end_pos
        
        move.piece._has_moved = True
        
        if move.rook:
            self._board[move.rook_start[0]][move.rook_start[1]] = None
            self._board[move.rook_end[0]][move.rook_end[1]] = move.rook
            move.rook._position = move.rook_end
            move.rook._has_moved = True
        
        if move.move_type == MoveType.EN_PASSANT:
            direction = -1 if move.piece.color == Color.WHITE else 1
            self._board[move.end_pos[0] - direction][move.end_pos[1]] = None
        
        if move.captured_piece:
            self._captured_pieces[move.piece.color].append(move.captured_piece)
    
    def undo_move(self):
        if not self._move_history:
            return None
        
        move = self._move_history.pop()
        
        self._board[move.start_pos[0]][move.start_pos[1]] = move.piece
        move.piece._position = move.start_pos
        move.piece._has_moved = not move.was_first_move
        
        self._board[move.end_pos[0]][move.end_pos[1]] = None
        
        if move.captured_piece:
            if move.move_type == MoveType.EN_PASSANT:
                direction = -1 if move.piece.color == Color.WHITE else 1
                cap_row = move.end_pos[0] - direction
                self._board[cap_row][move.end_pos[1]] = move.captured_piece
            else:
                self._board[move.end_pos[0]][move.end_pos[1]] = move.captured_piece
            
            if move.captured_piece in self._captured_pieces[move.piece.color]:
                self._captured_pieces[move.piece.color].remove(move.captured_piece)
        
        if move.rook:
            self._board[move.rook_end[0]][move.rook_end[1]] = None
            self._board[move.rook_start[0]][move.rook_start[1]] = move.rook
            move.rook._position = move.rook_start
            move.rook._has_moved = False
        
        self._en_passant_target = move.old_en_passant
        
        return move
    
    def _create_promotion_piece(self, color, position, choice):
        choice = choice.upper()
        pieces = {
            'Q': Queen,
            'R': Rook,
            'B': Bishop,
            'N': Knight,
            'A': Amazon,
            'C': Chancellor,
            'M': Archbishop
        }
        piece_class = pieces.get(choice, Queen)
        return piece_class(color, position)
    
    def get_threatened_pieces(self, color):
        threatened = []
        for row in range(8):
            for col in range(8):
                piece = self._board[row][col]
                if piece and piece.color == color:
                    if self.is_square_attacked(row, col, color):
                        threatened.append((row, col))
        return threatened
    
    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False
        return self._has_no_legal_moves(color)
    
    def is_stalemate(self, color):
        if self.is_in_check(color):
            return False
        return self._has_no_legal_moves(color)
    
    def _has_no_legal_moves(self, color):
        for row in range(8):
            for col in range(8):
                piece = self._board[row][col]
                if piece and piece.color == color:
                    if self.get_legal_moves(piece):
                        return False
        return True


class ChessGame:
    def __init__(self):
        self._board = Board()
        self._current_turn = Color.WHITE
        self._game_over = False
        self._winner = None
        self._selected_pos = None
        self._legal_moves = []
    
    def new_game(self):
        self._board = Board()
        self._board.setup_standard()
        self._current_turn = Color.WHITE
        self._game_over = False
        self._winner = None
        self._selected_pos = None
        self._legal_moves = []
    
    def display_board(self, show_hints=True):
        threatened = set(self._board.get_threatened_pieces(self._current_turn))
        in_check = self._board.is_in_check(self._current_turn)
        king_pos = self._board.find_king(self._current_turn)
        
        print()
        print("    a   b   c   d   e   f   g   h")
        print("  +---+---+---+---+---+---+---+---+")
        
        for row in range(8):
            print(f"{8-row} |", end="")
            for col in range(8):
                piece = self._board.get_piece(row, col)
                cell = f" {piece.symbol} " if piece else "   "
                
                if show_hints:
                    pos = (row, col)
                    
                    if pos == self._selected_pos:
                        cell = f" {cell[1]} "  # Выбранная фигура
                    elif pos in self._legal_moves:
                        if piece:
                            cell = f" {cell[1]} "  # Взятие
                        else:
                            cell = f" {cell[1]} "  # Возможный ход
                    elif in_check and pos == king_pos:
                        cell = f" {cell[1]} "  # Король под шахом
                    elif pos in threatened:
                        cell = f" {cell[1]} "  # Фигура под боем
                
                print(f"{cell}|", end="")
            
            print(f" {8-row}")
            if row < 7:
                print("  +---+---+---+---+---+---+---+---+")
        
        print("  +---+---+---+---+---+---+---+---+")
        print("    a   b   c   d   e   f   g   h")
        print()
        
        turn_str = "Белые" if self._current_turn == Color.WHITE else "Черные"
        print("Ход: " + turn_str)
        
        if in_check:
            print("Шах!")
        
        if threatened and show_hints:
            print("Под боем: " + str(len(threatened)) + " фигур(а)")
        
        white_captured = self._board._captured_pieces[Color.WHITE]
        black_captured = self._board._captured_pieces[Color.BLACK]
        if white_captured:
            print("Белые взяли: " + ''.join(p.symbol for p in white_captured))
        if black_captured:
            print("Черные взяли: " + ''.join(p.symbol for p in black_captured))
    
    def select_piece(self, pos_str):
        pos = self._parse_position(pos_str)
        if pos is None:
            print("Неверная позиция!")
            return False
        
        piece = self._board.get_piece(pos[0], pos[1])
        if piece is None:
            self._selected_pos = None
            self._legal_moves = []
            return False
        
        if piece.color != self._current_turn:
            print("Это не ваша фигура!")
            return False
        
        self._selected_pos = pos
        self._legal_moves = self._board.get_legal_moves(piece)
        
        if self._legal_moves:
            print("Выбрана: " + piece.name + ", ходов: " + str(len(self._legal_moves)))
        else:
            print("У " + piece.name + " нет ходов!")
        
        return True
    
    def make_move(self, start_str, end_str):
        start_pos = self._parse_position(start_str)
        end_pos = self._parse_position(end_str)
        
        if start_pos is None or end_pos is None:
            print("Неверный формат!")
            return False
        
        piece = self._board.get_piece(start_pos[0], start_pos[1])
        
        if piece is None:
            print("Нет фигуры!")
            return False
        
        if piece.color != self._current_turn:
            print("Не ваша фигура!")
            return False
        
        legal_moves = self._board.get_legal_moves(piece)
        
        if end_pos not in legal_moves:
            print("Недопустимый ход!")
            return False
        
        promotion = 'Q'
        if isinstance(piece, Pawn) and piece.is_promotion_move(end_pos[0]):
            promotion = self._get_promotion_choice()
        
        move = self._board.make_move(start_pos, end_pos, promotion)
        
        if move:
            print("Ход: " + str(move))
            self._selected_pos = None
            self._legal_moves = []
            self._switch_turn()
            self._check_game_over()
            return True
        
        return False
    
    def undo(self):
        move = self._board.undo_move()
        if move:
            self._switch_turn()
            self._selected_pos = None
            self._legal_moves = []
            self._game_over = False
            self._winner = None
            print("Отменено: " + str(move))
            return True
        print("Нечего отменять!")
        return False
    
    def _parse_position(self, pos_str):
        pos_str = pos_str.strip().lower()
        if len(pos_str) != 2:
            return None
        
        col_char, row_char = pos_str[0], pos_str[1]
        
        if col_char < 'a' or col_char > 'h':
            return None
        if row_char < '1' or row_char > '8':
            return None
        
        col = ord(col_char) - ord('a')
        row = 8 - int(row_char)
        
        return (row, col)
    
    def _get_promotion_choice(self):
        print("\nПревращение пешки!")
        print("Q-Ферзь, R-Ладья, B-Слон, N-Конь")
        print("A-Амазонка, C-Канцлер, M-Архиепископ")
        
        while True:
            choice = input("Выбор: ").strip().upper()
            if choice in ['Q', 'R', 'B', 'N', 'A', 'C', 'M']:
                return choice
            print("Неверный выбор!")
    
    def _switch_turn(self):
        self._current_turn = self._current_turn.opposite()
    
    def _check_game_over(self):
        if self._board.is_checkmate(self._current_turn):
            self._game_over = True
            self._winner = self._current_turn.opposite()
            winner = "Белые" if self._winner == Color.WHITE else "Черные"
            print("\nМАТ! " + winner + " победили!")
            
        elif self._board.is_stalemate(self._current_turn):
            self._game_over = True
            print("\nПАТ! Ничья!")
    
    def show_move_history(self):
        if not self._board.move_history:
            print("История пуста.")
            return
        
        print("\nИстория ходов:")
        for i, move in enumerate(self._board.move_history, 1):
            turn = "Б" if move.piece.color == Color.WHITE else "Ч"
            print(str(i) + ". " + turn + ": " + str(move))
    
    def play(self):
        print("\nШахматы - ООП версия")
        print("Команды: e2e4, undo, history, help, quit")
        
        self.new_game()
        
        while not self._game_over:
            self.display_board()
            
            user_input = input("\nХод: ").strip().lower()
            
            if not user_input:
                continue
            
            if user_input in ['quit', 'q']:
                print("Выход.")
                break
            
            if user_input in ['undo', 'u']:
                self.undo()
                continue
            
            if user_input in ['history', 'h']:
                self.show_move_history()
                continue
            
            if user_input == 'help':
                print("e2e4 - ход, e2 - выбрать фигуру")
                print("undo - отмена, history - история")
                print("quit - выход")
                continue
            
            if user_input == 'new':
                self.new_game()
                print("Новая игра!")
                continue
            
            parts = user_input.replace(' ', '').replace('-', '')
            
            if len(parts) == 2:
                self.select_piece(parts)
                continue
            
            if len(parts) == 4:
                start = parts[:2]
                end = parts[2:]
                self.make_move(start, end)
                continue
            
            print("Неверный формат! help - справка")


def main():
    game = ChessGame()
    game.play()


if __name__ == "__main__":
    main()
