from .Types import SpecialGenerator
from .Types import ExpandableTuple


__all__ = ["product", "expand_product_result", "combine_wordlists"]


def product(iterable_: iter, length: int, join=False):
    """Custom cartesian product that creates product on the fly

    Arguments:
        - iterable_: iterable object
        - length: length of products generated
        - join: (Default=False) When the iterable is a string you can put this to True so the generated words are string

    Returns:
        - Yields a tuple if join is set to False otherwise yields strings
    """
    try:
        iterable_ = tuple(set(iterable_))
    except TypeError:
        pass
    if length < 1:
        raise ValueError("Invalid length supplied")
    indexes = [0] * length
    chars_length = len(iterable_)
    while True:
        if not join:
            yield tuple(iterable_[index] for index in indexes)
        else:
            yield "".join(iterable_[index] for index in indexes)
        for index, index_value in enumerate(indexes):
            if indexes[index] < chars_length - 1:
                indexes[index] += 1
                break
            else:
                indexes[index] = 0
        if all(index == 0 for index in indexes):
            break


def expand_product_result(product_: tuple) -> list:
    """This function expand in it's correct way, the arguments provided by custom product

    Arguments:
        - product: The tuple containing the arguments

    Returns:
        - A sanitized tuple of arguments (sanitized as it eliminates one tuple in another, in another ...)
    """
    result = []
    for value in product_:
        if isinstance(value, ExpandableTuple):
            result += expand_product_result(value)
        elif isinstance(value, tuple):
            if len(value) == 1:  # If the tuple is just one argument
                result.append(value[0])
            else:
                result.append(value)
        else:
            result.append(value)
    return result


# Maybe useless
# Expected input
# [bftool.Types.SpecialGenerator, list, tuple, set, dict, ...] (list of iterables)
def combine_wordlists(iterables_: list, master=True):
    """This function is intended to handle the cartesian product of all arguments

    Arguments:
        - iterables_: This should be a list contains all the bruteforce rules, file reader generator and iterables you
        - want to combine

    Returns:
        - It yields the combinations of the input wordlists
    """
    number_of_iterables = len(iterables_)
    if isinstance(iterables_[0], SpecialGenerator):
        cycle_iterable = iterables_[0]()
    else:
        cycle_iterable = iterables_[0]
    if number_of_iterables == 1:
        for value in cycle_iterable:
            yield value,
    elif number_of_iterables > 1:
        for value in cycle_iterable:
            for second_value in combine_wordlists(iterables_[1:], False):
                second_value = ExpandableTuple(second_value)
                if master:
                    # When is the master function (the one that the user called), normalize it's values
                    yield expand_product_result((value, second_value))
                else:
                    yield value, second_value
    else:
        raise IndexError("Invalid number of arguments")
