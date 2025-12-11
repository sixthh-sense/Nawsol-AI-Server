import asyncio
from typing import Dict, List
from openai import OpenAI
from util.log.log import Log

logger = Log.get_logger()
client = OpenAI()

class FundRecommendationService:

    @staticmethod
    async def _call_gpt(prompt: str, max_tokens: int = 2000) -> str:
        """GPT API 비동기 호출"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            ).choices[0].message.content
        )
    
    @staticmethod
    def _build_financial_profile(
        income_data: Dict[str, int],
        expense_data: Dict[str, int],
        total_income: int,
        total_expense: int,
        surplus: int
    ) -> str:
        """재무 프로필 문자열 생성"""
        profile_parts = []
        
        # 기본 재무 정보
        profile_parts.append(f"📊 재무 요약")
        profile_parts.append(f"- 총 소득: {total_income:,}원")
        profile_parts.append(f"- 총 지출: {total_expense:,}원")
        profile_parts.append(f"- 여유 자금: {surplus:,}원")
        profile_parts.append(f"- 저축률: {(surplus/total_income*100):.1f}%" if total_income > 0 else "- 저축률: 0%")
        
        # 소득 상세
        if income_data:
            profile_parts.append(f"\n💰 소득 내역")
            for key, value in sorted(income_data.items(), key=lambda x: x[1], reverse=True)[:5]:
                profile_parts.append(f"- {key}: {value:,}원")
        
        # 지출 상세
        if expense_data:
            profile_parts.append(f"\n💸 주요 지출")
            for key, value in sorted(expense_data.items(), key=lambda x: x[1], reverse=True)[:5]:
                profile_parts.append(f"- {key}: {value:,}원")
        
        return "\n".join(profile_parts)
    
    @staticmethod
    def _build_fund_list(fund_data: List[Dict]) -> str:
        if not fund_data:
            return "Fund 데이터가 없습니다."
        
        fund_parts = []
        fund_parts.append(f"📈 분석 가능한 Fund 목록 ({len(fund_data)}개)")
        
        # 상위 10개 Fund만 표시 : 어떤 기준으로 가져올지 고민됨. 우선 설정일로 잡음
        sorted_funds = sorted(
            fund_data,
            key=lambda x: x.get('setpDt', 0) or 0,
            reverse=True
        )[:10]
        
        for idx, fund in enumerate(sorted_funds, 1):
            name = fund.get('fndNm', 'N/A')
            ctg = fund.get('ctg', 'N/A')
            setpDt = fund.get('setpDt', 'N/A')
            fndTp = fund.get('fndTp', 'N/A')
            prdClsfCd = fund.get('prdClsfCd', 'N/A')
            asoStdCd = fund.get('asoStdCd', 'N/A')
            
            fund_parts.append(
                f"{idx}. {name} | "
                f"구분: {ctg} | "
                f"설정일: {setpDt} | "
                f"펀드유형: {fndTp} | "
                f"상품분류코드: {prdClsfCd} | "
                f"협회표준코드: {asoStdCd}"
            )

        return "\n".join(fund_parts)

    @classmethod
    async def recommend_fund(
        cls,
        income_data: Dict[str, int],
        expense_data: Dict[str, int],
        total_income: int,
        total_expense: int,
        surplus: int,
        fund_data: List[Dict],
        investment_goal: str = None,
        risk_tolerance: str = None
    ) -> Dict:
        """
        사용자 재무 정보를 기반으로 Fund 추천
        
        Args:
            income_data: 소득 데이터
            expense_data: 지출 데이터
            total_income: 총 소득
            total_expense: 총 지출
            surplus: 여유 자금
            fund_data: Fund 데이터 목록
            investment_goal: 투자 목표 (선택)
            risk_tolerance: 위험 감수도 (선택)
        
        Returns:
            추천 결과 딕셔너리
        """
        try:
            # 재무 프로필 생성
            financial_profile = cls._build_financial_profile(
                income_data, expense_data, total_income, total_expense, surplus
            )
            
            # Fund 목록 생성
            fund_list = cls._build_fund_list(fund_data)
            
            # AI 프롬프트 작성 (1부)
            prompt_part1 = f"""당신은 전문 재무 상담사입니다. 사용자의 재무 상황을 분석하고 적합한 Fund를 추천해주세요.

