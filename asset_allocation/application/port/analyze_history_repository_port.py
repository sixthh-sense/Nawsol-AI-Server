"""
AnalyzeHistory Repository Port (인터페이스)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class AnalyzeHistoryRepositoryPort(ABC):
    """미래 자산 예측 분석 이력 저장소 인터페이스"""
    
    @abstractmethod
    def find_similar_pattern(self, pattern: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        유사한 패턴 검색
        
        Args:
            pattern: 소비 패턴 정보
        
        Returns:
            유사한 패턴 정보 또는 None
        """
        pass
    
    @abstractmethod
    def save_gpt_advice(self, pattern: Dict[str, Any], gpt_advice: str) -> bool:
        """
        GPT 조언 저장
        
        Args:
            pattern: 소비 패턴 정보
            gpt_advice: GPT 조언
        
        Returns:
            성공 여부
        """
        pass
    
    @abstractmethod
    def increment_use_count(self, analyze_id: int) -> bool:
        """
        사용 횟수 증가
        
        Args:
            analyze_id: 분석 ID
        
        Returns:
            성공 여부
        """
        pass
    
    @abstractmethod
    def get_total_count(self) -> int:
        """
        전체 레코드 수 조회
        
        Returns:
            레코드 수
        """
        pass
