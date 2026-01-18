import time
from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent

from ..persistence.repo import LoveRepo
from ..analysis.providers.message_provider import MessageProvider


class MessageHandler:
    """消息处理器，负责监听和解析用户发送的聊天消息"""

    # V2 引擎共享状态
    # {group_id: last_timestamp}
    _group_last_msg_time = {}
    # {group_id: {user_id: last_text}}
    _user_last_msg_text = {}

    TOPIC_THRESHOLD = 900  # 15 分钟沉默视为新话题 (破冰)

    def __init__(self, repo: LoveRepo):
        self.repo = repo
        self.provider = MessageProvider()

    async def handle_message(self, event: AstrMessageEvent):
        """处理群消息事件"""

        logger.debug(
            f"[LoveFormula] handle_message 开始处理: {event.message_obj.message_id}"
        )

        # 仅处理群消息
        if not event.message_obj.group_id:
            return

        group_id = str(event.message_obj.group_id)
        user_id = str(event.message_obj.sender.user_id)

        # 1. 使用 Provider 提取各项指标
        metrics = self.provider.extract_metrics(event)
        message_id = metrics["message_id"]
        text = metrics["text_content"]
        text_len = metrics["text_len"]
        image_count = metrics["image_count"]
        reply_target_id = metrics["reply_target_id"]

        # 2. 保存消息索引 (用于 Reaction 归因)
        await self.repo.save_message_index(message_id, group_id, user_id)

        # 3. V2 引擎指标分析 (破冰/重复)
        current_time = time.time()
        topic_inc = 0
        repeat_inc = 0

        # A. 破冰/开场 (Topic) 判定
        last_group_time = MessageHandler._group_last_msg_time.get(group_id, 0)
        if (
            last_group_time > 0
            and (current_time - last_group_time) > MessageHandler.TOPIC_THRESHOLD
        ):
            topic_inc = 1

        MessageHandler._group_last_msg_time[group_id] = current_time

        # B. 重复/刷屏 (Repeat) 判定
        user_last_texts = MessageHandler._user_last_msg_text.get(group_id, {})
        last_text = user_last_texts.get(user_id, "")
        if text and text == last_text:
            repeat_inc = 1

        if group_id not in MessageHandler._user_last_msg_text:
            MessageHandler._user_last_msg_text[group_id] = {}
        MessageHandler._user_last_msg_text[group_id][user_id] = text

        # 4. 更新 V2 统计
        if topic_inc > 0 or repeat_inc > 0:
            await self.repo.update_v2_stats(group_id, user_id, topic_inc, repeat_inc)

        # 5. 更新回复统计处理 (针对带有 MSG_REF: 的情况需要索引协助)
        final_reply_target_id = None
        if reply_target_id:
            if reply_target_id.startswith("MSG_REF:"):
                target_msg_id = reply_target_id.split(":")[1]
                owner_idx = await self.repo.get_message_owner(target_msg_id)
                if owner_idx:
                    final_reply_target_id = owner_idx.user_id
            else:
                final_reply_target_id = reply_target_id

        # 6. 更新每日统计和交互统计
        await self.repo.update_msg_stats(
            group_id=group_id,
            user_id=user_id,
            text_len=text_len,
            image_count=image_count,
        )

        if final_reply_target_id:
            await self.repo.update_interaction_sent(group_id, user_id, reply=1)
            if final_reply_target_id != str(user_id):
                await self.repo.update_interaction_received(
                    group_id, final_reply_target_id, reply=1
                )
