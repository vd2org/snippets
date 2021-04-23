# This snippet subclassing the list that implements map() and filter() methods.

# Motivation: Add to the list class ability to do map and filter with more graceful way.


from typing import Callable, Iterable, TypeVar, Generic, Iterator

T = TypeVar('T')
R = TypeVar('R')


class Functions(Generic[T, R]):
    def __iter__(self) -> Iterable:
        raise NotImplemented

    def map(self, func: Callable[[T], R]) -> 'Map[T, R]':
        return Map(self, func)

    def filter(self, func: Callable[[T], bool]) -> 'Filter[T, T]':
        return Filter(self, func)


class Map(Functions, Generic[T, R]):
    def __init__(self, iterable: Iterable, func: Callable[[T], R]):
        self._iter = map(func, iterable)

    def __iter__(self) -> Iterator[R]:
        return self._iter

    def __next__(self) -> T:
        return next(self._iter)

    def next(self) -> T:
        return next(iter(self))

    def flist(self) -> 'FList[R]':
        return FList(self)


class Filter(Functions, Generic[T, R]):
    def __init__(self, iterable: Iterable, func: Callable[[T], bool]):
        self._iter = filter(func, iterable)

    def __iter__(self) -> Iterator[T]:
        return self._iter

    def __next__(self) -> T:
        return next(self._iter)

    def next(self) -> T:
        return next(iter(self))

    def flist(self) -> 'FList[T]':
        return FList(self)


class FList(list, Functions, Generic[T]):
    pass


if __name__ == "__main__":
    test = FList([1, 2, 3, 4])

    print(type(test))
    print(test)

    double_map = test.map(lambda x: x * 2).map(lambda x: x * 2)
    print(FList(double_map))

    filter_map = test.filter(lambda x: not x % 2).map(lambda x: x * 2)
    print(FList(filter_map))

    different_type = test.map(lambda x: str(x))
    print(FList(different_type))
