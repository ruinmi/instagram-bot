import math
import random


def to_base36(num: int) -> str:
    """将整数转换为36进制字符串（小写字母表示）"""
    if num < 0:
        return '-' + to_base36(-num)
    if num == 0:
        return '0'

    digits = '0123456789abcdefghijklmnopqrstuvwxyz'
    result = ''
    while num > 0:
        num, remainder = divmod(num, 36)
        result = digits[remainder] + result
    return result


def get_tab_id():
    a = to_base36(math.floor(random.random() * 2176782336))
    return "0" * (6 - len(a)) + a