"""
test_app.py
===========
Comprehensive unittest suite for the Election Education Tool.

Covers:
  - Voter eligibility core logic (age + citizenship).
  - Age boundary cases (17, 18, 19).
  - Non-citizen edge cases.
  - Empty / invalid input handling.
  - MINIMUM_VOTING_AGE constant integrity.

Run with:
    python -m pytest test_app.py -v
  or:
    python -m unittest discover -v
"""

import unittest
from election_guide import check_voter_eligibility, MINIMUM_VOTING_AGE


# ─────────────────────────────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────────────────────────────

def _check(age, is_citizen):
    """Thin wrapper so tests read naturally."""
    return check_voter_eligibility(age, is_citizen)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Constant integrity
# ─────────────────────────────────────────────────────────────────────────────

class TestMinimumVotingAgeConstant(unittest.TestCase):
    """Verify that the MINIMUM_VOTING_AGE constant is set to 18."""

    def test_minimum_voting_age_is_18(self):
        """MINIMUM_VOTING_AGE must equal 18 — the legal standard."""
        self.assertEqual(MINIMUM_VOTING_AGE, 18)

    def test_minimum_voting_age_is_integer(self):
        """MINIMUM_VOTING_AGE must be an integer, not a float or string."""
        self.assertIsInstance(MINIMUM_VOTING_AGE, int)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Age boundary cases (17, 18, 19) — citizen path
# ─────────────────────────────────────────────────────────────────────────────

class TestAgeBoundaryCases(unittest.TestCase):
    """
    Test the critical age boundary around the minimum voting age.

    Age 17  → ineligible (one year below threshold).
    Age 18  → eligible   (exactly at threshold).
    Age 19  → eligible   (one year above threshold).
    """

    def test_age_17_citizen_ineligible(self):
        """A 17-year-old citizen must NOT be eligible."""
        eligible, reason = _check(17, True)
        self.assertFalse(eligible)
        self.assertIn("17", reason)

    def test_age_18_citizen_eligible(self):
        """An 18-year-old citizen MUST be eligible — the exact boundary."""
        eligible, reason = _check(18, True)
        self.assertTrue(eligible)
        self.assertIn("18", reason)

    def test_age_19_citizen_eligible(self):
        """A 19-year-old citizen must be eligible — one step above boundary."""
        eligible, reason = _check(19, True)
        self.assertTrue(eligible)

    def test_age_17_non_citizen_ineligible(self):
        """A 17-year-old non-citizen must fail on both age and citizenship."""
        eligible, reason = _check(17, False)
        self.assertFalse(eligible)
        # Reason should mention BOTH issues
        self.assertIn("17", reason)
        self.assertIn("citizen", reason.lower())

    def test_age_18_non_citizen_ineligible(self):
        """An 18-year-old non-citizen should fail solely on citizenship."""
        eligible, reason = _check(18, False)
        self.assertFalse(eligible)
        self.assertIn("citizen", reason.lower())

    def test_age_19_non_citizen_ineligible(self):
        """A 19-year-old non-citizen should fail solely on citizenship."""
        eligible, reason = _check(19, False)
        self.assertFalse(eligible)
        self.assertIn("citizen", reason.lower())


# ─────────────────────────────────────────────────────────────────────────────
# 3. Core eligibility logic — wide range of valid ages
# ─────────────────────────────────────────────────────────────────────────────

class TestCoreEligibilityLogic(unittest.TestCase):
    """Verify eligibility outcomes across a broad age range."""

    def test_eligible_citizen_adult(self):
        """Typical eligible voter: age 30, citizen."""
        eligible, _ = _check(30, True)
        self.assertTrue(eligible)

    def test_eligible_citizen_elderly(self):
        """Elderly eligible voter: age 80, citizen."""
        eligible, _ = _check(80, True)
        self.assertTrue(eligible)

    def test_ineligible_too_young_citizen(self):
        """Very young person (age 5) must not be eligible even as citizen."""
        eligible, _ = _check(5, True)
        self.assertFalse(eligible)

    def test_ineligible_non_citizen_adult(self):
        """Adult non-citizen (age 40) must not be eligible."""
        eligible, _ = _check(40, False)
        self.assertFalse(eligible)

    def test_ineligible_non_citizen_young(self):
        """Young non-citizen (age 16) must not be eligible."""
        eligible, _ = _check(16, False)
        self.assertFalse(eligible)

    def test_return_type_is_tuple(self):
        """check_voter_eligibility must always return a 2-tuple."""
        result = _check(25, True)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_first_element_is_bool(self):
        """First element of the returned tuple must be a bool."""
        eligible, _ = _check(25, True)
        self.assertIsInstance(eligible, bool)

    def test_second_element_is_str(self):
        """Second element of the returned tuple must be a non-empty string."""
        _, reason = _check(25, True)
        self.assertIsInstance(reason, str)
        self.assertGreater(len(reason), 0)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Empty / zero / edge-value input handling
