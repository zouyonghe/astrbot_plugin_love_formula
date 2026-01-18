from .base import BaseDataProvider


class NoticeProvider(BaseDataProvider):
    """
    通知数据提供者 (Notice Data Provider)
    负责处理戳一戳、表情、撤回等原始通知数据。
    """

    def extract_metrics(self, event_data: dict) -> dict:
        notice_type = event_data.get("notice_type")
        sub_type = event_data.get("sub_type")

        metrics = {
            "type": notice_type,
            "sub_type": sub_type,
            "poke": 0,
            "reaction": 0,
            "recall": 0,
            "target_id": None,
            "message_id": None,
        }

        # 1. 戳一戳
        if notice_type == "notify" and sub_type == "poke":
            metrics["poke"] = 1
            metrics["target_id"] = str(event_data.get("target_id", ""))

        # 2. 表情回应
        elif notice_type == "group_msg_emoji_like":
            metrics["reaction"] = 1
            metrics["message_id"] = str(event_data.get("message_id", ""))

        # 3. 撤回
        elif notice_type == "group_recall":
            metrics["recall"] = 1
            metrics["message_id"] = str(event_data.get("message_id", ""))

        return metrics
