#!/usr/bin/env python3
"""
This module provides a function to fetch a webpage and cache its content
in Redis with an expiration time, while tracking the number of accesses
to each URL.
"""
import redis
import requests
from typing import Callable
from functools import wraps


redis_client = redis.Redis()


def count_accesses(method: Callable) -> Callable:
    """
    Decorator to count the number of accesses to a URL.

    Args:
        method (Callable): The method to be decorated.

    Returns:
        Callable: The wrapped method.
    """
    @wraps(method)
    def wrapper(url: str, *args, **kwargs) -> str:
        """
        Wrapper function that increments the access count for the URL
        and calls the original method.
        """
        redis_client.incr(f"count:{url}")
        return method(url, *args, **kwargs)
    return wrapper


@count_accesses
def get_page(url: str) -> str:
    """
    Fetch the HTML content of a URL and cache it in Redis with an
    expiration time.

    Args:
        url (str): The URL to fetch.

    Returns:
        str: The HTML content of the URL.
    """
    cached_page = redis_client.get(f"cached:{url}")
    if cached_page:
        return cached_page.decode('utf-8')

    response = requests.get(url)
    html_content = response.text

    redis_client.setex(f"cached:{url}", 10, html_content)
    return html_content


if __name__ == "__main__":
    url = ("http://slowwly.robertomurray.co.uk/delay/3000/url/"
           "http://www.google.co.uk")
    print(get_page(url))
    print(redis_client.get(f"count:{url}").decode('utf-8'))
