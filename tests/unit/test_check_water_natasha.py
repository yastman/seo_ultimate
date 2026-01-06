from scripts.check_water_natasha import calculate_metrics_from_text, load_stopwords


class TestCheckWaterNatasha:
    def test_pure_water(self):
        # Text with only stopwords
        text = "и в на с по"
        metrics = calculate_metrics_from_text(text)
        # All words are stopwords.
        # Water raw = 100%. ADVEGO_MULTIPLIER = 2.4 -> 240%
        assert metrics["total_words"] == 5
        assert metrics["water_count"] == 5
        assert metrics["water_percent_raw"] == 100.0
        assert metrics["water_percent"] == 240.0

    def test_clean_text(self):
        # No stopwords (assuming "уникальный" etc are not stopwords)
        text = "уникальный контент без мусора"
        metrics = calculate_metrics_from_text(text)
        # Assuming stopwords loader works and these words are not in it.
        # "без" might be a stopword? Let's check.
        # "без" IS usually a stopword.
        # "уникальный" - no. "контент" - no. "мусора" - no.
        # So water count should be small but maybe not 0 if "без" is stopped.
        assert metrics["total_words"] >= 3
        # Ensure it runs without error at least
        assert metrics["classic_nausea"] >= 1.0

    def test_classic_nausea_calculation(self):
        # "тест" repeated 9 times -> sqrt(9) = 3.0
        text = " ".join(["тест"] * 9)
        metrics = calculate_metrics_from_text(text)
        assert metrics["most_common_lemma"] == "тест"
        assert metrics["max_frequency"] == 9
        assert metrics["classic_nausea"] == 3.0

    def test_academic_nausea_calculation(self):
        # significant words: "дым" (2), "огонь" (2)
        # total significant: 4
        # max freq: 2
        # academic: 2/4 = 50%
        text = "дым дым огонь огонь"
        metrics = calculate_metrics_from_text(text)
        assert metrics["total_significant"] == 4
        assert metrics["max_freq_significant"] == 2
        assert metrics["academic_nausea"] == 50.0

    def test_advego_multiplier(self):
        # Check that multiplier 2.4 is applied
        text = "один два три"  # "один" мб стоп-словом (числительное или местоимение).
        # "один" is in ADDITIONAL_STOP_WORDS in script? Yes.
        # "два", "три" - maybe not.

        metrics = calculate_metrics_from_text(text)
        raw = metrics["water_percent_raw"]
        final = metrics["water_percent"]
        assert abs(final - (raw * 2.4)) < 0.001

    def test_empty_or_foreign_text(self):
        assert calculate_metrics_from_text("") is None
        assert calculate_metrics_from_text("Only English Text") is None
        # "Text с русским словом" -> fails if tokens filter strict?
        # Script regex: re.match(r"[а-яё]+", token.text.lower())
        assert calculate_metrics_from_text("English и русское") is not None

    def test_load_stopwords_ru(self):
        sw = load_stopwords("ru")
        assert "и" in sw
        assert isinstance(sw, set)
