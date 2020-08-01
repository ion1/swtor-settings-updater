class OptionTransformer:
    """Prevent ConfigParser from lower-casing key names."""

    def __init__(self):
        self.canonical_forms = {}

    def xform(self, name):
        name_lower = name.lower()

        if name_lower in self.canonical_forms:
            return self.canonical_forms[name_lower]

        elif name == name_lower:
            # A lower-case name, possibly mangled by ConfigParser previously. Do not
            # add it to the dict.
            return name

        else:
            # Add the name to the dict as the canonical form.
            self.canonical_forms[name_lower] = name
            return name
