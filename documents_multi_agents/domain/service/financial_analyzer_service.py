import json
import os
import re
import traceback
from typing import Dict, Any

from dotenv import load_dotenv
from openai import OpenAI

from util.cache.ai_cache import AICache
from util.log.log import Log
from documents_multi_agents.domain.service.hybrid_parser import HybridParser

load_dotenv()
logger = Log.get_logger()
log_util = Log()


class FinancialAnalyzerService:
    """
    Redis에서 복호화된 재무 데이터를 AI로 분석하고 카테고리별로 분류하는 서비스
    """

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    @staticmethod
    def _fix_json_string(json_str: str) -> str:
        """
        잘못된 JSON 문자열을 수정
        """
        # 1. 마지막 항목의 쉼표 제거
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)

        # 2. 연속된 쉼표 제거
        json_str = re.sub(r',\s*,', ',', json_str)

        # 3. 콜론 뒤에 쉼표가 바로 오는 경우 수정
        json_str = re.sub(r':\s*,', ': null,', json_str)

        return json_str

    @staticmethod
    def _clean_item_names(data: Dict) -> Dict:
        """
        항목명의 언더스코어를 띄어쓰기로 변환하고 데이터 정리
        """
        if not isinstance(data, dict):
            return data

        cleaned = {}
        for key, value in data.items():
            # 키의 언더스코어를 띄어쓰기로 변환
            clean_key = key.replace("_", " ")

            if isinstance(value, dict):
                # 중첩된 딕셔너리도 재귀적으로 처리
                cleaned[clean_key] = FinancialAnalyzerService._clean_item_names(value)
            else:
                cleaned[clean_key] = value

        return cleaned

    @log_util.logging_decorator
    def categorize_financial_data(self, decrypted_data: Dict[str, str]) -> Dict[str, Any]:
        """
        복호화된 재무 데이터를 AI로 분석하여 카테고리별로 분류
        
        Args:
            decrypted_data: 복호화된 데이터 {"소득:급여": "3000000", "지출:식비": "500000", ...}
            
        Returns:
            카테고리별로 분류된 데이터
        """
        # 소득/지출 분리
        income_items = {}
        expense_items = {}

        for key, value in decrypted_data.items():
            if key == "USER_TOKEN":
                continue

            # "타입:항목" 형태에서 분리
            if ":" in key:
                doc_type, field = key.split(":", 1)

                if "소득" in doc_type or "income" in doc_type.lower():
                    income_items[field] = value
                elif "지출" in doc_type or "expense" in doc_type.lower():
                    expense_items[field] = value

        # AI로 각각 분석
        categorized_income = self._categorize_income(income_items) if income_items else {}
        categorized_expense = self._categorize_expense(expense_items) if expense_items else {}

        # 종합 분석 및 추천
        recommendations = self._generate_recommendations(categorized_income, categorized_expense)

        return {
            "income": categorized_income,
            "expense": categorized_expense,
            "recommendations": recommendations,
            "summary": self._generate_summary(categorized_income, categorized_expense)
        }

    @log_util.logging_decorator
    def _categorize_income(self, income_items: Dict[str, str]) -> Dict[str, Any]:
        """소득을 카테고리별로 분류"""
        if not income_items:
            return {}

        # 🔥 캐시 키 생성 (데이터 기반)
        data_str = json.dumps(income_items, ensure_ascii=False, sort_keys=True)
        cache_key = AICache.generate_cache_key(data_str, "categorize-income")
        
        # 🔥 캐시 확인
        cached_response = AICache.get_cached_response(cache_key)
        if cached_response:
            try:
                logger.info("[CACHE HIT] 소득 분류 캐시 사용")
                return json.loads(cached_response)
            except json.JSONDecodeError:
                logger.warning("[CACHE] Failed to parse cached income data, re-analyzing")

        # ============================================
        # 🆕 하이브리드 파싱 (규칙 기반 우선)
        # ============================================
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 [HYBRID PARSING START] 소득 항목 분류 시작 ({len(income_items)}개 항목)")
        logger.info(f"{'='*80}")
        
        try:
            hybrid_parser = HybridParser()  # ✏️ confidence_threshold 제거
        except Exception as e:
            logger.error(f"❌ [HYBRID PARSER] 초기화 실패: {str(e)}")
            logger.error(f"   스택: {traceback.format_exc()}")
            # 폴백: GPT만 사용
            hybrid_parser = None
        
        confident_items = {}  # 규칙 기반 성공
        uncertain_items = {}  # GPT 필요
        
        if hybrid_parser:
            for field_name, value in income_items.items():
                try:
                    trans_type, category, metadata = hybrid_parser.classify_item(
                        field_name, 
                        value, 
                        doc_type_hint='소득'
                    )
                    
                    if metadata['method'] == 'rule_based':
                        # ✅ 규칙 기반 성공
                        confident_items[field_name] = value
                    else:
                        # ⚠️ GPT 필요
                        uncertain_items[field_name] = value
                except Exception as e:
                    logger.warning(f"⚠️  [PARSE ERROR] '{field_name}' 파싱 실패: {str(e)}")
                    uncertain_items[field_name] = value
            
            # 📊 통계 출력
            try:
                stats = hybrid_parser.get_statistics()
                logger.info(f"\n📊 [PARSING STATS]")
                logger.info(f"   전체: {stats['total_items']}개")
                logger.info(f"   ✅ DB 규칙 성공: {stats['db_rule_success']}개 ({stats['db_rule_rate']*100:.1f}%)")
                logger.info(f"   ⚠️  GPT 필요: {stats['gpt_fallback']}개 ({stats['gpt_fallback_rate']*100:.1f}%)")
                logger.info(f"   💰 비용 절감률: {stats['cost_saving_rate']*100:.1f}%")
                logger.info(f"   🎓 새로 학습: {stats['new_keywords_learned']}개")
            except Exception as e:
                logger.warning(f"⚠️  통계 출력 실패: {str(e)}")
        else:
            # HybridParser 실패 시 모든 항목을 GPT로
            logger.warning("⚠️  HybridParser를 사용할 수 없습니다. 모든 항목을 GPT로 처리합니다.")
            uncertain_items = income_items.copy()
        
        # ============================================
        # GPT로 전체 재분석 (불확실한 항목 포함)
        # ============================================
        if uncertain_items:
            logger.warning(f"\n⚠️  [{len(uncertain_items)}개 항목] GPT로 재분석 필요:")
            for field in uncertain_items.keys():
                logger.warning(f"   - {field}")
            logger.info(f"\n🤖 [GPT PARSING] 전체 항목을 GPT로 분석합니다...")
        else:
            logger.info(f"\n✅ [100% DB-RULE] 모든 항목을 규칙 기반으로 처리했습니다!")
            logger.info(f"🤖 [GPT PARSING] 정확도 향상을 위해 GPT로 카테고리 분류를 진행합니다...")

        # 기존 GPT 프롬프트 사용 (전체 항목)
        prompt = f"""
다음 소득 항목들을 분석하여 아래 카테고리로 정확하게 분류해줘:

소득 항목:
{json.dumps(income_items, ensure_ascii=False, indent=2)}

**엄격한 분류 기준:**

1. 고정소득: 매월 일정하게 들어오는 소득
   - 급여, 월급, 연봉
   - 식대 (고정)
   - 정기 수당

2. 변동소득: 불규칙적으로 들어오는 소득
   - 상여금, 보너스, 성과급
   - 수당 (변동)
   - 야근수당, 연장근로수당

3. 기타소득: 부가 수입
   - 이자소득, 배당소득
   - 임대소득
   - 프리랜서 수입

**절대 규칙:**
1. 항목명의 언더스코어(_)를 띄어쓰기로 변경
2. 원본 금액을 그대로 사용 (숫자 타입)
3. 빈 객체 절대 사용 금지
4. JSON 문법 엄수: 마지막 항목 뒤에 쉼표 없음, 모든 괄호 정확히 닫기

**응답 형식 (반드시 이 형식을 정확히 따를 것):**

```json
{{
  "고정소득": {{
    "급여": 3000000,
    "식대": 200000
  }},
  "변동소득": {{
    "상여": 1000000
  }},
  "기타소득": {{
    "이자": 50000
  }},
  "카테고리별 합계": {{
    "고정소득": 3200000,
    "변동소득": 1000000,
    "기타소득": 50000
  }},
  "총소득": 4250000
}}
```

중요: 위 형식을 정확히 따라야 합니다. JSON 코드블록(```)은 제외하고 순수 JSON만 반환하세요.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0,
                seed=12345
            )

            result_text = response.choices[0].message.content.strip()

            # JSON 추출
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            # JSON 수정 (잘못된 문법 자동 수정)
            result_text = self._fix_json_string(result_text)

            # JSON 파싱 시도
            try:
                result = json.loads(result_text)
                # 언더스코어를 띄어쓰기로 변환
                cleaned_result = self._clean_item_names(result)
                
                # 🎓 GPT 학습: 불확실했던 항목들을 DB에 저장
                if uncertain_items:
                    self._learn_from_gpt_income(uncertain_items, cleaned_result)
                
                # ✅ GPT 분석 완료 로깅
                logger.info(f"\n✅ [GPT COMPLETED] 소득 분류 완료")
                logger.info(f"{'='*80}\n")
                
                # 🔥 캐시 저장 (24시간)
                AICache.set_cached_response(cache_key, json.dumps(cleaned_result, ensure_ascii=False), ttl=86400)
                
                return cleaned_result
            except json.JSONDecodeError as json_err:
                logger.error(f"[ERROR] JSON parsing failed: {json_err}")
                logger.error(f"[ERROR] Raw response text: {result_text}")
                # JSON 파싱 실패 시 원본 데이터 반환
                return {
                    "error": f"AI 응답을 파싱할 수 없습니다: {str(json_err)}",
                    "raw_items": income_items,
                    "고정소득": {},
                    "변동소득": {},
                    "기타소득": {},
                    "카테고리별 합계": {
                        "고정소득": 0,
                        "변동소득": 0,
                        "기타소득": 0
                    },
                    "총소득": sum(int(v) for v in income_items.values() if v.isdigit())
                }
        except Exception as e:
            logger.error(f"[ERROR] Income categorization failed: {str(e)}")
            return {
                "error": str(e),
                "raw_items": income_items,
                "고정소득": {},
                "변동소득": {},
                "기타소득": {},
                "카테고리별 합계": {
                    "고정소득": 0,
                    "변동소득": 0,
                    "기타소득": 0
                },
                "총소득": sum(int(v) for v in income_items.values() if v.isdigit())
            }

    @log_util.logging_decorator
    def _categorize_expense(self, expense_items: Dict[str, str]) -> Dict[str, Any]:
        """지출을 카테고리별로 분류"""
        if not expense_items:
            return {}

        # 🔥 캐시 키 생성 (데이터 기반)
        data_str = json.dumps(expense_items, ensure_ascii=False, sort_keys=True)
        cache_key = AICache.generate_cache_key(data_str, "categorize-expense")
        
        # 🔥 캐시 확인
        cached_response = AICache.get_cached_response(cache_key)
        if cached_response:
            try:
                logger.info("[CACHE HIT] 지출 분류 캐시 사용")
                return json.loads(cached_response)
            except json.JSONDecodeError:
                logger.warning("[CACHE] Failed to parse cached expense data, re-analyzing")

        # ============================================
        # 🆕 하이브리드 파싱 (규칙 기반 우선)
        # ============================================
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 [HYBRID PARSING START] 지출 항목 분류 시작 ({len(expense_items)}개 항목)")
        logger.info(f"{'='*80}")
        
        try:
            hybrid_parser = HybridParser()  # ✏️ confidence_threshold 제거
        except Exception as e:
            logger.error(f"❌ [HYBRID PARSER] 초기화 실패: {str(e)}")
            logger.error(f"   스택: {traceback.format_exc()}")
            # 폴백: GPT만 사용
            hybrid_parser = None
        
        confident_items = {}  # 규칙 기반 성공
        uncertain_items = {}  # GPT 필요
        
        if hybrid_parser:
            for field_name, value in expense_items.items():
                try:
                    trans_type, category, metadata = hybrid_parser.classify_item(
                        field_name, 
                        value, 
                        doc_type_hint='지출'
                    )
                    
                    if metadata['method'] == 'rule_based':
                        # ✅ 규칙 기반 성공
                        confident_items[field_name] = value
                    else:
                        # ⚠️ GPT 필요
                        uncertain_items[field_name] = value
                except Exception as e:
                    logger.warning(f"⚠️  [PARSE ERROR] '{field_name}' 파싱 실패: {str(e)}")
                    uncertain_items[field_name] = value
            
            # 📊 통계 출력
            try:
                stats = hybrid_parser.get_statistics()
                logger.info(f"\n📊 [PARSING STATS]")
                logger.info(f"   전체: {stats['total_items']}개")
                logger.info(f"   ✅ DB 규칙 성공: {stats['db_rule_success']}개 ({stats['db_rule_rate']*100:.1f}%)")
                logger.info(f"   ⚠️  GPT 필요: {stats['gpt_fallback']}개 ({stats['gpt_fallback_rate']*100:.1f}%)")
                logger.info(f"   💰 비용 절감률: {stats['cost_saving_rate']*100:.1f}%")
                logger.info(f"   🎓 새로 학습: {stats['new_keywords_learned']}개")
            except Exception as e:
                logger.warning(f"⚠️  통계 출력 실패: {str(e)}")
        else:
            # HybridParser 실패 시 모든 항목을 GPT로
            logger.warning("⚠️  HybridParser를 사용할 수 없습니다. 모든 항목을 GPT로 처리합니다.")
            uncertain_items = expense_items.copy()
        
        # ============================================
        # GPT로 전체 재분석 (불확실한 항목 포함)
        # ============================================
        if uncertain_items:
            logger.warning(f"\n⚠️  [{len(uncertain_items)}개 항목] GPT로 재분석 필요:")
            for field in uncertain_items.keys():
                logger.warning(f"   - {field}")
            logger.info(f"\n🤖 [GPT PARSING] 전체 항목을 GPT로 분석합니다...")
        else:
            logger.info(f"\n✅ [100% DB-RULE] 모든 항목을 규칙 기반으로 처리했습니다!")
            logger.info(f"🤖 [GPT PARSING] 정확도 향상을 위해 GPT로 카테고리 분류를 진행합니다...")


        # 기존 GPT 프롬프트 사용
        prompt = f"""