# ─────────────────────────────────────────────────────────────────────────────

class TestEdgeAndEmptyInputHandling(unittest.TestCase):
    """
    Test behaviour when age is 0, negative, or unrealistically large.

    The function receives an int — callers are responsible for sanitisation;
    these tests confirm the function does not crash and returns sensible output.
    """

    def test_age_zero_ineligible(self):
        """Age 0 must be ineligible (below minimum)."""
        eligible, reason = _check(0, True)
        self.assertFalse(eligible)
        self.assertIsInstance(reason, str)

    def test_age_negative_ineligible(self):
        """Negative age must be ineligible — does not raise an exception."""
        eligible, reason = _check(-5, True)
        self.assertFalse(eligible)
        self.assertIsInstance(reason, str)

    def test_age_very_large_citizen_eligible(self):
        """Unusually large age (150) with citizenship must be eligible."""
        eligible, _ = _check(150, True)
        self.assertTrue(eligible)

    def test_age_exactly_minimum_minus_one(self):
        """MINIMUM_VOTING_AGE - 1 must always be ineligible."""
        eligible, _ = _check(MINIMUM_VOTING_AGE - 1, True)
        self.assertFalse(eligible)

    def test_age_exactly_minimum(self):
        """MINIMUM_VOTING_AGE itself must always be eligible (citizen)."""
        eligible, _ = _check(MINIMUM_VOTING_AGE, True)
        self.assertTrue(eligible)

    def test_age_exactly_minimum_plus_one(self):
        """MINIMUM_VOTING_AGE + 1 must always be eligible (citizen)."""
        eligible, _ = _check(MINIMUM_VOTING_AGE + 1, True)
        self.assertTrue(eligible)

    def test_citizen_true_vs_false_difference(self):
        """
        For the same age above minimum, citizenship status must change
        the eligibility outcome from True to False.
        """
        eligible_citizen, _ = _check(30, True)
        eligible_non_citizen, _ = _check(30, False)
        self.assertTrue(eligible_citizen)
        self.assertFalse(eligible_non_citizen)

    def test_reason_contains_age_when_underage(self):
        """When underage, the reason string must reference the user's age."""
        _, reason = _check(15, True)
        self.assertIn("15", reason)

    def test_reason_mentions_citizen_when_not_citizen(self):
        """When not a citizen, reason must mention citizenship requirement."""
        _, reason = _check(25, False)
        self.assertIn("citizen", reason.lower())

    def test_both_disqualifiers_mentioned_in_reason(self):
        """When both age and citizenship fail, reason must cover both issues."""
        _, reason = _check(10, False)
        self.assertIn("citizen", reason.lower())
        # age (10) should also appear in reason
        self.assertIn("10", reason)


# ─────────────────────────────────────────────────────────────────────────────
# 5. Regression — boundary is not off by one
# ─────────────────────────────────────────────────────────────────────────────

class TestBoundaryRegression(unittest.TestCase):
    """Guard against off-by-one regressions in the eligibility threshold."""

    def test_no_off_by_one_below(self):
        """One day before 18 (conceptually age 17) must remain ineligible."""
        self.assertFalse(_check(MINIMUM_VOTING_AGE - 1, True)[0])

    def test_no_off_by_one_at(self):
        """Exactly at 18 must be eligible."""
        self.assertTrue(_check(MINIMUM_VOTING_AGE, True)[0])

    def test_no_off_by_one_above(self):
        """One year above 18 (19) must be eligible."""
        self.assertTrue(_check(MINIMUM_VOTING_AGE + 1, True)[0])


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)
