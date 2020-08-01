import regex


def swtor_lower(string: str) -> str:
    """Convert A-Z only into lowercase, matching SWTOR behavior."""
    return regex.sub("[A-Z]+", lambda m: m.group(0).lower(), string)


def swtor_upper(string: str) -> str:
    """Convert a-z only into uppercase, matching SWTOR behavior."""
    return regex.sub("[a-z]+", lambda m: m.group(0).upper(), string)
