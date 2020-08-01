import codecs
import regex

CP1252_PRINTABLE = regex.sub(
    r"\p{C}+",
    "",
    codecs.decode(bytes(range(0, 0x100)), encoding="CP1252", errors="ignore"),
)


def regex_character_class(characters: str, exclusions: str = "") -> str:
    ranges = []
    current_range = None

    exclusions_not_in_characters = set(exclusions) - set(characters)
    if exclusions_not_in_characters:
        raise ValueError(
            f"Tried to exclude {''.join(exclusions_not_in_characters)!r} from {''.join(characters)!r}"
        )

    characters_excluded = sorted(set(characters) - set(exclusions))

    if not characters_excluded:
        raise ValueError(
            f"Empty character class: {''.join(characters)!r} - {''.join(exclusions)!r}"
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
