import asyncio
import functools
import time
import logging

logger = logging.getLogger(__name__)


def retry(exceptions=(Exception,), tries=3, delay=1.0, backoff=2.0, logger=logger):
    """
    Retry decorator/wrapper supporting both synchronous and asynchronous functions
    with exponential backoff.

    Args:
        exceptions: A tuple of exception classes to catch.
        tries:      Maximum number of attempts.
        delay:      Initial delay between retries in seconds.
        backoff:    Multiplier applied to delay on each subsequent retry.
        logger:     Logging client for warnings.
    """
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                current_delay = delay
                for attempt in range(1, tries + 1):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        if attempt == tries:
                            if logger:
                                logger.error(
                                    f"Async function '{func.__name__}' failed after {tries} attempts: {e}"
                                )
                            raise e
                        if logger:
                            logger.warning(
                                f"Async function '{func.__name__}' raised {e.__class__.__name__}: {e}. "
                                f"Retrying in {current_delay:.2f} seconds (attempt {attempt}/{tries})..."
                            )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                current_delay = delay
                for attempt in range(1, tries + 1):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        if attempt == tries:
                            if logger:
                                logger.error(
                                    f"Sync function '{func.__name__}' failed after {tries} attempts: {e}"
                                )
                            raise e
                        if logger:
                            logger.warning(
                                f"Sync function '{func.__name__}' raised {e.__class__.__name__}: {e}. "
                                f"Retrying in {current_delay:.2f} seconds (attempt {attempt}/{tries})..."
                            )
                        time.sleep(current_delay)
                        current_delay *= backoff
            return sync_wrapper
    return decorator