다음 지출 항목들을 분석하여 아래 카테고리로 정확하게 분류해줘:

지출 항목:
{json.dumps(expense_items, ensure_ascii=False, indent=2)}

**엄격한 분류 기준:**

1. 고정지출 (매달 일정하게 나가는 고정 금액):
   - 월세, 관리비, 주택담보대출
   - 통신비 (휴대폰, 인터넷, TV)
   - 보험료 (건강보험, 자동차보험, 생명보험, 실손보험 등 모든 보험)
   - 구독료 (넷플릭스, 멜론 등)
   - 교통비 정기권
   - 학원비, 등록금 (정기 납부)
   
2. 변동지출 (매달 금액이 달라지는 지출):
   - 식비, 외식비, 배달음식
   - 쇼핑 (의류, 잡화, 화장품)
   - 문화생활 (영화, 공연, 취미)
   - 교통비 (택시, 주유비, 대중교통)
   - 의료비
   - 카드 사용액 (전통시장, 일반 카드 사용)
   
3. 저축 및 투자:
   - 적금, 예금, 청약저축
   - 주식, 펀드, 채권
   - 연금저축
   - 대출 원금 상환
   
4. 기타 및 예비비 (일회성 또는 분류 애매한 지출):
   - 병원비 (큰 치료비)
   - 경조사비
   - 선물비
   - 수리비
   - 일회성 지출

