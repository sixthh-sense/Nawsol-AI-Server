"""
규칙 기반 자산 분배 추천 서비스
GPT Agent 없이 소득/지출 데이터 기반으로 자산 분배를 추천합니다.
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class RuleBasedAllocationService:
    """규칙 기반 자산 분배 추천 서비스"""
    
    # 표준 자산 분배 비율
    STANDARD_ALLOCATION = {
        "emergency_fund": 0.30,      # 비상자금 30%
        "short_term_savings": 0.20,  # 단기저축 20%
        "long_term_investment": 0.30, # 장기투자 30%
        "insurance": 0.10,           # 보험 10%
        "other": 0.10                # 기타 10%
    }
    
    # 위험 성향별 조정
    RISK_PROFILES = {
        "safe": {
            "emergency_fund": 0.40,
            "short_term_savings": 0.30,
            "long_term_investment": 0.15,
            "insurance": 0.10,
            "other": 0.05
        },
        "balanced": {
            "emergency_fund": 0.30,
            "short_term_savings": 0.20,
            "long_term_investment": 0.30,
            "insurance": 0.10,
            "other": 0.10
        },
        "aggressive": {
            "emergency_fund": 0.20,
            "short_term_savings": 0.10,
            "long_term_investment": 0.50,
            "insurance": 0.10,
            "other": 0.10
        }
    }
    
    def __init__(self):
        pass
    
    def generate_recommendation(
        self,
        income_data: Dict[str, Any],
        expense_data: Dict[str, Any],
        risk_profile: str = "balanced"
    ) -> Dict[str, Any]:
        """
        규칙 기반 자산 분배 추천 생성
        
        Args:
            income_data: 소득 데이터
            expense_data: 지출 데이터
            risk_profile: 위험 성향 (safe/balanced/aggressive)
            
        Returns:
            자산 분배 추천 결과
        """
        try:
            # 1. 기본 정보 추출 (🆕 중복 계산 방지)
            total_income = self._calculate_total_income(income_data)
            total_expense = self._calculate_total_expense(expense_data)
            
            # logger.info(f"💰 총 소득: {total_income:,}원 (중복 제거)")
            # logger.info(f"💸 총 지출: {total_expense:,}원 (중복 제거)")
            
            # 2. 가처분 소득 계산
            disposable_income = total_income - total_expense
            
            # 3. 건강 점수 계산
            health_score = self._calculate_health_score(total_income, total_expense, expense_data)
            
            # 4. 자산 분배 계산
            allocation_ratios = self.RISK_PROFILES.get(risk_profile, self.STANDARD_ALLOCATION)
            asset_allocation = self._calculate_allocation(disposable_income, allocation_ratios)
            
            # 5. 개선 제안 생성
            improvement_suggestions = self._generate_improvement_suggestions(
                total_income, total_expense, expense_data, health_score
            )
            
            # 6. 저축 목표 생성
            savings_goals = self._generate_savings_goals(disposable_income)
            
            return {
                "method": "rule_based",
                "strategy": risk_profile,
                "health_score": health_score,
                "asset_allocation": asset_allocation,
                "improvement_suggestions": improvement_suggestions,
                "savings_goals": savings_goals
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Rule-based recommendation failed: {str(e)}")
            return {"error": str(e), "method": "rule_based"}
    
    def _calculate_total_income(self, income_data: Dict[str, Any]) -> int:
        """
        총 소득 계산 (중복 제거)
        
        우선순위:
        1. "총소득" 또는 "총 소득" 필드가 있으면 그것만 사용
        2. 없으면 개별 INCOME 항목들을 합산 (TOTAL_INCOME 제외)
        
        Args:
            income_data: 소득 데이터
            
        Returns:
            총 소득 금액
        """
        # 🔍 1순위: 총소득 필드 확인
        total_keys = ["총소득", "총 소득", "total_income", "총수입", "총 수입"]
        
        for key in total_keys:
            value = income_data.get(key)
            if value is not None:
                try:
                    total = int(value)
                    logger.info(f"✅ [총소득] '{key}' 필드 사용: {total:,}원")
                    return total
                except (ValueError, TypeError):
                    continue
        
        # 🔍 2순위: 개별 항목 합산 (TOTAL_INCOME 타입 제외)
        logger.info(f"⚠️  [총소득] 총소득 필드 없음 → 개별 항목 합산")
        
        total = 0
        counted_items = []
        
        # 카테고리별 합계 확인
        category_totals = income_data.get("카테고리별 합계", {}) or income_data.get("total_by_main_category", {})
        
        if isinstance(category_totals, dict):
            for category, amount in category_totals.items():
                # "총소득" 카테고리는 제외 (중복 방지)
                if any(keyword in category for keyword in ["총소득", "총 소득", "total"]):
                    continue
                
                try:
                    total += int(amount)
                    counted_items.append(f"{category}: {amount:,}원")
                except (ValueError, TypeError):
                    continue
        
        # 카테고리가 없으면 개별 항목 직접 합산
        if total == 0:
            for key, value in income_data.items():
                if key in ["USER_TOKEN", "카테고리별 합계", "total_by_main_category"]:
                    continue
                
                # "총" 키워드 포함된 항목은 제외
                if "총" in key or "total" in key.lower():
                    continue
                
                try:
                    total += int(value)
                    counted_items.append(f"{key}: {value:,}원")
                except (ValueError, TypeError):
                    continue
        
        logger.info(f"📊 [개별 항목 합산] 총 {len(counted_items)}개 항목:")
        for item in counted_items:
            logger.info(f"   - {item}")
        logger.info(f"💰 합계: {total:,}원")
        
        return total
    
    def _calculate_total_expense(self, expense_data: Dict[str, Any]) -> int:
        """
        총 지출 계산 (중복 제거)
        
        우선순위:
        1. "총지출" 또는 "총 지출" 필드가 있으면 그것만 사용
        2. 없으면 개별 EXPENSE 항목들을 합산 (TOTAL_EXPENSE 제외)
        
        Args:
            expense_data: 지출 데이터
            
        Returns:
            총 지출 금액
        """
        # 🔍 1순위: 총지출 필드 확인
        total_keys = ["총지출", "총 지출", "total_expense", "총비용", "총 비용"]
        
        for key in total_keys:
            value = expense_data.get(key)
            if value is not None:
                try:
                    total = int(value)
                    logger.info(f"✅ [총지출] '{key}' 필드 사용: {total:,}원")
                    return total
                except (ValueError, TypeError):
                    continue
        
        # 🔍 2순위: 개별 항목 합산 (TOTAL_EXPENSE 타입 제외)
        logger.info(f"⚠️  [총지출] 총지출 필드 없음 → 개별 항목 합산")
        
        total = 0
        counted_items = []
        
        # 카테고리별 합계 확인
        category_totals = expense_data.get("카테고리별 합계", {}) or expense_data.get("total_by_main_category", {})
        
        if isinstance(category_totals, dict):
            for category, amount in category_totals.items():
                # "총지출" 카테고리는 제외 (중복 방지)
                if any(keyword in category for keyword in ["총지출", "총 지출", "total"]):
                    continue
                
                try:
                    total += int(amount)
                    counted_items.append(f"{category}: {amount:,}원")
                except (ValueError, TypeError):
                    continue
        
        # 카테고리가 없으면 개별 항목 직접 합산
        if total == 0:
            for key, value in expense_data.items():
                if key in ["USER_TOKEN", "카테고리별 합계", "total_by_main_category"]:
                    continue
                
                # "총" 키워드 포함된 항목은 제외
                if "총" in key or "total" in key.lower():
                    continue
                
                try:
                    total += int(value)
                    counted_items.append(f"{key}: {value:,}원")
                except (ValueError, TypeError):
                    continue
        
        logger.info(f"📊 [개별 항목 합산] 총 {len(counted_items)}개 항목:")
        for item in counted_items:
            logger.info(f"   - {item}")
        logger.info(f"💸 합계: {total:,}원")
        
        return total

    def _calculate_health_score(
        self,
        total_income: int,
        total_expense: int,
        expense_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """재무 건전성 점수 계산"""
        if total_income == 0:
            return {
                "overall": 0,
                "income_to_expense_ratio": 0,
                "essential_expense_ratio": 0,
                "savings_ratio": 0,
                "comment": "소득 정보가 부족합니다"
            }
        
        # 소득 대비 지출 비율
        expense_ratio = (total_expense / total_income) * 100
        
        # 저축 비율
        savings_ratio = ((total_income - total_expense) / total_income) * 100
        
        # 필수 지출 비율 추정 (보험, 세금, 주거비 등)
        essential_expense = self._estimate_essential_expense(expense_data)
        essential_ratio = (essential_expense / total_income) * 100
        
        # 전체 점수 계산 (100점 만점)
        score = 100
        
        # 지출 비율 평가 (이상적: 70% 이하)
        if expense_ratio > 90:
            score -= 40
        elif expense_ratio > 80:
            score -= 25
        elif expense_ratio > 70:
            score -= 10
        
        # 저축 비율 평가 (이상적: 20% 이상)
        if savings_ratio < 10:
            score -= 30
        elif savings_ratio < 20:
            score -= 15
        
        # 필수 지출 비율 평가 (이상적: 50% 이하)
        if essential_ratio > 60:
            score -= 20
        elif essential_ratio > 50:
            score -= 10
        
        # 코멘트 생성
        if score >= 80:
            comment = "매우 건전한 재무 상태입니다"
        elif score >= 60:
            comment = "양호한 재무 상태이나 개선의 여지가 있습니다"
        elif score >= 40:
            comment = "재무 관리 개선이 필요합니다"
        else:
            comment = "즉각적인 재무 개선이 필요합니다"
        
        return {
            "overall": max(0, score),
            "income_to_expense_ratio": round(expense_ratio, 2),
            "essential_expense_ratio": round(essential_ratio, 2),
            "savings_ratio": round(savings_ratio, 2),
            "comment": comment
        }
    
    def _estimate_essential_expense(self, expense_data: Dict[str, Any]) -> int:
        """필수 지출 추정"""
        essential_categories = [
            "보험", "insurance", "세금", "tax",
            "주거", "rent", "월세", "전세",
            "공과금", "utility", "통신비", "communication"
        ]
        
        total_essential = 0
        
        # 카테고리별 합계에서 필수 항목 찾기
        category_totals = expense_data.get("카테고리별 합계", {}) or expense_data.get("total_by_main_category", {})
        
        if isinstance(category_totals, dict):
            for category, amount in category_totals.items():
                if any(keyword in category for keyword in essential_categories):
                    try:
                        total_essential += int(amount)
                    except (ValueError, TypeError):
                        continue
        
        return total_essential
    
    def _calculate_allocation(
        self,
        disposable_income: int,
        allocation_ratios: Dict[str, float]
    ) -> Dict[str, Any]:
        """자산 분배 계산"""
        if disposable_income <= 0:
            return {
                "error": "가처분 소득이 부족합니다",
                "disposable_income": disposable_income
            }
        
        allocation = {}
        
        for category, ratio in allocation_ratios.items():
            allocation[category] = {
                "amount": int(disposable_income * ratio),
                "ratio": ratio * 100
            }
        
        allocation["disposable_income"] = disposable_income
        
        return allocation
    
    def _generate_improvement_suggestions(
        self,
        total_income: int,
        total_expense: int,
        expense_data: Dict[str, Any],
        health_score: Dict[str, Any]
    ) -> List[str]:
        """개선 제안 생성"""
        suggestions = []
        
        if total_income == 0:
            suggestions.append("소득 정보를 입력하여 정확한 분석을 받아보세요")
            return suggestions
        
        # 지출 비율 기반 제안
        expense_ratio = health_score.get("income_to_expense_ratio", 0)
        
        if expense_ratio > 80:
            suggestions.append(f"소득 대비 지출 비율이 {expense_ratio:.1f}%로 높습니다. 불필요한 지출을 줄여보세요")
        
        # 저축 비율 기반 제안
        savings_ratio = health_score.get("savings_ratio", 0)
        
        if savings_ratio < 20:
            suggestions.append(f"저축 비율이 {savings_ratio:.1f}%로 낮습니다. 최소 20% 이상 저축을 목표로 하세요")
        
        # 필수 지출 비율 기반 제안
        essential_ratio = health_score.get("essential_expense_ratio", 0)
        
        if essential_ratio > 50:
            suggestions.append(f"필수 지출 비율이 {essential_ratio:.1f}%로 높습니다. 고정 지출 감축을 고려해보세요")
        
        # 일반 제안
        if not suggestions:
            suggestions.append("전반적으로 양호한 재무 상태입니다. 현재 패턴을 유지하세요")
        
        return suggestions
    
    def _generate_savings_goals(self, disposable_income: int) -> Dict[str, Any]:
        """저축 목표 생성"""
        if disposable_income <= 0:
            return {
                "monthly_target": 0,
                "annual_target": 0,
                "comment": "가처분 소득이 부족합니다"
            }
        
        # 월 저축 목표 (가처분 소득의 30%)
        monthly_target = int(disposable_income * 0.3)
        
        return {
            "monthly_target": monthly_target,
            "annual_target": monthly_target * 12,
            "comment": f"매월 {monthly_target:,}원 저축을 목표로 하세요"
        }
