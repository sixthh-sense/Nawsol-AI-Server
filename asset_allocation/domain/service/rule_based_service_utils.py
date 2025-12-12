"""
AI 서비스를 위한 규칙 기반 처리 유틸리티
GPT 호출 없이 빠르게 결과를 제공합니다.
"""

from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


class RuleBasedServiceUtils:
    """규칙 기반 AI 서비스 유틸리티"""
    
    @staticmethod
    def analyze_future_assets(income_data: Dict, expense_data: Dict) -> str:
        """
        미래 자산 예측 (규칙 기반)
        
        Args:
            income_data: 소득 데이터
            expense_data: 지출 데이터
            
        Returns:
            HTML 형식의 미래 자산 예측 결과
        """
        try:
            # 총 소득/지출 추출
            total_income = RuleBasedServiceUtils._extract_total(income_data, ["총소득", "total_income"])
            total_expense = RuleBasedServiceUtils._extract_total(expense_data, ["총지출", "total_expense"])
            
            monthly_surplus = total_income - total_expense
            
            if monthly_surplus <= 0:
                return """
                <div style="padding: 20px; background-color: #fff3cd; border-left: 4px solid #ffc107;">
                    <h3>⚠️ 현재 지출이 소득을 초과하고 있습니다</h3>
                    <p>월 잉여금: <strong style="color: #dc3545;">{:,}원</strong></p>
                    <p>미래 자산 축적을 위해서는 먼저 지출을 줄이는 것이 필요합니다.</p>
                    <ul>
                        <li>불필요한 고정 지출 검토</li>
                        <li>선택적 지출 20% 감축 목표</li>
                        <li>수입 증대 방안 모색</li>
                    </ul>
                </div>
                """.format(monthly_surplus)
            
            # 미래 자산 예측 (1년, 3년, 5년, 10년)
            year_1 = monthly_surplus * 12
            year_3 = monthly_surplus * 36
            year_5 = monthly_surplus * 60
            year_10 = monthly_surplus * 120
            
            # 투자 수익률 가정 (연 5%)
            investment_return = 0.05 / 12  # 월 복리
            
            year_1_invested = RuleBasedServiceUtils._calculate_compound_interest(monthly_surplus, 12, investment_return)
            year_3_invested = RuleBasedServiceUtils._calculate_compound_interest(monthly_surplus, 36, investment_return)
            year_5_invested = RuleBasedServiceUtils._calculate_compound_interest(monthly_surplus, 60, investment_return)
            year_10_invested = RuleBasedServiceUtils._calculate_compound_interest(monthly_surplus, 120, investment_return)
            
            html = f"""
            <div style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px;">
                    📊 미래 자산 예측
                </h2>
                
                <div style="background-color: #e8f4f8; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #2980b9;">💰 현재 재무 상황</h3>
                    <p>월 소득: <strong style="color: #27ae60;">{total_income:,}원</strong></p>
                    <p>월 지출: <strong style="color: #e74c3c;">{total_expense:,}원</strong></p>
                    <p>월 잉여금: <strong style="color: #3498db;">{monthly_surplus:,}원</strong></p>
                    <p>저축률: <strong>{(monthly_surplus/total_income*100):.1f}%</strong></p>
                </div>
                
                <h3 style="color: #2980b9;">📈 저축만 했을 경우</h3>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr style="background-color: #34495e; color: white;">
                        <th style="padding: 12px; text-align: left;">기간</th>
                        <th style="padding: 12px; text-align: right;">예상 자산</th>
                    </tr>
                    <tr style="background-color: #ecf0f1;">
                        <td style="padding: 12px;">1년 후</td>
                        <td style="padding: 12px; text-align: right; font-weight: bold;">{year_1:,}원</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px;">3년 후</td>
                        <td style="padding: 12px; text-align: right; font-weight: bold;">{year_3:,}원</td>
                    </tr>
                    <tr style="background-color: #ecf0f1;">
                        <td style="padding: 12px;">5년 후</td>
                        <td style="padding: 12px; text-align: right; font-weight: bold;">{year_5:,}원</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px;">10년 후</td>
                        <td style="padding: 12px; text-align: right; font-weight: bold; color: #27ae60;">{year_10:,}원</td>
                    </tr>
                </table>
                
                <h3 style="color: #2980b9;">🚀 투자했을 경우 (연 5% 수익률 가정)</h3>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr style="background-color: #16a085; color: white;">
                        <th style="padding: 12px; text-align: left;">기간</th>
                        <th style="padding: 12px; text-align: right;">예상 자산</th>
                        <th style="padding: 12px; text-align: right;">투자 수익</th>
                    </tr>
                    <tr style="background-color: #d5f4e6;">
                        <td style="padding: 12px;">1년 후</td>
                        <td style="padding: 12px; text-align: right; font-weight: bold;">{year_1_invested:,}원</td>
                        <td style="padding: 12px; text-align: right; color: #27ae60;">+{(year_1_invested-year_1):,}원</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px;">3년 후</td>
                        <td style="padding: 12px; text-align: right; font-weight: bold;">{year_3_invested:,}원</td>
                        <td style="padding: 12px; text-align: right; color: #27ae60;">+{(year_3_invested-year_3):,}원</td>
                    </tr>
                    <tr style="background-color: #d5f4e6;">
                        <td style="padding: 12px;">5년 후</td>
                        <td style="padding: 12px; text-align: right; font-weight: bold;">{year_5_invested:,}원</td>
                        <td style="padding: 12px; text-align: right; color: #27ae60;">+{(year_5_invested-year_5):,}원</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px;">10년 후</td>
                        <td style="padding: 12px; text-align: right; font-weight: bold; color: #16a085;">{year_10_invested:,}원</td>
                        <td style="padding: 12px; text-align: right; color: #27ae60; font-weight: bold;">+{(year_10_invested-year_10):,}원</td>
                    </tr>
                </table>
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; margin-top: 20px; border-left: 4px solid #ffc107;">
                    <h3 style="color: #856404;">💡 재무 목표 달성 가이드</h3>
                    <ul style="line-height: 1.8;">
                        <li><strong>단기 목표 (1년):</strong> 비상자금 {monthly_surplus * 6:,}원 마련</li>
                        <li><strong>중기 목표 (3-5년):</strong> 목돈 마련 (전세자금, 차량 구입)</li>
                        <li><strong>장기 목표 (10년+):</strong> 노후 준비 자산 형성</li>
                    </ul>
                    <p style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #f0e68c;">
                        <strong>투자 포트폴리오 추천:</strong><br>
                        • 안전 자산 (예적금, 채권) 40%<br>
                        • 성장 자산 (주식, 펀드, ETF) 50%<br>
                        • 대체 투자 (부동산, 금) 10%
                    </p>
                </div>
            </div>
            """
            
            return html
            
        except Exception as e:
            logger.error(f"[ERROR] Future assets analysis failed: {str(e)}")
            return f"<p>오류가 발생했습니다: {str(e)}</p>"
    
    @staticmethod
    def analyze_tax_credit(income_data: Dict, expense_data: Dict) -> str:
        """
        세액 공제 확인 (규칙 기반)
        
        Args:
            income_data: 소득 데이터
            expense_data: 지출 데이터
            
        Returns:
            HTML 형식의 세액 공제 확인 결과
        """
        try:
            # 공제 가능 항목 추출
            deductible_items = []
            
            # 지출 데이터에서 공제 가능 항목 찾기
            for key, value in expense_data.items():
                if key in ["카테고리별 합계", "총지출", "total_expense", "total_by_main_category"]:
                    continue
                
                # 공제 가능 키워드
                keywords = {
                    "의료비": ("의료비 세액공제", "15% 공제 (700만원 초과분 20%)"),
                    "교육비": ("교육비 세액공제", "15% 공제"),
                    "기부금": ("기부금 세액공제", "15-30% 공제"),
                    "보험료": ("보험료 세액공제", "12% 공제"),
                    "연금": ("연금저축 세액공제", "12-15% 공제 (최대 400만원)"),
                    "주택자금": ("주택자금 소득공제", "40-300만원 공제"),
                    "월세": ("월세 세액공제", "10-12% 공제 (최대 750만원)")
                }
                
                for keyword, (category, rate) in keywords.items():
                    if keyword in str(key):
                        try:
                            amount = int(value) if isinstance(value, (int, str)) else 0
                            if amount > 0:
                                deductible_items.append((category, amount, rate))
                        except (ValueError, TypeError):
                            continue
            
            if not deductible_items:
                return """
                <div style="padding: 20px; background-color: #f8d7da; border-left: 4px solid: #dc3545;">
                    <h3>❌ 세액 공제 가능 항목이 없습니다</h3>
                    <p>업로드한 지출 내역에서 세액 공제 가능 항목을 찾을 수 없습니다.</p>
                    <p>다음 항목들을 확인해보세요:</p>
                    <ul>
                        <li>의료비 지출</li>
                        <li>교육비 지출</li>
                        <li>기부금</li>
                        <li>보험료</li>
                        <li>연금저축</li>
                    </ul>
                </div>
                """
            
            # HTML 생성
            rows = ""
            total_deduction = 0
            
            for category, amount, rate in deductible_items:
                # 간단한 공제액 추정 (실제로는 복잡한 계산 필요)
                if "15%" in rate:
                    estimated = int(amount * 0.15)
                elif "12%" in rate:
                    estimated = int(amount * 0.12)
                elif "10%" in rate:
                    estimated = int(amount * 0.10)
                else:
                    estimated = int(amount * 0.12)  # 기본값
                
                total_deduction += estimated
                
                rows += f"""
                <tr style="background-color: #f8f9fa;">
                    <td style="padding: 12px;">{category}</td>
                    <td style="padding: 12px; text-align: right;">{amount:,}원</td>
                    <td style="padding: 12px; text-align: center;">{rate}</td>
                    <td style="padding: 12px; text-align: right; color: #27ae60; font-weight: bold;">약 {estimated:,}원</td>
                </tr>
                """
            
            html = f"""
            <div style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px;">
                    💳 세액 공제 확인
                </h2>
                
                <div style="background-color: #d4edda; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745;">
                    <h3 style="color: #155724;">✅ 공제 가능 항목 발견</h3>
                    <p>총 <strong>{len(deductible_items)}개</strong>의 세액 공제 가능 항목이 있습니다.</p>
                    <p style="font-size: 18px; margin-top: 10px;">
                        예상 세액 공제: <strong style="color: #28a745;">{total_deduction:,}원</strong>
                    </p>
                </div>
                
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr style="background-color: #34495e; color: white;">
                        <th style="padding: 12px; text-align: left;">공제 항목</th>
                        <th style="padding: 12px; text-align: right;">지출 금액</th>
                        <th style="padding: 12px; text-align: center;">공제율</th>
                        <th style="padding: 12px; text-align: right;">예상 공제액</th>
                    </tr>
                    {rows}
                </table>
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; margin-top: 20px; border-left: 4px solid #ffc107;">
                    <h3 style="color: #856404;">⚠️ 주의사항</h3>
                    <ul style="line-height: 1.8;">
                        <li>위 금액은 <strong>예상 공제액</strong>이며, 실제 공제액은 다를 수 있습니다.</li>
                        <li>소득 수준, 다른 공제 항목, 한도 등에 따라 실제 공제액이 달라질 수 있습니다.</li>
                        <li>정확한 세액 공제를 위해서는 세무사와 상담하시기 바랍니다.</li>
                        <li>연말정산 시 증빙 서류를 반드시 준비하세요.</li>
                    </ul>
                </div>
                
                <div style="background-color: #e8f4f8; padding: 15px; border-radius: 8px; margin-top: 20px;">
                    <h3 style="color: #2980b9;">💡 추가 공제 항목 체크리스트</h3>
                    <ul style="line-height: 1.8;">
                        <li>☐ 신용카드/체크카드 사용액 (소득공제)</li>
                        <li>☐ 청약저축 (소득공제)</li>
                        <li>☐ 소기업·소상공인 공제부금 (소득공제)</li>
                        <li>☐ 우리사주조합 출자금 (소득공제)</li>
                        <li>☐ 장기집합투자증권저축 (소득공제)</li>
                    </ul>
                </div>
            </div>
            """
            
            return html
            
        except Exception as e:
            logger.error(f"[ERROR] Tax credit analysis failed: {str(e)}")
            return f"<p>오류가 발생했습니다: {str(e)}</p>"
    
    @staticmethod
    def analyze_deduction_expectation(income_data: Dict, expense_data: Dict) -> str:
        """
        연말정산 공제 내역 확인 (규칙 기반)
        
        Args:
            income_data: 소득 데이터
            expense_data: 지출 데이터
            
        Returns:
            HTML 형식의 연말정산 공제 내역
        """
        # 세액 공제와 유사한 로직 사용
        return RuleBasedServiceUtils.analyze_tax_credit(income_data, expense_data)
    
    @staticmethod
    def analyze_financial_guide(income_data: Dict, expense_data: Dict, target_amount: int = 10000000, target_months: int = 12) -> str:
        """
        목표 금액 재무 가이드 (규칙 기반)
        
        Args:
            income_data: 소득 데이터
            expense_data: 지출 데이터
            target_amount: 목표 금액
            target_months: 목표 기간 (개월)
            
        Returns:
            HTML 형식의 재무 가이드
        """
        try:
            total_income = RuleBasedServiceUtils._extract_total(income_data, ["총소득", "total_income"])
            total_expense = RuleBasedServiceUtils._extract_total(expense_data, ["총지출", "total_expense"])
            
            monthly_surplus = total_income - total_expense
            monthly_required = target_amount / target_months
            
            if monthly_surplus >= monthly_required:
                status = "달성 가능"
                status_color = "#28a745"
                message = f"현재 저축률로 {target_months}개월 안에 목표 달성이 가능합니다!"
            elif monthly_surplus > 0:
                actual_months = int(target_amount / monthly_surplus)
                status = "기간 조정 필요"
                status_color = "#ffc107"
                message = f"현재 저축률로는 약 {actual_months}개월이 필요합니다."
            else:
                status = "달성 불가"
                status_color = "#dc3545"
                message = "현재 지출이 소득을 초과하여 저축이 불가능합니다."
            
            # 필요한 지출 절감액
            deficit = max(0, monthly_required - monthly_surplus)
            
            html = f"""
            <div style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px;">
                    🎯 목표 금액 재무 가이드
                </h2>
                
                <div style="background-color: #e8f4f8; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #2980b9;">📊 목표 설정</h3>
                    <p style="font-size: 24px; margin: 10px 0;">
                        목표 금액: <strong style="color: #3498db;">{target_amount:,}원</strong>
                    </p>
                    <p style="font-size: 18px;">
                        목표 기간: <strong>{target_months}개월</strong>
                    </p>
                </div>
                
                <div style="background-color: {status_color}20; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid {status_color};">
                    <h3 style="color: {status_color};">달성 가능성: {status}</h3>
                    <p style="font-size: 16px;">{message}</p>
                </div>
                
                <h3 style="color: #2980b9;">💰 현재 재무 상황</h3>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr style="background-color: #ecf0f1;">
                        <td style="padding: 12px;">월 소득</td>
                        <td style="padding: 12px; text-align: right; font-weight: bold; color: #27ae60;">{total_income:,}원</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px;">월 지출</td>
                        <td style="padding: 12px; text-align: right; font-weight: bold; color: #e74c3c;">{total_expense:,}원</td>
                    </tr>
                    <tr style="background-color: #ecf0f1;">
                        <td style="padding: 12px;">월 저축 가능액</td>
                        <td style="padding: 12px; text-align: right; font-weight: bold; color: #3498db;">{monthly_surplus:,}원</td>
                    </tr>
                    <tr style="background-color: #fff3cd;">
                        <td style="padding: 12px;"><strong>월 필요 저축액</strong></td>
                        <td style="padding: 12px; text-align: right; font-weight: bold; color: #856404;">{int(monthly_required):,}원</td>
                    </tr>
            """
            
            if deficit > 0:
                html += f"""
                    <tr style="background-color: #f8d7da;">
                        <td style="padding: 12px;"><strong>부족액</strong></td>
                        <td style="padding: 12px; text-align: right; font-weight: bold; color: #721c24;">{int(deficit):,}원</td>
                    </tr>
                """
            
            html += """
                </table>
            """
            
            # 실행 계획
            html += """
                <div style="background-color: #d4edda; padding: 20px; border-radius: 8px; margin-top: 20px; border-left: 4px solid #28a745;">
                    <h3 style="color: #155724;">✅ 목표 달성 실행 계획</h3>
                    <ol style="line-height: 2;">
            """
            
            if deficit > 0:
                html += f"""
                        <li><strong>지출 절감:</strong> 월 {int(deficit):,}원 절감 필요</li>
                        <li><strong>우선순위:</strong> 선택적 지출 항목부터 줄이기</li>
                        <li><strong>대안:</strong> 부수입 창출 고려 (투잡, 프리랜싱)</li>
                """
            else:
                html += f"""
                        <li><strong>자동이체 설정:</strong> 월 {int(monthly_required):,}원 자동 저축</li>
                        <li><strong>여유 자금:</strong> 남는 {int(monthly_surplus - monthly_required):,}원은 추가 투자</li>
                        <li><strong>비상자금:</strong> 목표 달성 후 비상자금 마련</li>
                """
            
            html += """
                    </ol>
                </div>
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; margin-top: 20px; border-left: 4px solid #ffc107;">
                    <h3 style="color: #856404;">💡 재무 목표 달성 팁</h3>
                    <ul style="line-height: 1.8;">
                        <li>급여일에 자동이체로 먼저 저축하기</li>
                        <li>고금리 적금 상품 활용하기</li>
                        <li>포인트, 리워드 적극 활용하기</li>
                        <li>불필요한 구독 서비스 해지하기</li>
                        <li>월 단위로 저축 진행상황 점검하기</li>
                    </ul>
                </div>
            </div>
            """
            
            return html
            
        except Exception as e:
            logger.error(f"[ERROR] Financial guide analysis failed: {str(e)}")
            return f"<p>오류가 발생했습니다: {str(e)}</p>"
    
    # 헬퍼 메서드
    @staticmethod
    def _extract_total(data: Dict[str, Any], keys: List[str]) -> int:
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
    def _calculate_compound_interest(monthly_amount: int, months: int, monthly_rate: float) -> int:
        """복리 계산"""
        if monthly_rate == 0:
            return monthly_amount * months
        
        # FV = P * [((1 + r)^n - 1) / r]
        future_value = monthly_amount * (((1 + monthly_rate) ** months - 1) / monthly_rate)
        return int(future_value)
