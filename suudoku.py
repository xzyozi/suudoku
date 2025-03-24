import random 
from typing import List, Tuple, Any
import copy
from copy import deepcopy
from collections import Counter
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

DEF_MAP = [ [0,0,0,0,1,0,5,0,0],
            [7,6,5,0,0,0,0,0,0],
            [8,0,0,0,0,0,2,0,0],
            [2,0,0,0,8,6,0,0,0],
            [0,0,7,0,0,0,0,0,0],
            [0,5,0,3,9,2,0,0,0],
            [0,0,0,5,0,0,0,0,1],
            [0,0,9,0,0,0,4,0,8],
            [0,0,1,6,3,0,0,9,0]

]

ditect_map = deepcopy(DEF_MAP)

# +---------------------------------------------------------------------------------------
# + 判定関数
# +---------------------------------------------------------------------------------------
def allowValue( 
            line: List[int] 
            ) -> List[int]:
    result_list = []
    for num in range(1,10):
        if not num in line:
            result_list.append(num)

    return result_list

def extract_square(matrix, 
                   x : int,
                   y : int, 
                   size=3
                   ):

    if y in [0,1,2] :
        start_row = 0
    elif y in [3,4,5]:
        start_row = 3
    elif y in [6,7,8] :
        start_row = 6
    else : raise("input y error")

    if x in [0,1,2] :
        start_col = 0
    elif x in [3,4,5]:
        start_col = 3
    elif x in [6,7,8] :
        start_col = 6
    else : raise("input x error")    

    return [row[start_col:start_col + size] for row in matrix[start_row:start_row + size]]

def restructure_list(square):
    """
    2Dリストを1Dリストに変換し、重複を除去、0をスキップ
    """
    unique_values = set()  # 重複チェック用のセット
    result_list = []
    
    for row in square:
        for value in row:
            if value != 0 and value not in unique_values:
                unique_values.add(value)
                result_list.append(value)

    return result_list

def merge_unique(*lists):
    """
    複数のリストを統合し、重複を削除したリストを返す
    """
    unique_values = set()  # 重複を除去するためのセット
    result_list = []

    for lst in lists:
        for value in lst:
            if value not in unique_values:
                unique_values.add(value)
                result_list.append(value)

    return result_list

def merge_common(*lists):
    """
    複数のリストから共通する要素のみを抽出して返す
    """
    if not lists:
        return []

    # 最初のリストを基準にして、他のリストと共通する要素を求める
    common_values = set(lists[0])
    for lst in lists[1:]:
        common_values.intersection_update(lst)

    return list(common_values)

def extract_unique(*lists) -> Tuple[List,int]:
    """
    複数のリストの中で、一意に存在する要素のみを抽出する
    """
    # 各リストのインデックスを保持
    index_map = {}  # { 要素: どのリストの要素か } 
    all_elements = []  # すべての要素を集約
    unique_index_num = 0

    for i, lst in enumerate(lists):
        for value in lst:
            all_elements.append(value)
            if value in index_map:
                index_map[value].add(i)  # すでに存在する場合、リストのインデックスを追加
            else:
                index_map[value] = {i}  # 初回登録

    # 各要素の出現回数をカウント
    counts = Counter(all_elements)

    # 1回しか登場しない要素を抽出
    unique_values = [key for key, count in counts.items() if count == 1]

    unique_indices = {key: index_map[key] for key in unique_values}
    # if 1 == len(unique_values):

    #     for key,val in unique_indices.items() :
    #         print(val,key,type(val),type(key))
    #         unique_index_num = val
    if len(unique_values) >= 1 :
        unique_index_num = unique_indices[unique_values[0]].pop()
        #print(unique_index_num,type(unique_index_num))

    return unique_values, unique_index_num

def split_matrix_and_extract(*matrices) -> Tuple[List,int]:
    """
    複数の行列 (list[list[int]]) を個別のリストに展開し、 extract_unique() に渡す
    """
    # 各行列を行ごとに分割
    separated_lists = [row for matrix in matrices for row in matrix]

    # 一意な要素を取得
    return extract_unique(*separated_lists)

def allowLists(x: int , 
             y: int ,
             map : List[List[int]]
             ) -> List[int]:

    square_list = []

    row_list = map[y]

    col_map = [list(line) for line in zip(*map)]

    square_matrix = extract_square(map,x,y)
    square_list = restructure_list(square_matrix)

    # print(row_list)
    # print(col_map[x])
    # print(square_list)

    result_list = row_list + col_map[x] + square_list

    return allowValue(result_list)


