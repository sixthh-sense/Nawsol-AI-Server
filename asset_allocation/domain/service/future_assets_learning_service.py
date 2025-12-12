"""
미래 자산 예측 학습 기반 서비스 (Repository 패턴)
GPT 조언을 학습하여 유사한 패턴의 사용자에게 재사용
"""

from typing import Dict, Any, Optional
from config.database.session import SessionLocal
from asset_allocation.infrastructure.repository.analyze_history_repository_impl import AnalyzeHistoryRepositoryImpl
import logging

logger = logging.getLogger(__name__)


class FutureAssetsLearningService:
    """미래 자산 예측 학습 기반 서비스"""
    
    @staticmethod
    def calculate_pattern(income_data: Dict, expense_data: Dict) -> Dict[str, Any]:
        """
        소비 패턴 & 자산 수준 계산
        
        Args:
            income_data: 소득 데이터 (카테고리별)
            expense_data: 지출 데이터 (카테고리별)
            
        Returns:
            Dict 패턴 정보
        """
        # 총 소득/지출 추출
        monthly_income = FutureAssetsLearningService._extract_total(
            income_data, ["총소득", "total_income", "total"]
        )
        monthly_expense = FutureAssetsLearningService._extract_total(
            expense_data, ["총지출", "total_expense", "total"]
        )
        
        # 🔥 소득이 0원이어도 처리 (데이터 없는 경우)
        if monthly_income == 0:
            logger.info("[INFO] Monthly income is 0 - proceeding with default pattern")
            # 소득 0원일 때는 비율을 0 또는 100으로 설정
            expense_ratio = 0.0
            savings_ratio = 0.0
        else:
            # 기본 지표 계산
            expense_ratio = round((monthly_expense / monthly_income) * 100, 2)
            savings_ratio = round(((monthly_income - monthly_expense) / monthly_income) * 100, 2)
        
        monthly_surplus = monthly_income - monthly_expense
        
        # 지출 카테고리 비율 계산
        essential_ratio = FutureAssetsLearningService._calculate_category_ratio(
            expense_data, ["필수", "essential", "주거", "식비", "교통"], monthly_expense
        )
        leisure_ratio = FutureAssetsLearningService._calculate_category_ratio(
            expense_data, ["여가", "leisure", "문화", "취미"], monthly_expense
        )
        investment_ratio = FutureAssetsLearningService._calculate_category_ratio(
            expense_data, ["투자", "investment", "저축", "연금"], monthly_expense
        )
        other_ratio = 100.0 - essential_ratio - leisure_ratio - investment_ratio
        
        # 자산 수준 결정
        asset_level = FutureAssetsLearningService._determine_asset_level(monthly_surplus)
        
        return {
            "monthly_income": monthly_income,
            "monthly_expense": monthly_expense,
            "monthly_surplus": monthly_surplus,
            "expense_ratio": expense_ratio,
            "savings_ratio": savings_ratio,
            "essential_ratio": essential_ratio,
            "leisure_ratio": leisure_ratio,
            "investment_ratio": investment_ratio,
            "other_ratio": other_ratio,
            "asset_level": asset_level
        }
    
    @staticmethod
    def find_similar_pattern(pattern: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        ANALYZE_HISTORY에서 유사한 패턴 검색 (Repository 사용)
        
        Args:
            pattern: 현재 사용자의 패턴
            
        Returns:
            유사한 패턴의 GPT 조언 (dict) 또는 None
        """
        try:
            db = SessionLocal()
            repository = AnalyzeHistoryRepositoryImpl(db)
            
            # 유사 패턴 검색
            similar_pattern = repository.find_similar_pattern(pattern)
            
            # USE_COUNT 증가
            if similar_pattern:
                repository.increment_use_count(similar_pattern["analyze_id"])
                similar_pattern["use_count"] += 1
            
            db.close()
            return similar_pattern
                
        except Exception as e:
            logger.error(f"[ERROR] find_similar_pattern failed: {str(e)}")
            return None
    
    @staticmethod
    def save_gpt_advice(pattern: Dict[str, Any], gpt_advice: str):
        """
        GPT 조언을 ANALYZE_HISTORY에 저장 (Repository 사용)
        
        Args:
            pattern: 소비 패턴 정보
            gpt_advice: GPT가 생성한 조언 (HTML)
        """
        try:
            db = SessionLocal()
            repository = AnalyzeHistoryRepositoryImpl(db)
            
            # GPT 조언 저장
            success = repository.save_gpt_advice(pattern, gpt_advice)
            
            if success:
                logger.info("[INFO] GPT advice saved successfully")
            else:
                logger.error("[ERROR] Failed to save GPT advice")
            
            db.close()
            
        except Exception as e:
            logger.error(f"[ERROR] save_gpt_advice failed: {str(e)}")
    
    # 헬퍼 메서드
    @staticmethod
    def _extract_total(data: Dict[str, Any], keys: list) -> int:
        """데이터에서 총액 추출"""
        for key in keys:
            value = data.get(key)
            if value is not None:
                try:
                    return int(value)
                except (ValueError, TypeError):
                    continue
        return 0
    
    @staticmethod
    def _calculate_category_ratio(data: Dict[str, Any], keywords: list, total_expense: int) -> float:
        """특정 카테고리의 지출 비율 계산"""
        if total_expense == 0:
            return 0.0
        
        category_sum = 0
        for key, value in data.items():
            # 카테고리별 합계 또는 총액 키는 제외
            if any(x in str(key).lower() for x in ["합계", "total", "카테고리별"]):
                continue
            
            # 키워드 매칭
            if any(keyword in str(key) for keyword in keywords):
                try:
                    category_sum += int(value)
                except (ValueError, TypeError):
                    continue
        
        return round((category_sum / total_expense) * 100, 2)
    
    @staticmethod
    def _determine_asset_level(monthly_surplus: int) -> str:
        """월 잉여금 기반 자산 수준 결정"""
        if monthly_surplus < 0:
            return "DEFICIT"  # 적자
        elif monthly_surplus < 500000:
            return "LOW"  # 낮음 (50만원 미만)
        elif monthly_surplus < 1500000:
            return "MEDIUM"  # 중간 (50-150만원)
        elif monthly_surplus < 3000000:
            return "HIGH"  # 높음 (150-300만원)
        else:
            return "VERY_HIGH"  # 매우 높음 (300만원 이상)
