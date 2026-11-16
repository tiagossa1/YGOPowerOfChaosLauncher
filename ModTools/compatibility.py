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


# No confirmed executable profiles for these editions yet.
INTENDED_EDITIONS = ('Yugi the Destiny', 'Kaiba the Revenge', 'Joey the Passion')

# Research references, not locally verified executable profiles. Source labels
# are preserved without granting capabilities or making safety claims.
MODTOOLS_SOURCE = (
    'https://github.com/derplayer/YuGiOh-PoC-ModTools/blob/master/'
    'YuGiOh_PoC_Patcher/YuGi/YuGiExtendedMethods.cs'
)
UNVERIFIED_SAMPLES = {
    'Joey_Pc.exe': {
        'edition': 'Joey the Passion',
        'md5': '6bb361cd96a6a1964a35c00625bad82b',
        'sha1': None,
        'sha256': None,
        'sources': ('AppQuantify (contributor attribution, not independently checked)',
                    'https://www.processchecker.com/file/joey_pc.exe.html',
                    'https://threatinfo.net/files/Joey_Pc.exe-6bb361cd96a6a1964a35c00625bad82b'),
        'variant': 'unknown',
        'note': 'Reported as a game executable by AppQuantify. ProcessChecker lists '
                'the MD5 and ThreatInfo flags the sample as Trojan.Packed. '
                'Authenticity and safety are unconfirmed.',
    },
    'Kaiba_Pc.exe': {
        'edition': 'Kaiba the Revenge',
        'md5': 'b4160ad7b97d3c28cfb484ad53e7f4e1',
        'sha1': '67367f7fca2218fda4959837ab0f2696e091b77a',
        'sha256': 'a829b16eee11356159850029f5a809886b47c33498ce1d849dd1591a603c0309',
        'sources': (
            'https://gridinsoft.com/online-virus-scanner/id/a829b16eee11356159850029f5a809886b47c33498ce1d849dd1591a603c0309',
            'https://www.freefixer.com/library/file/kaiba_pc.exe-107096/',
        ),
        'size_bytes': 1789952,
        'variant': 'unknown; observed in a crack folder',
        'note': 'Hashes corroborated by GridinSoft and FreeFixer. FreeFixer '
                'places it in a crack folder. Original/NoCD classification, '
                'authenticity and runtime compatibility remain unconfirmed.',
    },
    'Yugi_PC.exe': {
        'edition': 'Yugi the Destiny',
        'variant': 'unknown',
        'size_bytes': 1740800,
        'md5': '7caa787dde5e05e005e73634f956fd8b',
        'sha1': 'eb7e7b0d023884b3cc1daa63fef737524ac30d60',
        'sha256': 'e8724a30f8814d2297a7a2a79fc1b422181dd313bc4481b1def16f504d92d5b6',
        'sources': (
            'https://gridinsoft.com/online-virus-scanner/id/e8724a30f8814d2297a7a2a79fc1b422181dd313bc4481b1def16f504d92d5b6',
            'https://processchecker.com/file/yugi_pc.exe.html',
        ),
        'note': 'Published file hashes; neither source establishes original/NoCD '
                'status. Scanner results do not establish authenticity or safety.',
    },
    'Joey US v1.0 normal': {
        'edition': 'Joey the Passion',
        'variant': 'US v1.0 normal (source label POC_JTP_US_HASH)',
        'md5': None,
        'sha1': 'e438a082105f1045b92922504a93a8ad26846dc2',
        'sha256': None,
        'sources': (MODTOOLS_SOURCE,),
        'note': 'Normal-release classification from third-party source code, '
                'not verified against original media here. SHA-256 not found.',
    },
    'Joey EUR v1.1 normal': {
        'edition': 'Joey the Passion',
        'variant': 'EUR v1.1 normal (source label POC_JTP_EUR_HASH)',
        'md5': None,
        'sha1': '3b12fdeb63b6359561fbbde21f9d7ed922245152',
        'sha256': None,
        'sources': (MODTOOLS_SOURCE,),
        'note': 'Normal-release classification from third-party source code, '
                'not verified against original media here. SHA-256 not found.',
    },
    'Joey US v1.0 SRLESS': {
        'edition': 'Joey the Passion',
        'variant': 'US v1.0 SRLESS (source label POC_JTP_US_SRLESS_HASH)',
        'size_bytes': 3919872,
        'md5': '75461d4ac813ecd1aa8aeca1ac526629',
        'sha1': '4f24efdd237408ea27384a00c627a4d85e8439b1',
        'sha256': 'c5749eb934a1cf68d9236e44ff81e98b8aaee486b4f8ebd417440505d44ac1ea',
        'sources': (
            MODTOOLS_SOURCE,
            'https://gridinsoft.com/online-virus-scanner/id/c5749eb934a1cf68d9236e44ff81e98b8aaee486b4f8ebd417440505d44ac1ea',
        ),
        'note': 'SRLESS denotes the SecuROM-less variant in the external catalog. '
                'GridinSoft report dated 2026-05-13 shows 8/66 detections, '
                'including Sality and packed-file labels. Do not treat as safe '
                'or compatible on the strength of the hash reference.',
    },
    'Joey EUR v1.1 SRLESS': {
        'edition': 'Joey the Passion',
        'variant': 'EUR v1.1 SRLESS (source label POC_JTP_EUR_SRLESS_HASH)',
        'size_bytes': 2060288,
        'md5': 'a3416b07c3bf72d9401fc95a15f64d79',
        'sha1': 'edc4b7249423af32abb08b6a4f97d5549a7bd937',
        'sha256': '08018ebbc73f3fa51fdf220e903f69cd9a22572e508ea9cd145853abf8ed2dda',
        'sources': (
            MODTOOLS_SOURCE,
            'https://gridinsoft.com/online-virus-scanner/id/08018ebbc73f3fa51fdf220e903f69cd9a22572e508ea9cd145853abf8ed2dda',
        ),
        'note': 'SRLESS denotes the SecuROM-less variant in the external catalog. '
                'SHA-1 cross-matches the GridinSoft sample. No local runtime '
                'verification or guarantee of authenticity or safety.',
    },
}

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
