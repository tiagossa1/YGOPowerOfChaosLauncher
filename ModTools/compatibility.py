"""Exact SHA-256 compatibility catalog; unknown executables gain no capabilities.

Legend Reborn's normal flags have been confirmed. The flag-only patch was tested
locally with and without ``-skipintro``: it reaches the menu or shows the logos.
Arguments describe supported flags, not flags that must always be passed.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CompatibilityProfile:
    edition: str
    variant: str
    arguments: tuple[str, ...]
    skip_intro: bool


# Metadata only: no hashes or supported arguments established for these editions.
INTENDED_EDITIONS = ('Yugi the Destiny', 'Kaiba the Revenge', 'Joey the Passion')

KNOWN_PROFILES = {
    '2316127757ce832387e4278fafe4acfa5fe2beb363e77d0bfe74dc47b827edab': (
        CompatibilityProfile(
            edition='Legend Reborn',
            variant='normal',
            arguments=('-win', '-nosound', '-speedy'),
            skip_intro=False,
        )
    ),
    '47ee5bd047cbadf4ff6c17e714bb0f51669d6b45a4b66242a49288ebbdde475a': (
        CompatibilityProfile(
            edition='Legend Reborn',
            variant='patch flag-only',
            arguments=('-win', '-nosound', '-speedy', '-skipintro'),
            skip_intro=True,
        )
    ),
}


def identify_digest(digest: str) -> CompatibilityProfile | None:
    """Return a profile for an exact lowercase SHA-256 hexdigest, else None."""
    return KNOWN_PROFILES.get(digest)
