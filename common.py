import os
import time
import hashlib


def cache_function_result(cache_duration=60):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate a unique filename based on the function name and arguments
            cache_key = f"{func.__name__}_{args}_{kwargs}"
            file_name = f"cache/{hashlib.md5(cache_key.encode()).hexdigest()}.cache"

            # Check if cache file exists
            if os.path.exists(file_name):
                with open(file_name, 'r') as f:
                    cached_time = float(f.readline().strip())  # First line is the timestamp
                    result = f.read()  # Rest of the file is the result
                    # If cache is still valid (within the specified duration)
                    if time.time() - cached_time < cache_duration:
                        print("Using cached result.")
                        return result

            # Calculate new result if cache is expired or doesn't exist
            print("Calculating new result.")
            result = func(*args, **kwargs)
            with open(file_name, 'w') as f:
                f.write(f"{time.time()}\n")  # Write the current time as the first line
                f.write(result)  # Write the result as plain text
            return result

        return wrapper

    return decorator
