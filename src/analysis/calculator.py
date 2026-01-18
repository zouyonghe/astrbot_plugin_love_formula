import math
from ..models.tables import LoveDailyRef


class LoveCalculator:
    # Weights for Simp Score (Effort/Output)
    W_MSG_SENT = 1.0
    W_POKE_SENT = 2.0
    W_AVG_LEN = 0.05  # Per character

    # Weights for Vibe Score (Feedback/Input)
    W_REPLY_RECV = 3.0
    W_REACTION_RECV = 2.0
    W_POKE_RECV = 2.0

    # Weights for Ick Score (Negative)
    W_RECALL = 5.0

    @staticmethod
    def calculate_scores(data: LoveDailyRef) -> dict:
        # 1. Simp Score Calculation (S)
        avg_len = data.text_len_total / data.msg_sent if data.msg_sent > 0 else 0
        raw_simp = (
            data.msg_sent * LoveCalculator.W_MSG_SENT
            + data.poke_sent * LoveCalculator.W_POKE_SENT
            + avg_len * LoveCalculator.W_AVG_LEN
        )

        # 2. Vibe Score Calculation (V)
        raw_vibe = (
            data.reply_received * LoveCalculator.W_REPLY_RECV
            + data.reaction_received * LoveCalculator.W_REACTION_RECV
            + data.poke_received * LoveCalculator.W_POKE_RECV
        )

        # 3. Ick Score Calculation (I)
        raw_ick = data.recall_count * LoveCalculator.W_RECALL

        # 4. Normalization (using sigmoid to map to 0-100)
        # Using a relaxed sigmoid: 100 * (2 / (1 + e^(-0.1 * x)) - 1)
        # This maps 0 -> 0, 10 -> 46, 20 -> 76, 50 -> 98

        def normalize(x):
            if x <= 0:
                return 0
            return int(100 * (2 / (1 + math.exp(-0.05 * x)) - 1))

        return {
            "simp": normalize(raw_simp),
            "vibe": normalize(raw_vibe),
            "ick": normalize(raw_ick),
            "raw": {"simp": raw_simp, "vibe": raw_vibe, "ick": raw_ick},
        }
