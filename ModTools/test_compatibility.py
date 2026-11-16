"""Compatibility identification must never infer support from unknown hashes."""

from dataclasses import FrozenInstanceError

import compatibility
import pytest

NORMAL = '2316127757ce832387e4278fafe4acfa5fe2beb363e77d0bfe74dc47b827edab'
FLAG_ONLY = '47ee5bd047cbadf4ff6c17e714bb0f51669d6b45a4b66242a49288ebbdde475a'


@pytest.mark.parametrize('digest', (
    '', '0' * 64, NORMAL.upper(), NORMAL[:-1], ' ' + NORMAL,
    '1e5d81b1e44edf09e91addab582ef963694aa285e4be5eb5ad8e0ce4ab04664c',
))
def test_unknown_or_nonexact_digest_has_no_profile(digest):
    assert compatibility.identify_digest(digest) is None


@pytest.mark.parametrize(('digest', 'variant', 'arguments', 'skip_intro'), (
    (NORMAL, 'normal', ('-win', '-nosound', '-speedy'), False),
    (FLAG_ONLY, 'patch flag-only', ('-win', '-nosound', '-speedy', '-skipintro'), True),
))
def test_known_digest_returns_only_its_confirmed_capabilities(
    digest, variant, arguments, skip_intro,
):
    profile = compatibility.identify_digest(digest)
    assert isinstance(profile, compatibility.CompatibilityProfile)
    assert profile.edition == 'Legend Reborn'
    assert profile.variant == variant
    assert profile.arguments == arguments
    assert profile.skip_intro is skip_intro


def test_identified_profile_cannot_be_mutated():
    profile = compatibility.identify_digest(NORMAL)
    with pytest.raises(FrozenInstanceError):
        profile.skip_intro = True


def test_catalog_contains_only_observed_digests():
    assert set(compatibility.KNOWN_PROFILES) == {NORMAL, FLAG_ONLY}


def test_reported_samples_preserve_hashes_without_granting_capabilities():
    joey = compatibility.UNVERIFIED_SAMPLES['Joey_Pc.exe']
    assert joey['md5'] == '6bb361cd96a6a1964a35c00625bad82b'
    assert joey['sha256'] is None
    assert 'Trojan.Packed' in joey['note']
    kaiba = compatibility.UNVERIFIED_SAMPLES['Kaiba_Pc.exe']
    assert kaiba['md5'] == 'b4160ad7b97d3c28cfb484ad53e7f4e1'
    assert kaiba['sha1'] == '67367f7fca2218fda4959837ab0f2696e091b77a'
    assert kaiba['sha256'] == 'a829b16eee11356159850029f5a809886b47c33498ce1d849dd1591a603c0309'
    assert 'crack' in kaiba['note']
    assert compatibility.identify_digest(kaiba['sha256']) is None


def test_intended_editions_are_metadata_not_supported_profiles():
    assert compatibility.INTENDED_EDITIONS == (
        'Yugi the Destiny', 'Kaiba the Revenge', 'Joey the Passion',
    )
    assert not any(
        profile.edition in compatibility.INTENDED_EDITIONS
        for profile in compatibility.KNOWN_PROFILES.values()
    )


@pytest.mark.parametrize(('sample', 'sha1', 'sha256'), (
    ('Yugi_PC.exe', 'eb7e7b0d023884b3cc1daa63fef737524ac30d60',
     'e8724a30f8814d2297a7a2a79fc1b422181dd313bc4481b1def16f504d92d5b6'),
    ('Joey US v1.0 normal', 'e438a082105f1045b92922504a93a8ad26846dc2', None),
    ('Joey EUR v1.1 normal', '3b12fdeb63b6359561fbbde21f9d7ed922245152', None),
    ('Joey US v1.0 SRLESS', '4f24efdd237408ea27384a00c627a4d85e8439b1',
     'c5749eb934a1cf68d9236e44ff81e98b8aaee486b4f8ebd417440505d44ac1ea'),
    ('Joey EUR v1.1 SRLESS', 'edc4b7249423af32abb08b6a4f97d5549a7bd937',
     '08018ebbc73f3fa51fdf220e903f69cd9a22572e508ea9cd145853abf8ed2dda'),
))
def test_researched_references_are_not_confirmed_profiles(sample, sha1, sha256):
    reference = compatibility.UNVERIFIED_SAMPLES[sample]
    assert reference['sha1'] == sha1
    assert reference['sha256'] == sha256
    assert reference['sources']
    if sha256 is not None:
        assert compatibility.identify_digest(sha256) is None


def test_srless_us_reference_preserves_scanner_warning():
    assert '8/66' in compatibility.UNVERIFIED_SAMPLES['Joey US v1.0 SRLESS']['note']
