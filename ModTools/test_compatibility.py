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


def test_intended_editions_are_metadata_not_supported_profiles():
    assert compatibility.INTENDED_EDITIONS == (
        'Yugi the Destiny', 'Kaiba the Revenge', 'Joey the Passion',
    )
    assert not any(
        profile.edition in compatibility.INTENDED_EDITIONS
        for profile in compatibility.KNOWN_PROFILES.values()
    )
