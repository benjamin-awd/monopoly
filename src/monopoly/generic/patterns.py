import re
from dataclasses import asdict, dataclass
from enum import StrEnum


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

    DD_MM: str = rf"\b({DateFormats.DD}[\/\-]{DateFormats.MM})"
    DD_MMM: str = rf"\b({DateFormats.DD}[-\s]{DateFormats.MMM})"
    DD_MMM_YYYY: str = (
        rf"\b({DateFormats.DD}[-\s]{DateFormats.MMM}[,\s]{{1,2}}20\d{{2}})"
    )
    DD_MM_YYYY: str = rf"\b({DateFormats.DD}[\/\-]{DateFormats.MM}[\/\-]20\d{{2}})"
    MMMM_DD_YYYY: str = (
        rf"\b({DateFormats.MMMM}\s{DateFormats.DD}[,\s]{{1,2}}20\d{{2}})"
    )
    MMM_DD: str = rf"\b({DateFormats.MMM}[-\s]{DateFormats.DD})"
    MMM_DD_YYYY: str = (
        rf"\b({DateFormats.MMM}[-\s]{DateFormats.DD}[,\s]{{1,2}}20\d{{2}})"
    )

    def as_pattern_dict(self):
        return {k: re.compile(v, re.IGNORECASE) for k, v in asdict(self).items()}
