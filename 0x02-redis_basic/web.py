#!/usr/bin/env python3
import requests
import redis
from functools import wraps
import time

# Initialize Redis client
cache = redis.Redis(host='localhost', port=6379, db=0)

def cache_page(func):
    @wraps(func)
    def wrapper(url):
        # Check if the URL result is cached
        cached_page = cache.get(f"cache:{url}")
        if cached_page:
            return cached_page.decode('utf-8')

        # Fetch the page content
        page_content = func(url)

        # Cache the result with an expiration time of 10 seconds
        cache.setex(f"cache:{url}", 10, page_content)

        return page_content

    return wrapper

def track_access(func):
    @wraps(func)
    def wrapper(url):
        # Increment the access count for the URL
        cache.incr(f"count:{url}")

        return func(url)

    return wrapper

@track_access
@cache_page
def get_page(url: str) -> str:
    response = requests.get(url)
    return response.text

# Example Usage
if __name__ == "__main__":
    test_url = "http://slowwly.robertomurray.co.uk/delay/5000/url/http://www.google.co.uk"

    # Fetch the page twice to see caching in action
    print(get_page(test_url))
    time.sleep(5)
    print(get_page(test_url))
    time.sleep(5)
    print(get_page(test_url))

    # Print access count
    print(f"Access count for {test_url}: {cache.get(f'count:{test_url}').decode('utf-8')}")
