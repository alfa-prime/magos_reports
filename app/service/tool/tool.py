import httpx

def is_retryable_exception(exception) -> bool:
    """Возвращает True, если исключение - это ошибка, которую стоит повторить."""
    if isinstance(exception, (
            httpx.ReadError,
            httpx.ConnectError,
            httpx.ReadTimeout,
            httpx.ConnectTimeout,
            httpx.WriteTimeout
    )):
        return True

    return False