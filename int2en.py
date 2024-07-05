#!python3
import random

base = 10

space = ' '

def int2en(i: int) -> str:
    ''' Return a written-English representation of the integer `i`.
    '''

    if i < 0:
        return f'negative {int2en(-i)}'

    # "Basic" numbers: zero to ten
    if i <= base:
        return basic[i]

    q, r = divmod(i, base)

    # Eleven, twelve, and the "teens"
    if q == 1:
        return (lefts | teens)[r]

    # Numbers between twenty and one hundred
    if q < base:  # i.e. digits(i, 2)
        return twenty2onehundred(i)

    # "Medium-sized" numbers: one hundred to one thousand
    if digits(i, ShortScale.illion(0)):
        return place_value(i, 2, 'hundred')

    # "Big" numbers: one thousand and above
    for x, name in ({0: 'thousand'} | illions).items():
        if digits(i, ShortScale.illion(x + 1)):
            return place_value(i, ShortScale.illion(x), name)

    raise ValueError(i)


basic = {0: 'zero',
         1: 'one',
         2: 'two',
         3: 'three',
         4: 'four',
         5: 'five',
         6: 'six',
         7: 'seven', 
         8: 'eight',
         9: 'nine',
        10: 'ten'}

lefts = {1: 'eleven',
         2: 'twelve'}

teens = {3: 'thirteen',
         4: 'fourteen',
         5: 'fifteen',
         6: 'sixteen',
         7: 'seventeen',
         8: 'eighteen', 
         9: 'nineteen'}

ties = {2: 'twenty',
        3: 'thirty',
        4: 'forty',
        5: 'fifty',
        6: 'sixty',
        7: 'seventy',
        8: 'eighty',
        9: 'ninety'}

def digits(i: int, n: int) -> int:
    ''' Can the positive integer `i` be represented with at most `n` digits?
    '''
    return i < base ** n

def how_many_digits(i: int) -> int:
    ''' How many digits are needed to represent the positive integer `i`?
    '''
    n = 0
    while i >= base ** n:
        n += 1
    return n

def twenty2onehundred(i: int) -> str:
    ''' Handle integers in `range(20, 100)`.'''
    assert i in range(2 * base, base ** 2)
    q, r = divmod(i, base)
    head = ties[q]
    if not r: return head
    tail = int2en(r)
    return space.join((head, tail))

def place_value(i: int, exponent: int, name: str) -> str:

    q, r = divmod(i, base ** exponent)
    head = space.join((int2en(q), name))
    if not r: return head
    tail = int2en(r)
    return space.join((head, 'and', tail) if digits(r, 2) else (head, tail))

class ShortScale:

    grouping = 3

    @classmethod
    def illion(cls, n: int) -> int:
        # https://en.wikipedia.org/wiki/Long_and_short_scales
        return cls.grouping * n + cls.grouping

class LongScale:

    grouping = 3

    @classmethod
    def illion(cls, n: int) -> int:
        return 2 * cls.grouping * n

    @classmethod
    def iard(cls, n: int) -> int:
        return 2 * cls.grouping * n + cls.grouping


assert ShortScale.illion(1) == 6
assert ShortScale.illion(2) == 9
assert LongScale .illion(1) == 6
assert LongScale .illion(2) == 12

illions = {
    1: 'million',
    2: 'billion',
    3: 'trillion',
    4: 'quadrillion',
    5: 'quintillion',
    6: 'sextillion',
    7: 'septillion',
    8: 'octillion',
    9: 'nonillion',
   10: 'decillion',
   11: 'undecillion',
   12: 'duodecillion'}


def determine_limit() -> int:
    lim = 1
    try:
        while True:
            int2en(lim)
            lim *= base
    except ValueError as err:
        assert err.args == (lim,)
        return lim


if __name__ == '__main__':

    lim = determine_limit()
    hi = lim - 1
    print(f'We can handle numbers no greater than {lim:.0E} '
          f'(that is, numbers up to {hi:,}, or {int2en(hi)}).')

    for _ in range(10):
        i = random.randint(-lim, +lim)
        print(f'{i:,}', int2en(i))
        print()