def scanMemo(std_map:List[List[int]],
             std_memo_map : List[List[List[int]]]     
             ) -> bool:
    flg = False

    # row scan


    for y,line in enumerate(std_memo_map) :
        unique_index_num = 0
        row_list, unique_index_num = split_matrix_and_extract(line)
        
        if row_list and std_map[y][unique_index_num] == 0 :
            logger.info("row update ")
            logger.info(f"y[{y}]x[{unique_index_num}]list[{row_list}][{std_map[y][unique_index_num]}]")
            std_map[y][unique_index_num] = row_list[0]
            std_memo_map[y][unique_index_num]= []
            updataMemo(y,unique_index_num,row_list[0],std_map,std_memo_map)
            flg = True
            break


    if flg :
        return flg
        
    # line scan
    for x, col in enumerate(zip(*std_memo_map)):  # 列ごとに処理
        unique_index_num = 0
        col_list, unique_index_num = split_matrix_and_extract(list(col))

        if col_list and std_map[unique_index_num][x] == 0 :
            print("line update")
            print(x, unique_index_num, col_list, std_map[unique_index_num][x])
            std_map[unique_index_num][x] = col_list[0]
            std_memo_map[unique_index_num][x] = []
            updataMemo(unique_index_num, x,   col_list[0], std_map, std_memo_map)
            flg = True
            break

    if flg:
        return flg


    # --- Square Scan ---
    for x in range(0, 9, 3):
        if flg:
            break
        for y in range(0, 9, 3):
            square_matrix = extract_square(std_memo_map, x, y)

            logger.info("-------------------------------------------------------")
            print_matrix(square_matrix)  # デバッグ用出力

            merge_square = [point for line in square_matrix for point in line]  # 1次元リストに変換

            logger.info(merge_square)

            square_list, index_num = split_matrix_and_extract(merge_square)
            if square_list and index_num is not None:
                chg_y = index_num // 3
                chg_x = index_num % 3
                target_x = x + chg_x
                target_y = y + chg_y

                if std_map[target_y][target_x] == 0:  # 0 の場合にのみ更新
                    flg = True
                    logger.info(f"({square_list}), {index_num}, x[{target_x}] y[{target_y}]")
                    logger.info(f"Before update: {std_map[target_y][target_x]}")
                    std_map[target_y][target_x] = square_list[0]
                    logger.info(f"After update: {std_map[target_y][target_x]}")

                    std_memo_map[target_y][target_x] = []  # 確定値を削除
                    updataMemo(target_x, target_y, square_list[0], std_map, std_memo_map)
                    break

    

    if flg :
        return flg


    return flg


def updataMemo(x,y,value,std_map,std_memo_map):
    
    upd_flg = False

    log_xStr, log_yStr, log_sqStr = "", "", ""

    for point_x in range(9):
        log_xStr +=f"({point_x},{y}){std_memo_map[point_x][y]}--"
        if not std_memo_map[point_x][y] : continue

        if value in std_memo_map[point_x][y]:
            std_memo_map[point_x][y].remove(value)
    logger.info(log_xStr)

    for point_y in range(9):
        log_yStr += f"({x},{point_y}){std_memo_map[x][point_y]}--"
        if not std_memo_map[x][point_y] : continue

        if value in std_memo_map[x][point_y] :
            std_memo_map[x][point_y].remove(value)
    logger.info(log_yStr)


    # --- 3×3 Square Update ---
    base_x, base_y = (x // 3) * 3, (y // 3) * 3  # 3×3 のブロックの左上座標
    for dx in range(3):
        for dy in range(3):
            target_x, target_y = base_x + dx, base_y + dy
            log_sqStr += f"({target_x},{target_y}){std_memo_map[target_x][target_y]}--"
            if std_memo_map[target_x][target_y] and value in std_memo_map[target_x][target_y]:
                std_memo_map[target_x][target_y].remove(value)

    logger.info(log_sqStr)


    return upd_flg


def updata_chkMemo(std_map,
                   std_memo_map
                   ) -> bool :
    
    upd_flg = False
    # memo chk
    for upd_x, upd_line in enumerate(std_memo_map):
        if upd_flg :
            break
        for upd_y, upd_point in enumerate(upd_line):
            if 1 == len(upd_point) and 0 == std_map[upd_x][upd_y]:
                print(f"★ {upd_x}:{upd_y} -- {std_map[upd_x][upd_y]} -- {std_memo_map[upd_x][upd_y]} -- {len(upd_point)}")
                std_map[upd_x][upd_y] = upd_point[0]
                std_memo_map[upd_x][upd_y] = []
                updataMemo(upd_y,upd_x,upd_point[0],std_map,std_memo_map)
                upd_flg = True
                break




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

# allows_v = allowLists(3,1,std_map)

# print(allows_v)


# +---------------------------------------------------------------------------------------
# + 複合関数
# +---------------------------------------------------------------------------------------
def full_scan(std_map : List[List[int]], 
              memo_map,
              make_memo_flg = False
              ) -> bool:
    count = 0
    upd_flg = False
    memo_count = 0

    for x,line in enumerate(std_map) :
        memo_line= []

        for y,point in enumerate(line):
            count+=1
            if 0 != std_map[x][y] :

                memo_line.append([])
                continue

            allows_v = allowLists(y,x,std_map)
            if len(allows_v) == 1 :
                std_map[x][y] = allows_v[0]
                allows_v.clear()
                upd_flg = True

            memo_line.append(allows_v)
        
        else :
            if make_memo_flg :
                memo_map.append(memo_line)
            memo_count += 1



        #print(std_map)
    # print(count,len(memo_map))


def main():
    update_flg = True
    memo_update_flg = True
    memo_map = []
    # print_matrix(ditect_map)
    full_scan(ditect_map,memo_map,make_memo_flg=True)

    # while memo_update_flg:

    for _ in range(50):
        print_matrix(ditect_map)
        print_matrix(memo_map)
        # full_scan(ditect_map,memo_map)

        if scanMemo(ditect_map,memo_map) :
            continue

        if updata_chkMemo(ditect_map,memo_map):
            continue

        # if updata_chkMemo(ditect_map,memo_map) :
        #     memo_update_flg = True

    print_matrix(ditect_map)
    
    print_matrix(memo_map)


main()

for x in range(0,9,3):
    for y in range(0,9,3):
        pass