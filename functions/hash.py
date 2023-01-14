import hashlib
import random


def generate_random_hash() -> str:
    """生成随机的8位hash"""
    return hashlib.md5(str(random.random()).encode()).hexdigest()[:8]
