import re
from dataclasses import dataclass
from enum import StrEnum
from string import Template


# flake8: noqa
# pylint: disable=line-too-long
class DateFormats(StrEnum):
    D = "(?:1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31)"
    DD = "(?:01|02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31)"
    M = "(?:1|2|3|4|5|6|7|8|9|10|11|12)"
    MM = "(?:01|02|03|04|05|06|07|08|09|10|11|12)"
    MMM = "(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
    MMMM = "(?:January|February|March|April|May|June|July|August|September|October|November|December)"


@dataclass
class DateRegexPatterns:
    """Holds date regex patterns used by the generic statement handler"""

    DD_MM = r"\b(${DD}[\/\-]${MM})"
    DD_MMM = r"\b(${DD}[-\s]${MMM})"
    DD_MMM_YYYY = r"\b(${DD}[-\s]${MMM}[,\s]{1,2}20\d{2})"
    DD_MM_YYYY = r"\b(${DD}[\/\-]${MM}[\/\-]20\d{2})"
    MMMM_DD_YYYY = r"\b(${MMMM}\s${DD}[,\s]{1,2}20\d{2})"
    MMM_DD = r"\b(${MMM}[-\s]${DD})"
    MMM_DD_YYYY = r"\b(${MMM}[-\s]${DD}[,\s]{1,2}20\d{2})"

    def __post_init__(self):
        """Accesses class variables and performs substitution on variables enclosed by ${ }"""
        fields = [attribute for attribute in dir(self) if not attribute.startswith("_")]
        for field in fields:
            pattern = getattr(self, field)
            replaced_pattern = self._replace_bracketed_variables(pattern)
            object.__setattr__(self, field, replaced_pattern)
            # compile patterns
            setattr(self, field, re.compile(replaced_pattern, re.IGNORECASE))

    def _replace_bracketed_variables(self, pattern: str) -> str:
        template = Template(pattern)
        replacements = {format.name: format.value for format in DateFormats}
        return template.substitute(replacements)

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value
