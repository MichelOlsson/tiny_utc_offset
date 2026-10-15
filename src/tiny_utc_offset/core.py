from __future__ import annotations

import datetime
import re

__all__ = ["parse_utc_offset", "ParseError"]


class ParseError(ValueError):
    """Raised when an input string cannot be interpreted as a UTC offset."""


# Accept forms like:
#   Z                -> UTC (zero offset)
#   UTC, GMT         -> zero offset, bare or with a trailing sign
#   +0530            -> sign + 1-4 digits (hhmm or hhmm)
#   +05:30           -> sign + hh:mm
#   +05              -> sign + 1-2 digit hours
#   +0530, -0530     -> sign + hhmm
# A 'Z' may also follow any of the above (common in ISO 8601) and is
# accepted but ignored — the offset is what matters.
_PATTERN = re.compile(
    r"""
    ^
    \s*
    (?:
        (?P<prefix>UTC|GMT|Z)
        (?P<rest>[+-]\d{1,2}(?::?\d{2})?)?   # optional sign+hhmm after UTC/GMT
    |
        (?P<sign>[+-])
        (?P<hh>\d{1,2})
        (?::?(?P<mm>\d{2}))?
    )
    \s*
    Z?                                      # trailing 'Z' marker, ignored
    $
    """,
    re.VERBOSE | re.IGNORECASE,
)


def parse_utc_offset(text: str) -> datetime.timezone:
    """Parse a human-written UTC offset string into a ``datetime.timezone``.

    Supported forms (case-insensitive, surrounding whitespace allowed):

    * ``Z`` / ``UTC`` / ``GMT`` — zero offset
    * ``UTC+02:00`` / ``GMT-5`` — prefixed forms with a trailing offset
    * ``+0530`` / ``-0530`` — sign + hhmm
    * ``+05:30`` / ``-05:30`` — sign + hh:mm
    * ``+05`` / ``-5`` — sign + 1-2 digit hours
    * ``+0530Z`` — trailing ``Z`` marker is accepted and ignored

    Minutes must be in range 0-59. Hours are capped at 23 by the timezone
    constructor's own range checks, which mirrors what real-world offsets
    are: the largest currently in use is UTC+14.

    Raises:
        ParseError: If the string does not match a recognised form or
            contains an out-of-range minute value.
    """
    if not isinstance(text, str):
        raise ParseError(f"expected str, got {type(text).__name__}")

    m = _PATTERN.match(text)
    if m is None:
        raise ParseError(f"unrecognised UTC offset: {text!r}")

    # --- Zero-offset keywords -------------------------------------------
    prefix = m.group("prefix")
    if prefix and prefix.upper() not in ("UTC", "GMT"):
        # 'Z' alone means UTC.
        return datetime.timezone.utc

    rest = m.group("rest")
    if prefix and rest is None:
        # Bare 'UTC' / 'GMT' with no trailing offset → zero.
        return datetime.timezone.utc

    # --- Sign + hh[:mm] -------------------------------------------------
    if rest is not None:
        sign_str = rest[0]
        digits = rest[1:]
    else:
        sign_str = m.group("sign")
        # By construction of the pattern, if we're here we have sign + hh.
        hh = m.group("hh")
        mm = m.group("mm")
        if mm is not None:
            digits = f"{hh}:{mm}"
        else:
            digits = hh

    sign = -1 if sign_str == "-" else 1

    # Split digits into hours and optional minutes.
    if ":" in digits:
        hh_str, mm_str = digits.split(":", 1)
    else:
        # Digits without colon: either hh or hhmm.
        if len(digits) <= 2:
            hh_str, mm_str = digits, "0"
        else:
            # hhmm: last two chars are minutes.
            hh_str, mm_str = digits[:-2], digits[-2:]

    hours = int(hh_str)
    minutes = int(mm_str)

    if minutes > 59:
        raise ParseError(f"minute value out of range in {text!r}")

    delta = datetime.timedelta(hours=hours, minutes=minutes) * sign
    return datetime.timezone(delta, name=text.strip())
