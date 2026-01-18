from abc import ABC, abstractmethod


class BaseDataProvider(ABC):
    """
    原始数据提取抽象基类。
    负责从原始事件（消息、通知等）中提取出用于分析的指标数据。
    """

    @abstractmethod
    def extract_metrics(self, event) -> dict:
        """提取指标"""
        pass
