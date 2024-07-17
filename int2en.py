#!python3
import numpy as np

base = 10

NumType = int

Cardinal, Ordinal = 0, 1


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
           do_say_and: bool = True, do_warn: bool = False,
           negative_or_minus: str = 'negative',
           cardinal_or_ordinal: NumType = Cardinal) -> str:
    ''' Return a written-English representation of the integer `i`.

    `two_digit_linker`: For cardinals in the 20-100 range,
        we may choose to write either e.g. "twenty one" or "twenty-one".
        Therefore, a choice can be made between `' '` and `'-'`.

    `do_say_and`: e.g. "one hundred and eighteen" vs "one hundred eighteen"

    `thousands_separator`: e.g. "one thousand, five hundred" vs "one thousand five hundred"

    `negative_or_minus`: e.g. "negative one" vs "minus one"

    `cardinal_or_ordinal`: e.g. "one" vs "first"
    '''

    recurse = lambda i: int2en(i,
                               scale=scale, two_digit_linker=two_digit_linker,
                               thousands_separator=thousands_separator,
                               do_say_and=do_say_and, do_warn=do_warn,
                               negative_or_minus=negative_or_minus,
                               cardinal_or_ordinal=cardinal_or_ordinal)

    if i < 0:
        assert negative_or_minus in ('negative', 'minus')
        return f'{negative_or_minus} {recurse(-i)}'

    q, r = divmod(i, base)

    # 0-9
    if q == 0:
        return _0_to_9[r][cardinal_or_ordinal]

    # 10-19
    if q == 1:
        return _10_to_19[r][cardinal_or_ordinal]

    # 20-99
    if q < base:
        part1 = tens[q]
        if not r: return part1
        part2 = recurse(r)
        return f'{part1}{two_digit_linker}{part2}'

    # 100+

    # Use the greatest relevant vocabulary item first
    power_of_ten, name = max(scale.relevant_vocabulary(i).items())
    q, r = divmod(i, power_of_ten)
    if do_warn and q >= power_of_ten:
        # We shall then be saying things like "billion billion"
        print(f'Overflow: {i} = {q} × {power_of_ten} + {r}')
    part1 = f'{recurse(q)} {name}'
    if not r: return part1
    part2 = recurse(r)
    return f'{part1}{thousands_separator} {part2}' \
        if scale.relevant_vocabulary(r) \
        else f'{part1} and {part2}' \
        if do_say_and \
        else f'{part1} {part2}'


class th:

    def __str__(self) -> str:
        return 'th'

    def __radd__(self, other) -> str:

        match other:
            case str(_): pass
            case _: raise TypeError(other)

        if other.endswith('ve'):
            # 'five' -> 'fifth'
            # # 'twelve' -> 'twelfth'
            other = f'{other.removesuffix('ve')}f'
        if other.endswith('ne'):
            # 'nine' -> 'ninth'
            other = f'{other.removesuffix('ne')}n'
        if other.endswith('ght'):
            # 'eight' -> 'eighth'
            other = f'{other.removesuffix('t')}'

        return other + str(self)

class teen:

    def __str__(self) -> str:
        return 'teen'

    def __radd__(self, other) -> str:

        match other:
            case str(_): pass
            case _: raise TypeError(other)

        if other.endswith('ve'):
            # 'five' -> 'fifteen'
            other = f'{other.removesuffix('ve')}f'
        if other.endswith('ght'):
            # 'eight' -> 'eighteen'
            other = f'{other.removesuffix('t')}'

        return other + str(self)


class ty:

    def __str__(self) -> str:
        return 'ty'

    def __radd__(self, other) -> str:

        match other:
            case str(_): pass
            case _: raise TypeError(other)

        if other.endswith('ve'):
            # 'five' -> 'fifty'
            other = f'{other.removesuffix('ve')}f'
        if other.endswith('ght'):
            # 'eight' -> 'eighty'
            other = f'{other.removesuffix('t')}'

        return other + str(self)


_0_to_9 = {
    0: {Cardinal: 'zero',  Ordinal: 'zero'  + th()},
    1: {Cardinal: 'one',   Ordinal: 'first'       },
    2: {Cardinal: 'two',   Ordinal: 'second'      },
    3: {Cardinal: 'three', Ordinal: 'third'       },
    4: {Cardinal: 'four',  Ordinal: 'four'  + th()},
    5: {Cardinal: 'five',  Ordinal: 'five'  + th()},
    6: {Cardinal: 'six',   Ordinal: 'six'   + th()},
    7: {Cardinal: 'seven', Ordinal: 'seven' + th()},
    8: {Cardinal: 'eight', Ordinal: 'eight' + th()},
    9: {Cardinal: 'nine',  Ordinal: 'nine'  + th()},
}

_10_to_19 = {
    i: {
        Cardinal: root + teen(),
        Ordinal:  root + teen() + th(),
    } for i, root in ({i: item[Cardinal] for i, item in _0_to_9.items()} | {3: 'thir'}).items()
} | {
    0: {Cardinal: 'ten',    Ordinal: 'ten'    + th()},
    1: {Cardinal: 'eleven', Ordinal: 'eleven' + th()},
    2: {Cardinal: 'twelve', Ordinal: 'twelve' + th()},
}

tens = {
    1: _10_to_19[0][Cardinal],  # Not 'onety'
} | {
    i: root + ty() for i, root in ({
        i: root[Cardinal] for i, root in _0_to_9.items()
    } | {
        2: 'twen',  # Not 'twoty'
        3: 'thir',  # Not 'threety'
        4: 'for',   # Not 'fourty'
    }
).items()}


def demo(n: int = 10):

    xs = np.abs(np.random.randn(n) * 1E3).astype(int)
    for x in xs:
        print(f'{x:,}: {int2en(x, cardinal_or_ordinal=Ordinal)}', end='\n\n')


if __name__ == '__main__':

    demo()
