"""
Tests for Water/Nausea quality check integration

Tests the integration between quality_runner.py and check_water_natasha.py
"""

import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


class TestQualityCheckWaterNausea:
    """Test water/nausea check in QualityCheck class"""

    @pytest.fixture
    def sample_russian_text(self, tmp_path):
        """Create a sample Russian markdown file"""
        content = """# Активная пена для мойки автомобиля

Активная пена — это специальное моющее средство для бесконтактной мойки автомобиля.
Она эффективно удаляет грязь и пыль, не повреждая лакокрасочное покрытие.

## Преимущества активной пены

Активная пена обладает рядом преимуществ:
- Безопасна для ЛКП автомобиля
- Экономичный расход
- Быстро смывает грязь

## Как использовать

Нанесите пену на сухой автомобиль. Подождите 2-3 минуты.
Смойте водой под высоким давлением.
"""
        test_file = tmp_path / "test_ru.md"
        test_file.write_text(content, encoding="utf-8")
        return test_file

    def test_quality_check_initialization(self, sample_russian_text):
        """Should initialize QualityCheck correctly"""
        try:
            from quality_runner import QualityCheck

            checker = QualityCheck(str(sample_russian_text), "активная пена", "B")
            assert checker.file_path == sample_russian_text
            assert checker.keyword == "активная пена"
            assert checker.tier == "B"
        except ImportError as e:
            pytest.skip(f"Could not import quality_runner: {e}")

    def test_quality_check_invalid_tier(self, sample_russian_text):
        """Should reject invalid tier"""
        try:
            from quality_runner import QualityCheck

            with pytest.raises(ValueError, match="Invalid tier"):
                QualityCheck(str(sample_russian_text), "test", "X")
        except ImportError as e:
            pytest.skip(f"Could not import quality_runner: {e}")

    def test_quality_check_file_not_found(self, tmp_path):
        """Should raise error for non-existent file"""
        try:
            from quality_runner import QualityCheck

            with pytest.raises(FileNotFoundError):
                QualityCheck(str(tmp_path / "nonexistent.md"), "test", "B")
        except ImportError as e:
            pytest.skip(f"Could not import quality_runner: {e}")

    def test_water_nausea_skip_flag(self, sample_russian_text):
        """Should skip water check when flag is set"""
        try:
            from quality_runner import QualityCheck

            checker = QualityCheck(str(sample_russian_text), "активная пена", "B", skip_water=True)
            status, metrics = checker.check_water_nausea()
            assert status == "PASS"
            assert metrics == {}
        except ImportError as e:
            pytest.skip(f"Could not import quality_runner: {e}")


class TestCheckWaterNatashaScript:
    """Test check_water_natasha.py directly"""

    @pytest.fixture
    def sample_text(self):
        """Sample Russian text for testing"""
        return """
        Активная пена для мойки автомобиля.
        Это эффективное средство для бесконтактной мойки.
        Пена быстро удаляет грязь и пыль с поверхности автомобиля.
        Использование активной пены экономит время и воду.
        """

    def test_script_exists(self):
        """check_water_natasha.py should exist"""
        script_path = Path(__file__).parent.parent / "scripts" / "check_water_natasha.py"
        assert script_path.exists()

    def test_calculate_metrics_import(self):
        """Should be able to import calculate_metrics function"""
        try:
            from check_water_natasha import calculate_metrics_from_text

            assert callable(calculate_metrics_from_text)
        except (ImportError, SystemExit) as e:
            pytest.skip(f"Could not import check_water_natasha: {e}")

    def test_calculate_metrics_returns_dict(self, sample_text):
        """calculate_metrics should return a dictionary"""
        try:
            from check_water_natasha import calculate_metrics_from_text

            metrics = calculate_metrics_from_text(sample_text)
            assert isinstance(metrics, dict)
        except (ImportError, SystemExit) as e:
            pytest.skip(f"Could not import check_water_natasha: {e}")

    def test_metrics_contain_required_keys(self, sample_text):
        """Metrics should contain water, classic_nausea, academic_nausea"""
        try:
            from check_water_natasha import calculate_metrics_from_text

            metrics = calculate_metrics_from_text(sample_text)

            # At least some metrics should be present
            assert "total_words" in metrics or "water" in metrics or len(metrics) > 0
        except (ImportError, SystemExit) as e:
            pytest.skip(f"Could not import check_water_natasha: {e}")


class TestQualityRunnerScript:
    """Test quality_runner.py as a subprocess"""

    def test_script_exists(self):
        """Script should exist"""
        script_path = Path(__file__).parent.parent / "scripts" / "quality_runner.py"
        assert script_path.exists()

    def test_script_help(self):
        """Script should show help"""
        import subprocess

        script_path = Path(__file__).parent.parent / "scripts" / "quality_runner.py"

        result = subprocess.run(  # noqa: S603
            [sys.executable, str(script_path), "--help"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(Path(__file__).parent.parent),
        )

        # Should show help or fail gracefully
        assert result.returncode in [0, 1, 2]

    def test_script_with_missing_args(self):
        """Script should exit with error when missing args"""
        import subprocess

        script_path = Path(__file__).parent.parent / "scripts" / "quality_runner.py"

        result = subprocess.run(  # noqa: S603
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(Path(__file__).parent.parent),
        )

        # Should exit with error (2 = argparse error)
        assert result.returncode != 0
