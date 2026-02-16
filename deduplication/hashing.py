import hashlib
from typing import Literal


def generate_hash(data: bytes, algorithm: Literal["sha256", "sha1"] = "sha256") -> str:
    if algorithm == "sha1":
        h = hashlib.sha1()
    else:
        h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()
import hashlib
