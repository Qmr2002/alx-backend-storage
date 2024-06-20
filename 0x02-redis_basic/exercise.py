#!/usr/bin/env python3
"""
This module contains the Cache class which provides a simple interface
to store data in Redis, as well as decorators to count method calls and
store call history.
"""
import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """
    Decorator to count the number of calls to a method.

    Args:
        method (Callable): The method to be decorated.

    Returns:
        Callable: The wrapped method.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function that increments the call count and calls
        the original method.
        """
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and outputs of a method.

    Args:
        method (Callable): The method to be decorated.

    Returns:
        Callable: The wrapped method.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function that stores inputs and outputs history and
        calls the original method.
        """
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        self._redis.rpush(input_key, str(args))
        output = method(self, *args, **kwargs)
        self._redis.rpush(output_key, str(output))
        return output

    return wrapper


class Cache:
    """
    Cache class for storing data in Redis with random keys.
    """

    def __init__(self):
        """
        Initialize the Cache instance.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store the given data in Redis with a random key.

        Args:
            data (Union[str, bytes, int, float]): The data to be stored.

        Returns:
            str: The key under which the data is stored.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[
            str, bytes, int, float, None]:
        """
        Retrieve the data stored in Redis for the given key and optionally
        convert it using the provided function.

        Args:
            key (str): The key of the data to retrieve.
            fn (Callable, optional): A function to convert the data.
            Defaults to None.

        Returns:
            Union[str, bytes, int, float, None]: The retrieved data or
            None if the key does not exist.
        """
        data = self._redis.get(key)
        if data is None:
            return None
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> Optional[str]:
        """
        Retrieve the data stored in Redis for the given key and convert it
        to a string.

        Args:
            key (str): The key of the data to retrieve.

        Returns:
            Optional[str]: The retrieved data as a string or None if the key
            does not exist.
        """
        return self.get(key, fn=lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieve the data stored in Redis for the given key and convert it
        to an integer.

        Args:
            key (str): The key of the data to retrieve.

        Returns:
            Optional[int]: The retrieved data as an integer or None if the key
            does not exist.
        """
        return self.get(key, fn=int)


def replay(method: Callable):
    """
    Display the history of calls of a particular function.

    Args:
        method (Callable): The method whose history to display.
    """
    redis_instance = redis.Redis()
    input_key = f"{method.__qualname__}:inputs"
    output_key = f"{method.__qualname__}:outputs"

    inputs = redis_instance.lrange(input_key, 0, -1)
    outputs = redis_instance.lrange(output_key, 0, -1)

    print(f"{method.__qualname__} was called {len(inputs)} times:")
    for inp, out in zip(inputs, outputs):
        print(f"{method.__qualname__}(*{inp.decode('utf-8')}) -> "
              f"{out.decode('utf-8')}")