**절대 규칙:**
1. 모든 보험료는 반드시 "고정지출"에 포함
2. 카드 사용액은 "변동지출"에 포함
3. 항목명의 언더스코어(_)를 띄어쓰기로 변경
4. 원본 금액을 그대로 사용 (숫자 타입)
5. 빈 객체 절대 사용 금지
6. JSON 문법 엄수: 마지막 항목 뒤에 쉼표 없음, 모든 괄호 정확히 닫기

**응답 형식 (반드시 이 형식을 정확히 따를 것):**

```json
{{
  "고정지출": {{
    "월세": 1000000,
    "국민연금보험료 총합계": 675000
  }},
  "변동지출": {{
    "식비": 300000,
    "카드 전통시장 합계": 120000
  }},
  "저축 및 투자": {{
    "적금": 500000
  }},
  "기타 및 예비비": {{
    "경조사비": 100000
  }},
  "카테고리별 합계": {{
    "고정지출": 1675000,
    "변동지출": 420000,
    "저축 및 투자": 500000,
    "기타 및 예비비": 100000
  }},
  "총지출": 2695000
}}
```

중요: 위 형식을 정확히 따라야 합니다. JSON 코드블록(```)은 제외하고 순수 JSON만 반환하세요.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0,
                seed=12345
            )

            result_text = response.choices[0].message.content.strip()

            # JSON 추출
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            # JSON 수정 (잘못된 문법 자동 수정)
            result_text = self._fix_json_string(result_text)

            # JSON 파싱 시도
            try:
                result = json.loads(result_text)
                # 언더스코어를 띄어쓰기로 변환
                cleaned_result = self._clean_item_names(result)
                
                # 🎓 GPT 학습: 불확실했던 항목들을 DB에 저장
                if uncertain_items:
                    self._learn_from_gpt_expense(uncertain_items, cleaned_result)
                
                # ✅ GPT 분석 완료 로깅
                logger.info(f"\n✅ [GPT COMPLETED] 지출 분류 완료")
                logger.info(f"{'='*80}\n")
                
                # 🔥 캐시 저장 (24시간)
                AICache.set_cached_response(cache_key, json.dumps(cleaned_result, ensure_ascii=False), ttl=86400)
                
                return cleaned_result
            except json.JSONDecodeError as json_err:
                logger.error(f"[ERROR] JSON parsing failed: {json_err}")
                logger.error(f"[ERROR] Raw response text: {result_text}")
                # JSON 파싱 실패 시 원본 데이터 반환
                return {
                    "error": f"AI 응답을 파싱할 수 없습니다: {str(json_err)}",
                    "raw_items": expense_items,
                    "고정지출": {},
                    "변동지출": {},
                    "저축 및 투자": {},
                    "기타 및 예비비": {},
                    "카테고리별 합계": {
                        "고정지출": 0,
                        "변동지출": 0,
                        "저축 및 투자": 0,
                        "기타 및 예비비": 0
                    },
                    "총지출": sum(int(v) for v in expense_items.values() if v.isdigit())
                }
        except Exception as e:
            logger.error(f"[ERROR] Expense categorization failed: {str(e)}")
            return {
                "error": str(e),
                "raw_items": expense_items,
                "고정지출": {},
                "변동지출": {},
                "저축 및 투자": {},
                "기타 및 예비비": {},
                "카테고리별 합계": {
                    "고정지출": 0,
                    "변동지출": 0,
                    "저축 및 투자": 0,
                    "기타 및 예비비": 0
                },
                "총지출": sum(int(v) for v in expense_items.values() if v.isdigit())
            }

    @log_util.logging_decorator
    def _generate_recommendations(self, income_data: Dict, expense_data: Dict, use_ai: bool = False) -> Dict[str, Any]:
        """소득/지출 데이터를 기반으로 자산 분배 추천
        
        Args:
            income_data: 소득 데이터
            expense_data: 지출 데이터
            use_ai: True이면 GPT 사용, False이면 규칙 기반 사용 (기본값: False)
        """
        if not income_data or not expense_data:
            return {"message": "소득 또는 지출 데이터가 부족합니다"}

        # 🔥 규칙 기반 추천 (기본값)
        if not use_ai:
            from asset_allocation.domain.service.rule_based_allocation_service import RuleBasedAllocationService
            rule_service = RuleBasedAllocationService()
            return rule_service.generate_recommendation(income_data, expense_data, risk_profile="balanced")

        # 🔥 AI 기반 추천 (use_ai=True일 때만)
        # 안전한 타입 변환
        try:
            total_income = int(income_data.get("total_income", 0)) if income_data.get("total_income") else 0
        except (ValueError, TypeError):
            total_income = 0

        try:
            total_expense = int(expense_data.get("total_expense", 0)) if expense_data.get("total_expense") else 0
        except (ValueError, TypeError):
            total_expense = 0

        prompt = f"""
당신은 전문 재무설계사입니다. 다음 데이터를 분석하여 자산 분배를 추천해주세요.

소득 분석:
{json.dumps(income_data, ensure_ascii=False, indent=2)}

지출 분석:
{json.dumps(expense_data, ensure_ascii=False, indent=2)}

다음 항목들을 포함하여 분석해주세요:

1. 재무 건전성 평가
   - 소득 대비 지출 비율
   - 필수지출 비율
   - 선택지출 비율
   - 저축/투자 비율

2. 자산 분배 추천 (월 가처분소득 기준)
   - 비상자금: X원 (Y%)
   - 단기저축: X원 (Y%)
   - 장기투자: X원 (Y%)
   - 보험: X원 (Y%)
   - 기타: X원 (Y%)

3. 개선 제안 (우선순위 순)
   - 줄일 수 있는 지출 항목
   - 늘려야 할 항목
   - 구체적인 실행 방법

4. 목표별 저축 계획
   - 단기 목표 (1년 이내)
   - 중기 목표 (1-5년)
   - 장기 목표 (5년 이상)

반드시 다음 JSON 형식으로만 답변해:
{{
  "health_score": {{
    "overall": 0-100점,
    "income_to_expense_ratio": 비율,
    "essential_expense_ratio": 비율,
    "savings_ratio": 비율,
    "comment": "평가 코멘트"
  }},
  "asset_allocation": {{
    "emergency_fund": {{"amount": 금액, "percentage": 비율, "reason": "이유"}},
    "short_term_savings": {{"amount": 금액, "percentage": 비율, "reason": "이유"}},
    "long_term_investment": {{"amount": 금액, "percentage": 비율, "reason": "이유"}},
    "insurance": {{"amount": 금액, "percentage": 비율, "reason": "이유"}},
    "other": {{"amount": 금액, "percentage": 비율, "reason": "이유"}}
  }},
  "improvement_suggestions": [
    {{"priority": 1, "category": "카테고리", "action": "구체적 행동", "expected_saving": 예상절감액}},
    {{"priority": 2, "category": "카테고리", "action": "구체적 행동", "expected_saving": 예상절감액}}
  ],
  "savings_goals": {{
    "short_term": {{"target": "목표", "amount": 금액, "months": 개월}},
    "medium_term": {{"target": "목표", "amount": 금액, "months": 개월}},
    "long_term": {{"target": "목표", "amount": 금액, "months": 개월}}
  }}
}}
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2500,
                temperature=0,  # 일관성을 위해 0으로 변경
                seed=12345  # 동일한 입력에 대해 일관된 결과 보장
            )

            result_text = response.choices[0].message.content.strip()
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            return json.loads(result_text)
        except Exception as e:
            logger.error(f"[ERROR] Recommendation generation failed: {str(e)}")
            return {"error": str(e)}

    @log_util.logging_decorator
    def _generate_summary(self, income_data: Dict, expense_data: Dict) -> Dict[str, Any]:
        """전체 재무 상황 요약"""
        # 안전한 타입 변환 - 한글 키 우선, 없으면 영문 키
        try:
            total_income = int(income_data.get("총소득") or income_data.get("total_income", 0)) if (
                        income_data.get("총소득") or income_data.get("total_income")) else 0
        except (ValueError, TypeError):
            total_income = 0

        try:
            total_expense = int(expense_data.get("총지출") or expense_data.get("total_expense", 0)) if (
                        expense_data.get("총지출") or expense_data.get("total_expense")) else 0
        except (ValueError, TypeError):
            total_expense = 0

        surplus = total_income - total_expense
        surplus_ratio = (surplus / total_income * 100) if total_income > 0 else 0

        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "surplus": surplus,
            "surplus_ratio": round(surplus_ratio, 2),
            "status": "흑자" if surplus > 0 else "적자" if surplus < 0 else "수지균형"
        }
    
    def _learn_from_gpt_income(self, uncertain_items: Dict[str, str], gpt_result: Dict):
        """
        GPT가 분류한 소득 항목을 DB에 학습
        
        Args:
            uncertain_items: 규칙 기반으로 처리 못한 항목들
            gpt_result: GPT 분석 결과
        """
        try:
            from documents_multi_agents.domain.service.hybrid_parser import HybridParser
            
            learner = HybridParser()
            
            # GPT 결과에서 각 항목이 어느 카테고리에 속하는지 확인
            for field_name in uncertain_items.keys():
                # 모든 카테고리에서 해당 항목 찾기
                found = False
                for category_name, items in gpt_result.items():
                    if category_name in ['카테고리별 합계', '총소득', 'total_income', 'error', 'raw_items']:
                        continue
                    
                    if isinstance(items, dict) and field_name in items:
                        # 이 항목은 소득으로 분류됨
                        learner.learn_from_gpt_result(field_name, 'income')
                        found = True
                        break
                
                if not found:
                    logger.debug(f"[LEARN] 항목 '{field_name}'을 GPT 결과에서 찾을 수 없음")
        
        except Exception as e:
            logger.error(f"[LEARN] 소득 학습 오류: {str(e)}")
    
    def _learn_from_gpt_expense(self, uncertain_items: Dict[str, str], gpt_result: Dict):
        """
        GPT가 분류한 지출 항목을 DB에 학습
        
        Args:
            uncertain_items: 규칙 기반으로 처리 못한 항목들
            gpt_result: GPT 분석 결과
        """
        try:
            from documents_multi_agents.domain.service.hybrid_parser import HybridParser
            
            learner = HybridParser()
            
            # GPT 결과에서 각 항목이 어느 카테고리에 속하는지 확인
            for field_name in uncertain_items.keys():
                # 모든 카테고리에서 해당 항목 찾기
                found = False
                for category_name, items in gpt_result.items():
                    if category_name in ['카테고리별 합계', '총지출', 'total_expense', 'error', 'raw_items']:
                        continue
                    
                    if isinstance(items, dict) and field_name in items:
                        # 이 항목은 지출로 분류됨
                        learner.learn_from_gpt_result(field_name, 'expense')
                        found = True
                        break
                
                if not found:
                    logger.debug(f"[LEARN] 항목 '{field_name}'을 GPT 결과에서 찾을 수 없음")
        
        except Exception as e:
            logger.error(f"[LEARN] 지출 학습 오류: {str(e)}")
