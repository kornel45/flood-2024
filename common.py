import hashlib
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)


def cache_function_result():
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate a unique filename based on the function name and arguments
            cache_key = f"{func.__name__}_{args}_{kwargs}"
            if not os.path.isdir('cache'):
                os.mkdir('cache')
            file_name = f"cache/{hashlib.md5(cache_key.encode()).hexdigest()}.cache"
            # Check if cache file exists
            if os.path.exists(file_name):
                with open(file_name, 'r') as f:
                    result = f.read()  # Rest of the file is the result
                    return result

            # Calculate new result if cache is expired or doesn't exist
            logger.info("Calculating new result.")
            result = func(*args, **kwargs)
            with open(file_name, 'w') as f:
                f.write(result)  # Write the result as plain text
            return result

        return wrapper

    return decorator
