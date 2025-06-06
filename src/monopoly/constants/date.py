"""Store date-related regex patterns and constants."""

import logging

from strenum import StrEnum

from monopoly.enums import RegexEnum

logger = logging.getLogger(__name__)


# pylint: disable=line-too-long
class DateFormats(StrEnum):
    """Case-insensitive list of common ISO 8601 date formats."""

    D = r"(1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31)"
    DD = r"(01|02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31)"
    M = r"(1|2|3|4|5|6|7|8|9|10|11|12)"
    MM = r"(01|02|03|04|05|06|07|08|09|10|11|12)"
    MMM = r"(?i:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
    MMMM = r"(?i:January|February|March|April|May|June|July|August|September|October|November|December)"
    YY = r"([2-5][0-9]\b)"
    YYYY = r"(20\d{2}\b)"


class ISO8601(RegexEnum):
    DD_MM = rf"\b({DateFormats.DD}[\/\-\s.]{DateFormats.MM})"
    DD_MM_YY = rf"\b({DateFormats.DD}[\/\-\s.]{DateFormats.MM}[\/\-\s.]{DateFormats.YY})"
    DD_MM_YYYY = rf"\b({DateFormats.DD}[\/\-\s.]{DateFormats.MM}[\/\-\s.]{DateFormats.YYYY})"
    DD_MMM = rf"\b({DateFormats.DD}[\/\-\s.]{DateFormats.MMM})"
    DD_MMM_RELAXED = DD_MMM.replace(r"[\/\-\s.]", r"(?:[\/\-\s.]|)")
    DD_MMM_YY = rf"\b({DateFormats.DD}[\/\-\s.]{DateFormats.MMM}[\/\-\s.]{DateFormats.YY})"
    DD_MMM_YYYY = rf"\b({DateFormats.DD}[\/\-\s.]{DateFormats.MMM}[,\s]{{1,2}}{DateFormats.YYYY})"
    MM_DD = rf"\b({DateFormats.MM}[\/\-\s.]{DateFormats.DD})"
    MM_DD_YY = rf"\b({DateFormats.MM}[\/\-\s.]{DateFormats.DD}[\/\-\s.]{DateFormats.YY})"
    MMMM_DD_YYYY = rf"\b({DateFormats.MMMM}\s{DateFormats.DD}[,\s]{{1,2}}{DateFormats.YYYY})"
    MMM_DD = rf"\b({DateFormats.MMM}[\/\-\s.]{DateFormats.DD})"
    MMM_DD_YYYY = rf"\b({DateFormats.MMM}[\/\-\s.]{DateFormats.DD}[,\s]{{1,2}}{DateFormats.YYYY})"
