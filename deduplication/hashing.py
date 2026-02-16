import hashlib
from typing import Literal


def generate_hash(data: bytes, algorithm: Literal["sha256", "sha1"] = "sha256") -> str:
    """Generate a hash of input data using the specified algorithm.
    
    Supports SHA256 (default, cryptographically secure) and SHA1 (legacy).
    Used to deduplicate files by content rather than metadata.
    
    Args:
        data: Bytes to hash.
        algorithm: Hash algorithm; one of "sha256" or "sha1". Defaults to "sha256".
    
    Returns:
        Hexadecimal string representation of the hash.
    
    Example:
        >>> h = generate_hash(b"hello world")
        >>> len(h)
        64
    """
    if algorithm == "sha1":
        h = hashlib.sha1()
    else:
        h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()
import hashlib
