"""This file stores date-related regex patterns and constants"""

import re
from dataclasses import asdict

from pydantic.dataclasses import dataclass
from strenum import StrEnum


# flake8: noqa
# pylint: disable=line-too-long
class DateFormats(StrEnum):
    """Holds a case-insensitive list of common ISO 8601 date formats"""

    D = r"(?i:1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31)"
    DD = r"(?i:01|02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31)"
    M = r"(?i:1|2|3|4|5|6|7|8|9|10|11|12)"
    MM = r"(?i:01|02|03|04|05|06|07|08|09|10|11|12)"
    MMM = r"(?i:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
    MMMM = r"(?i:January|February|March|April|May|June|July|August|September|October|November|December)"
    YY = r"(?i:[2-5][0-9]\b)"
    YYYY = r"(?i:20\d{2}\b)"


# pylint: disable=too-many-instance-attributes
@dataclass
class DateRegexPatterns:
    """Holds date regex patterns used by the generic statement handler"""

    dd_mm: str = rf"\b({DateFormats.DD}[\/\-\s]{DateFormats.MM})"
    dd_mm_yy: str = (
        rf"\b({DateFormats.DD}[\/\-\s]{DateFormats.MM}[\/\-\s]{DateFormats.YY})"
    )
    dd_mmm: str = rf"\b({DateFormats.DD}[-\s]{DateFormats.MMM})"
    dd_mmm_yy: str = rf"\b({DateFormats.DD}[-\s]{DateFormats.MMM}[-\s]{DateFormats.YY})"
    dd_mmm_yyyy: str = (
        rf"\b({DateFormats.DD}[-\s]{DateFormats.MMM}[,\s]{{1,2}}{DateFormats.YYYY})"
    )
    dd_mm_yyyy: str = (
        rf"\b({DateFormats.DD}[\/\-\s]{DateFormats.MM}[\/\-\s]{DateFormats.YYYY})"
    )
    mmmm_dd_yyyy: str = (
        rf"\b({DateFormats.MMMM}\s{DateFormats.DD}[,\s]{{1,2}}{DateFormats.YYYY})"
    )
    mmm_dd: str = rf"\b({DateFormats.MMM}[-\s]{DateFormats.DD})"
    mmm_dd_yyyy: str = (
        rf"\b({DateFormats.MMM}[-\s]{DateFormats.DD}[,\s]{{1,2}}{DateFormats.YYYY})"
    )

    def as_pattern_dict(self):
        return {k: re.compile(v, re.IGNORECASE) for k, v in asdict(self).items()}
