"""
tests/test_fact_checking.py
------------------------------
Tests for the shared claim-verification helper used by the GitHub
Project Importer and the Profile Update Drafter.
"""

from agents.fact_checking import verify_claims_against_text


def test_verifies_exact_phrase():
    verified, unverified = verify_claims_against_text(["Python"], "Built with Python and Flask.")
    assert verified == ["Python"]
    assert unverified == []


def test_flags_fabricated_term():
    verified, unverified = verify_claims_against_text(
        ["Kubernetes"], "Built with Python and Flask."
    )
    assert unverified == ["Kubernetes"]


def test_verifies_true_metric_even_with_different_descriptor_word():
    verified, unverified = verify_claims_against_text(
        ["10000 downloads"], "The package has been installed 10000 times."
    )
    assert verified == ["10000 downloads"]


def test_flags_fabricated_metric():
    verified, unverified = verify_claims_against_text(
        ["50000 users"], "The package has been installed 10000 times."
    )
    assert unverified == ["50000 users"]


def test_ignores_empty_and_whitespace_claims():
    verified, unverified = verify_claims_against_text(["", "   ", "Python"], "Written in Python.")
    assert verified == ["Python"]
    assert unverified == []


def test_majority_word_match_verifies_non_numeric_claim():
    verified, unverified = verify_claims_against_text(
        ["real-time chat feature"], "Implements a real time chat system for users."
    )
    assert verified == ["real-time chat feature"]
