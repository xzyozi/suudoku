from typing import List, Set, Optional, Tuple, Any

from copy import deepcopy

import logging 

logger = logging.getLogger(__name__)

# フォーマッタの作成
formatter = logging.Formatter('[%(lineno)d LINE][%(funcName)s] - %(message)s')

# コンソールハンドラの作成
handler = logging.StreamHandler()

handler.setLevel(logging.DEBUG)
# ハンドラにフォーマッタを設定
handler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.propagate = False

DEF_MAP = [ [0,0,0,1,0,0,0,0,0],
            [4,3,0,0,6,0,7,0,0],
            [0,0,0,9,0,0,0,0,8],
            [0,0,6,5,0,2,0,0,0],
            [0,7,0,0,0,1,3,0,0],
            [0,9,0,0,0,0,5,4,0],
            [0,0,0,0,5,0,0,0,7],
            [0,0,0,7,0,0,4,1,0],
            [0,0,3,0,0,6,0,5,0] 
            ]
# https://si-coding.net/20250322/sudoku9.html#content

DEF_MAP = [ [0,0,4,0,0,3,0,2,0],
            [0,0,8,0,1,0,0,0,0],
            [2,1,0,0,0,7,9,0,0],
            [0,0,0,0,0,9,0,0,5],
            [3,6,0,0,7,0,0,8,0],
            [0,0,1,0,0,0,0,0,0],
            [7,2,0,0,6,0,0,3,0],
            [4,0,0,0,0,0,0,0,0],
            [0,0,0,3,0,0,8,0,0]

]

ditect_map = deepcopy(DEF_MAP)

# +---------------------------------------------------------------------------------------
# + 判定関数
# +---------------------------------------------------------------------------------------
def initialize_memo_map(board: List[List[int]]) -> List[List[Set[int]]]:
    """
    各マスに入る可能性のある数字をセットで保持するメモマップを初期化する。

    Args:
        board (List[List[int]]): 数独の初期盤面 (9x9)

    Returns:
        List[List[Set[int]]]: 各マスに入る可能性のある数字のセットを持つメモマップ
    """
    memo_map: List[List[Set[int]]] = [[set(range(1, 10)) for _ in range(9)] for _ in range(9)]

    for row in range(9):
        for col in range(9):
            num = board[row][col]
            if num != 0:
                memo_map[row][col] = {num}
                update_memo_map(memo_map, row, col, num)

    logger.debug("Initialized memo_map:\n%s", memo_map)
    return memo_map

def update_memo_map(memo_map: List[List[Set[int]]], row: int, col: int, num: int) -> None:
    """
    確定した数字をメモマップから削除する。

    Args:
        memo_map (List[List[Set[int]]]): 各マスの候補数字を保持するメモマップ
        row (int): 更新対象の行
        col (int): 更新対象の列
        num (int): 確定した数字
    """
    logger.debug("Updating memo_map at (%d, %d) with num=%d", row, col, num)

    for i in range(9):
        memo_map[row][i].discard(num)
        memo_map[i][col].discard(num)

    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            memo_map[start_row + i][start_col + j].discard(num)

def find_next_cell(memo_map: List[List[Set[int]]], board: List[List[int]]) -> Optional[Tuple[int, int]]:
    """
    次に試行するマスを選択する（最小候補のマスを優先）。

    Args:
        memo_map (List[List[Set[int]]]): 各マスの候補数字を保持するメモマップ
        board (List[List[int]]): 数独の盤面

    Returns:
        Optional[Tuple[int, int]]: 試行すべきマスの座標 (row, col) または None
    """
    row, col = None, None
    min_candidates = 10  # 1～9なので最大値は10

    for r in range(9):
        for c in range(9):
            if board[r][c] == 0 and 0 < len(memo_map[r][c]) < min_candidates:
                row, col = r, c
                min_candidates = len(memo_map[r][c])

    return (row, col) if row is not None else None

def solve_with_memo(board: List[List[int]], memo_map: List[List[Set[int]]]) -> bool:
    """
    メモマップを使用して数独を解く。

    Args:
        board (List[List[int]]): 数独の盤面
        memo_map (List[List[Set[int]]]): 各マスの候補数字を保持するメモマップ

    Returns:
        bool: 解が見つかった場合は True、それ以外は False
    """
    while True:
        updated = False
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0 and len(memo_map[row][col]) == 1:
                    num = memo_map[row][col].pop()
                    board[row][col] = num
                    update_memo_map(memo_map, row, col, num)
                    logger.debug("Filled (%d, %d) with %d", row, col, num)
                    updated = True

        if not updated:
            break  # これ以上確定できるマスがない場合は終了

    if all(board[row][col] != 0 for row in range(9) for col in range(9)):
        return True

    next_cell = find_next_cell(memo_map, board)
    if next_cell is None:
        return False

    row, col = next_cell

    for num in memo_map[row][col]:
        board_copy = [r[:] for r in board]
        memo_copy = [list(map(set, r)) for r in memo_map]

        board_copy[row][col] = num
        update_memo_map(memo_copy, row, col, num)
        logger.debug("Trying %d at (%d, %d)", num, row, col)

        if solve_with_memo(board_copy, memo_copy):
            board[:] = board_copy
            return True

    return False



def format_matrix(matrix: List[Any], depth: int = 0) -> str:
    """
    任意の次元のリスト (最大3次元) を整形して見やすく表示する
    """
    indent = "    " * depth  # ネストの深さに応じたインデント
    if isinstance(matrix, list):
        if not matrix:  # 空リストの場合
            return indent + "[]"
        if isinstance(matrix[0], list):  # 2次元以上
            return indent + "[\n" + ",\n".join(format_matrix(row, depth + 1) for row in matrix) + "\n" + indent + "]"
        else:  # 1次元リスト
            return indent + "[" + ", ".join(map(str, matrix)) + "]"
    else:  # 予期しないデータ型
        return indent + str(matrix)

def print_matrix(matrix: List[Any]):
    """
    任意の次元のリストを整形して表示
    """
    logger.info(format_matrix(matrix))


# +---------------------------------------------------------------------------------------
# + 複合関数
# +---------------------------------------------------------------------------------------
solved_board: List[List[int]] = [row[:] for row in ditect_map]
memo_map: List[List[Set[int]]] = initialize_memo_map(solved_board)

if solve_with_memo(solved_board, memo_map):
    logger.info("Sudoku Solved!")
else:
    logger.error("No solution found")

print_matrix(solved_board)
print_matrix(memo_map)