#!python3
import numpy as np

base = 10


class Scale:
    # https://en.wikipedia.org/wiki/Long_and_short_scales

    grouping = 3

    @classmethod
    def vocabulary(cls):
        return {100: 'hundred', 1000: 'thousand'}

    # million, billion, etc.
    prefixes = {
        1: 'm',
        2: 'b',
        3: 'tr',
        4: 'quadr',
        5: 'quint',
        6: 'sext',
        7: 'sept',
        8: 'oct',
        9: 'non',
        10: 'dec',
        11: 'undec',
        12: 'duodec',
    }

    @classmethod
    def relevant_vocabulary(cls, x: int) -> dict:
        ''' Which vocabulary items are no greater than the integer `x`?
        '''
        return {
            power_of_ten: name for power_of_ten, name in cls.vocabulary().items()
            if power_of_ten <= x
        }

class ShortScale(Scale):

    @classmethod
    def illion(cls, n: int) -> int:
        ''' An `n`-illion is `10 ** (3 * n + 3)`.
        '''
        return cls.grouping * n + cls.grouping

    @classmethod
    def vocabulary(cls):
        return super().vocabulary() | {
            10 ** cls.illion(n): f'{prefix}illion'
            for n, prefix in cls.prefixes.items()
        }


class LongScale(Scale):

    @classmethod
    def illion(cls, n: int) -> int:
        ''' An `n`-illion is `10 ** (6 * n)`.
        '''
        return 2 * cls.grouping * n

    @classmethod
    def illiard(cls, n: int) -> int:
        ''' An `n`-illiard is `10 ** (6 * n + 3)`,
            i.e. a thousand `n`-illion.
        '''
        return 2 * cls.grouping * n + cls.grouping

    @classmethod
    def vocabulary(cls):
        return super().vocabulary() | {
            10 ** cls.illion(n): f'{prefix}illion'
            for n, prefix in cls.prefixes.items()
        } | {
            10 ** cls.illiard(n): f'{prefix}illiard'
            for n, prefix in cls.prefixes.items()
        }


def test_scales():

    assert ShortScale.illion(1) == 6
    assert ShortScale.illion(2) == 9
    assert LongScale .illion(1) == 6
    assert LongScale .illion(2) == 12

    assert ShortScale.vocabulary()[10 **  6] ==  'million'
    assert ShortScale.vocabulary()[10 **  9] ==  'billion'
    assert ShortScale.vocabulary()[10 ** 12] == 'trillion'

    assert {v: k for k, v in LongScale.vocabulary().items()}['milliard'] \
        == {v: k for k, v in ShortScale.vocabulary().items()}['billion']


def int2en(i: int, *, scale: type = ShortScale,
           two_digit_linker: str = '-', thousands_separator: str =',',
           do_say_and: bool = True,
           do_warn: bool = False,
           negative_or_minus: str = 'negative') -> str:
    ''' Return a written-English representation of the integer `i`.

    `two_digit_linker`: For cardinals in the 20-100 range,
        we may choose to write either e.g. "twenty one" or "twenty-one".
        Therefore, a choice can be made between `' '` and `'-'`.

    `do_say_and`: e.g. "one hundred and eighteen" vs "one hundred eighteen"
    '''

    if i < 0:
        assert negative_or_minus in ('negative', 'minus')
        return f'{negative_or_minus} {int2en(-i)}'

    q, r = divmod(i, base)

    # 0-9
    if q == 0:
        return basic[r]

    # 10-19
    if q == 1:
        return (ten | lefts | teens)[r]

    # 20-99
    if q < base:
        part1 = ties[q]
        if not r: return part1
        part2 = int2en(r)
        return f'{part1}{two_digit_linker}{part2}'

    # 100+

    # Use the greatest relevant vocabulary item first
    power_of_ten, name = max(scale.relevant_vocabulary(i).items())
    q, r = divmod(i, power_of_ten)
    if do_warn and q >= power_of_ten:
        # We shall then be saying things like "billion billion"
        print(f'Overflow: {i} = {q} × {power_of_ten} + {r}')
    part1 = f'{int2en(q)} {name}'
    if not r: return part1
    part2 = int2en(r)
    return f'{part1}{thousands_separator} {part2}' \
        if scale.relevant_vocabulary(r) \
        else f'{part1} and {part2}' \
        if do_say_and \
        else f'{part1} {part2}'


basic = {0: 'zero',
         1: 'one',
         2: 'two',
         3: 'three',
         4: 'four',
         5: 'five',
         6: 'six',
         7: 'seven', 
         8: 'eight',
         9: 'nine'}

ten = {0: 'ten'}

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


def demo(n: int = 10):

    xs = np.abs(np.random.randn(n) * 1E3).astype(int)
    for x in xs:
        print(f'{x:,}: {int2en(x)}', end='\n\n')


if __name__ == '__main__':

    demo()
