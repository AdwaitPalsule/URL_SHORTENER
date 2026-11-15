from rate_limiter import r



def get_cached_url(code: str):
    key = f"url:{code}"
    return r.get(key)

def cache_url(code: str, original_url: str):
    key = f"url:{code}"
    r.set(key, original_url, ex=300)