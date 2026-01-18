class ArchetypeClassifier:
    ARCHETYPES = {
        "THE_SIMP": "沸羊羊 (The Simp)",
        "THE_PLAYER": "海王 (The Player)",
        "HIMBO": "笨蛋美人 (Himbo)",
        "NPC": "路人甲 (NPC)",
        "IDOL": "高冷男神/女神 (The Idol)",
        "NORMAL": "普通群友 (Normal)",
    }

    @staticmethod
    def classify(scores: dict) -> tuple[str, str]:
        s = scores["simp"]
        v = scores["vibe"]
        i = scores["ick"]

        # Classification Logic
        if i > 60 and v > 50:
            return "HIMBO", ArchetypeClassifier.ARCHETYPES["HIMBO"]

        if s > 70 and v < 30:
            return "THE_SIMP", ArchetypeClassifier.ARCHETYPES["THE_SIMP"]

        if s < 40 and v > 70:
            return "THE_PLAYER", ArchetypeClassifier.ARCHETYPES["THE_PLAYER"]

        if s < 15 and v > 40:
            return "IDOL", ArchetypeClassifier.ARCHETYPES["IDOL"]

        if s < 20 and v < 20:
            return "NPC", ArchetypeClassifier.ARCHETYPES["NPC"]

        return "NORMAL", ArchetypeClassifier.ARCHETYPES["NORMAL"]