## 사용자 재무 정보
{financial_profile}

## 투자 선호도
- 투자 목표: {investment_goal or '명시되지 않음'}
- 위험 감수도: {risk_tolerance or '보통'}

## 분석 가능한 Fund 목록
{fund_list}

---

## 추천 요청사항
다음 형식으로 **정확히 3개의 Fund**를 추천해주세요:

### 1. 재무 분석 요약
- 사용자의 재무 상태를 간단히 분석 (3-4문장)
- 월 투자 가능 금액 추정
- 투자 성향 평가"""
            
            # AI 프롬프트 작성 (2부)
            prompt_part2 = """

### 2. Fund 추천

**[추천 1] Fund명**
- 추천 이유: (2-3문장, 펀드유형, 운용사, 설정일, 구분 등 포함)
- 예상 투자 비중: X%
- 기대 수익률: 연 X%
- 위험도: 낮음/보통/높음
- 투자 전략: (1-2문장, 펀드의 전략적 특성 설명)
- 보수 및 기타 비용: (펀드의 총보수, 판매보수 등)

**[추천 2] Fund명**
- 추천 이유: (2-3문장, 펀드유형, 운용사, 설정일, 구분 등 포함)
- 예상 투자 비중: X%
- 기대 수익률: 연 X%
- 위험도: 낮음/보통/높음
- 투자 전략: (1-2문장, 펀드의 전략적 특성 설명)
- 보수 및 기타 비용: (펀드의 총보수, 판매보수 등)

**[추천 3] Fund명**
- 추천 이유: (2-3문장, 펀드유형, 운용사, 설정일, 구분 등 포함)
- 예상 투자 비중: X%
- 기대 수익률: 연 X%
- 위험도: 낮음/보통/높음
- 투자 전략: (1-2문장, 펀드의 전략적 특성 설명)
- 보수 및 기타 비용: (펀드의 총보수, 판매보수 등)

### 3. 포트폴리오 운용 전략
- 자산 배분 전략 (3-4문장, 펀드의 유형별 배분 전략)
- 리밸런싱 주기 권장
- 추가 고려사항 (운용사, 보수, 구분 등)

### 4. 주의사항
- 투자 시 유의할 점 (2-3가지, 보수, 운용사, 설정일, 구분 등)

---

**중요 규칙:**
1. Fund명은 반드시 제공된 목록에서만 선택
2. 구체적인 수치와 근거 제시
3. 전문적이지만 이해하기 쉬운 설명
4. 과장되지 않은 현실적인 조언
5. 마크다운 형식 사용 금지 (일반 텍스트로만 작성)
"""
            
            prompt = prompt_part1 + prompt_part2
            
            # GPT 호출
            logger.info("Calling GPT for Fund recommendation...")
            recommendation = await cls._call_gpt(prompt)
            
            logger.info(f"Fund recommendation generated (length: {len(recommendation)})")
            
            return {
                "success": True,
                "financial_summary": {
                    "total_income": total_income,
                    "total_expense": total_expense,
                    "surplus": surplus,
                    "saving_rate": round(surplus / total_income * 100, 1) if total_income > 0 else 0,
                },
                "recommendation": recommendation,
                "fund_count": len(fund_data),
                "investment_goal": investment_goal,
                "risk_tolerance": risk_tolerance
            }
            
        except Exception as e:
            logger.error(f"Error in Fund recommendation: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "message": "Fund 추천 중 오류가 발생했습니다."
            }
