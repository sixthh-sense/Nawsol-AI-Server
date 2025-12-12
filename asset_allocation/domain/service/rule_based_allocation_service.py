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
            # 1. 기본 정보 추출
            total_income = self._extract_total(income_data, ["총소득", "total_income"])
            total_expense = self._extract_total(expense_data, ["총지출", "total_expense"])
            
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
    
    def _extract_total(self, data: Dict[str, Any], keys: List[str]) -> int:
        """데이터에서 총액 추출"""
        for key in keys:
            value = data.get(key)
            if value is not None:
                try:
                    return int(value)
                except (ValueError, TypeError):
                    continue
        return 0
    
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
    ) -> Dict[str, Dict[str, Any]]:
        """자산 분배 계산"""
        if disposable_income <= 0:
            return {
                "message": "가처분 소득이 부족하여 자산 분배가 어렵습니다",
                "disposable_income": disposable_income
            }
        
        allocation = {}
        reasons = {
            "emergency_fund": "예상치 못한 지출에 대비한 안전망",
            "short_term_savings": "1년 이내 목표를 위한 단기 저축",
            "long_term_investment": "노후 대비 및 자산 증식을 위한 장기 투자",
            "insurance": "건강 및 생명 보험료",
            "other": "여가 및 자기계발"
        }
        
        korean_names = {
            "emergency_fund": "비상자금",
            "short_term_savings": "단기저축",
            "long_term_investment": "장기투자",
            "insurance": "보험",
            "other": "기타"
        }
        
        for key, ratio in allocation_ratios.items():
            amount = int(disposable_income * ratio)
            percentage = ratio * 100
            
            allocation[korean_names[key]] = {
                "amount": amount,
                "percentage": round(percentage, 1),
                "reason": reasons[key]
            }
        
        return allocation
    
    def _generate_improvement_suggestions(
        self,
        total_income: int,
        total_expense: int,
        expense_data: Dict[str, Any],
        health_score: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """개선 제안 생성"""
        suggestions = []
        priority = 1
        
        # 1. 지출 비율이 높은 경우
        if health_score["income_to_expense_ratio"] > 80:
            suggestions.append({
                "priority": priority,
                "category": "지출 관리",
                "action": "월 지출을 소득의 70% 이하로 줄이세요",
                "expected_saving": int(total_expense * 0.1)
            })
            priority += 1
        
        # 2. 저축 비율이 낮은 경우
        if health_score["savings_ratio"] < 20:
            target_savings = int(total_income * 0.2)
            current_savings = total_income - total_expense
            suggestions.append({
                "priority": priority,
                "category": "저축",
                "action": f"월 저축액을 {target_savings:,}원으로 늘리세요 (소득의 20%)",
                "expected_saving": target_savings - current_savings
            })
            priority += 1
        
        # 3. 선택적 지출 줄이기
        optional_categories = ["여가", "외식", "쇼핑", "문화생활"]
        category_totals = expense_data.get("카테고리별 합계", {}) or expense_data.get("total_by_main_category", {})
        
        if isinstance(category_totals, dict):
            for category, amount in category_totals.items():
                if any(keyword in category for keyword in optional_categories):
                    try:
                        amount_int = int(amount)
                        if amount_int > total_income * 0.1:  # 소득의 10% 초과
                            suggestions.append({
                                "priority": priority,
                                "category": category,
                                "action": f"{category} 지출을 20% 줄이세요",
                                "expected_saving": int(amount_int * 0.2)
                            })
                            priority += 1
                    except (ValueError, TypeError):
                        continue
        
        return suggestions[:5]  # 상위 5개만 반환
    
    def _generate_savings_goals(self, disposable_income: int) -> Dict[str, Dict[str, Any]]:
        """저축 목표 생성"""
        if disposable_income <= 0:
            return {
                "short_term": {"target": "지출 줄이기", "amount": 0, "months": 0},
                "medium_term": {"target": "수입 늘리기", "amount": 0, "months": 0},
                "long_term": {"target": "재무 안정화", "amount": 0, "months": 0}
            }
        
        return {
            "short_term": {
                "target": "비상자금 마련",
                "amount": disposable_income * 6,  # 6개월치
                "months": 6
            },
            "medium_term": {
                "target": "목돈 마련 (전세자금, 차량 구입 등)",
                "amount": disposable_income * 36,  # 3년치
                "months": 36
            },
            "long_term": {
                "target": "노후 준비 (5,000만원 목표)",
                "amount": 50000000,
                "months": int(50000000 / disposable_income) if disposable_income > 0 else 0
            }
        }
