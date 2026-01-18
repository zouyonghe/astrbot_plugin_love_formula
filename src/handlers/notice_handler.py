from astrbot.api import logger
from ..persistence.repo import LoveRepo
from ..analysis.providers.notice_provider import NoticeProvider


class NoticeHandler:
    """通知事件处理器，负责处理戳一戳、表情回应和撤回等通知"""

    def __init__(self, repo: LoveRepo):
        self.repo = repo
        self.provider = NoticeProvider()

    async def handle_notice(self, event_data: dict):
        """
        处理来自 NapCat/OneBot V11 的原始通知事件
        """
        if event_data.get("post_type") != "notice":
            return

        group_id = str(event_data.get("group_id", ""))
        user_id = str(event_data.get("user_id", ""))
        if not group_id:
            return

        # 1. 使用 Provider 提取指标
        metrics = self.provider.extract_metrics(event_data)

        # 2. 根据提取结果进行业务分发
        # A. 戳一戳
        if metrics["poke"]:
            await self.repo.update_interaction_sent(group_id, user_id, poke=1)
            if metrics["target_id"]:
                await self.repo.update_interaction_received(
                    group_id, metrics["target_id"], poke=1
                )

        # B. 表情回应
        elif metrics["reaction"] and metrics["message_id"]:
            msg_idx = await self.repo.get_message_owner(metrics["message_id"])
            if msg_idx:
                await self.repo.update_interaction_sent(group_id, user_id, reaction=1)
                await self.repo.update_interaction_received(
                    group_id, msg_idx.user_id, reaction=1
                )

        # C. 撤回
        elif metrics["recall"]:
            await self.repo.update_interaction_sent(group_id, user_id, recall=1)
