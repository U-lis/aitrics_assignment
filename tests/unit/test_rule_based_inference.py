from app.domain.inference import RuleBasedInference
from app.domain.risk_level import RiskLevel


class TestRuleBasedInference:
    def setup_method(self):
        self.inference = RuleBasedInference()

    def test_no_rules_matched(self):
        """0 matched rules -> LOW (0.2)."""
        vitals = {"HR": 80, "SBP": 120, "SpO2": 98}
        result = self.inference.evaluate(vitals)

        assert result.risk_score == 0.2
        assert result.risk_level == RiskLevel.LOW
        assert result.checked_rules == []

    def test_one_rule_hr(self):
        """HR > 120 -> MEDIUM."""
        vitals = {"HR": 130, "SBP": 120, "SpO2": 98}
        result = self.inference.evaluate(vitals)

        assert result.risk_score == 0.5
        assert result.risk_level == RiskLevel.MEDIUM
        assert result.checked_rules == ["HR > 120"]

    def test_one_rule_sbp(self):
        """SBP < 90 -> MEDIUM."""
        vitals = {"HR": 80, "SBP": 85, "SpO2": 98}
        result = self.inference.evaluate(vitals)

        assert result.risk_score == 0.5
        assert result.risk_level == RiskLevel.MEDIUM
        assert result.checked_rules == ["SBP < 90"]

    def test_one_rule_spo2(self):
        """SpO2 < 90 -> MEDIUM."""
        vitals = {"HR": 80, "SBP": 120, "SpO2": 85}
        result = self.inference.evaluate(vitals)

        assert result.risk_score == 0.5
        assert result.risk_level == RiskLevel.MEDIUM
        assert result.checked_rules == ["SpO2 < 90"]

    def test_two_rules_matched(self):
        """2 matched rules -> MEDIUM (0.7)."""
        vitals = {"HR": 130, "SBP": 85, "SpO2": 98}
        result = self.inference.evaluate(vitals)

        assert result.risk_score == 0.7
        assert result.risk_level == RiskLevel.MEDIUM
        assert "HR > 120" in result.checked_rules
        assert "SBP < 90" in result.checked_rules
        assert len(result.checked_rules) == 2

    def test_three_rules_matched(self):
        """3 matched rules -> HIGH (0.9)."""
        vitals = {"HR": 130, "SBP": 85, "SpO2": 85}
        result = self.inference.evaluate(vitals)

        assert result.risk_score == 0.9
        assert result.risk_level == RiskLevel.HIGH
        assert len(result.checked_rules) == 3

    def test_missing_hr_default(self):
        """No HR -> treated as 0 (no match for HR > 120)."""
        vitals = {"SBP": 120, "SpO2": 98}
        result = self.inference.evaluate(vitals)

        assert "HR > 120" not in result.checked_rules

    def test_missing_sbp_default(self):
        """No SBP -> treated as inf (no match for SBP < 90)."""
        vitals = {"HR": 80, "SpO2": 98}
        result = self.inference.evaluate(vitals)

        assert "SBP < 90" not in result.checked_rules

    def test_missing_spo2_default(self):
        """No SpO2 -> treated as 100 (no match for SpO2 < 90)."""
        vitals = {"HR": 80, "SBP": 120}
        result = self.inference.evaluate(vitals)

        assert "SpO2 < 90" not in result.checked_rules
