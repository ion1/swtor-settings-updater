import codecs
import regex

CP1252_PRINTABLE = regex.sub(
    r"\p{C}+",
    "",
    codecs.decode(bytes(range(0, 0x100)), encoding="CP1252", errors="ignore"),
)


def regex_character_class(characters, exclusions=""):
    ranges = []
    current_range = None

    characters_excluded = sorted(set(characters) - set(exclusions))

    if not characters_excluded:
        raise ValueError(
            f"Empty character class: {repr(characters)} - {repr(exclusions)}"
        )

    for c in characters_excluded:
        if current_range is not None:
            first, last = current_range

            if ord(c) == ord(last) + 1:
                current_range = (first, c)
            else:
                ranges.append(current_range)
                current_range = (c, c)
        else:
            current_range = (c, c)

    if current_range is not None:
        ranges.append(current_range)

    regex_class = ""
    for first, last in ranges:
        if first == last:
            regex_class += regex.escape(first)
        else:
            regex_class += f"{regex.escape(first)}-{regex.escape(last)}"

    return regex_class


def swtor_lower(string):
    """Convert A-Z only into lowercase, matching SWTOR behavior."""
    return regex.sub("[A-Z]+", lambda m: m.group(0).lower(), string)


def swtor_upper(string):
    """Convert a-z only into uppercase, matching SWTOR behavior."""
    return regex.sub("[a-z]+", lambda m: m.group(0).upper(), string)
