from abc import ABC, abstractmethod


class BaseCollector(ABC):
    """
    领域指标采集器基类 (DDD Pattern)
    负责从事件流中提取该领域特有的指标数据。
    """

    @abstractmethod
    def collect(self, event) -> dict:
        """从事件中采集指标数据"""
        pass
