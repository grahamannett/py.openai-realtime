from array import array
import random
import string


def generate_id(prefix: str, length: int = 21) -> str:
    """
    Generate a random ID with a given prefix.

    This function creates a unique identifier by combining a provided prefix
    with a random string of characters. The total length of the ID is
    determined by the 'length' parameter, which includes the prefix.

    Args:
        prefix (str): The string to be prepended to the random part of the ID.
        length (int, optional): The total length of the generated ID, including
                                the prefix. Defaults to 21.

    Returns:
        str: A string containing the prefix followed by random characters,
             with a total length equal to the 'length' parameter.

    Note:
        The random part of the ID is generated using digits (1-9) and
        both uppercase and lowercase ASCII letters.
    """
    return prefix + "".join(random.choices(string.digits[1:] + string.ascii_letters, k=length - len(prefix)))


def merge_arrays(arr1: list[int] | array, arr2: list[int] | array, use_array: bool = False) -> list[int]:
    """
    Merge two arrays of 16-bit integers into a single array.

    This function takes two arrays of 16-bit integers and merges them into a single array.
    The resulting array contains all elements from both input arrays, maintaining the order.

    Args:
        arr1 (list[int] | array): The first array of 16-bit integers.
        arr2 (list[int] | array): The second array of 16-bit integers.

    Returns:
        list[int]: A new array containing all elements from both input arrays.

    Note:
        This function assumes that both input arrays are of the same type (either both lists or both arrays).
    """

    arr1.extend(arr2)

    if use_array:
        return array("h", arr1)

    return arr1
