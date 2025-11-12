import re


class Regex:
    def __init__(self, pattern, flags=0):
        self.pattern = re.compile(pattern, flags)

    def __eq__(self, other) -> bool:
        return bool(self.pattern.fullmatch(other))

    def __repr__(self):
        return f"<RegexMatcher {self.pattern.pattern!r}>"
