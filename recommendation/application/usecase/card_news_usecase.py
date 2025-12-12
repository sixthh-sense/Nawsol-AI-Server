"""
카드뉴스 추천 UseCase
로그인 여부에 따라 DB 또는 Redis에서 자산 정보를 가져와 카드뉴스 추천
"""
from typing import Dict, List
from datetime import datetime, timedelta

from community.infrastructure.repository.community_repository_impl import CommunityRepositoryImpl
from config.crypto import Crypto
from config.redis_config import get_redis
from ieinfo.infrastructure.repository.ie_info_repository_impl import IEInfoRepositoryImpl
from ieinfo.infrastructure.orm.ie_info import IEType
from news_info.infrastructure.repository.news_info_repository_impl import NewsInfoRepositoryImpl
from recommendation.domain.service.card_news_service import CardNewsService
from util.log.log import Log

logger = Log.get_logger()

class CardNewsRecommendationUseCase:
    """카드 뉴스 추천 UseCase"""

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.ie_repository = IEInfoRepositoryImpl.get_instance()
            self.news_repository = NewsInfoRepositoryImpl.get_instance()
            self.community_repository = CommunityRepositoryImpl.get_instance()
            self.redis_client = get_redis()
            self.crypto = Crypto.get_instance()
            self.initialized = True

    def _get_financial_data_from_db(self, session_id: str, year:int, month:int) -> Dict:
        """DB에서 자산 정보 가져오기 (로그인 사용자)"""
        try:
            # DB에서 데이터 조회
            ie_records = self.ie_repository.get_by_session(session_id, year, month)

            income_data = {}
            expense_data = {}
            total_income = 0
            total_expense = 0

            for record in ie_records:
                if record.ie_type == IEType.INCOME:
                    income_data[record.key] = record.value
                    total_income += record.value
                elif record.ie_type == IEType.EXPENSE:
                    expense_data[record.key] = record.value
                    total_expense += record.value

            surplus = total_income - total_expense

            logger.info(f"Loaded financial data from DB: {len(ie_records)} records")

            return {
                "income_data": income_data,
                "expense_data": expense_data,
                "total_income": total_income,
                "total_expense": total_expense,
                "surplus": surplus,
                "source": "database"
            }

        except Exception as e:
            logger.error(f"Error loading data from DB: {str(e)}")
            return None

    def _get_financial_data_from_redis(self, session_id: str) -> Dict:
        """Redis에서 자산 정보 가져오기 (비로그인 사용자)"""
        try:
            encrypted_data = self.redis_client.hgetall(session_id)

            if not encrypted_data:
                logger.warning(f"No data found in Redis for session: {session_id}")
                return None

            income_data = {}
            expense_data = {}
            total_income = 0
            total_expense = 0

            for key_bytes, value_bytes in encrypted_data.items():
                try:
                    # bytes를 문자열로 변환
                    if isinstance(key_bytes, bytes):
                        key_str = key_bytes.decode('utf-8')
                    else:
                        key_str = str(key_bytes)

                    if isinstance(value_bytes, bytes):
                        value_str = value_bytes.decode('utf-8')
                    else:
                        value_str = str(value_bytes)

                    # USER_TOKEN 제외
                    if key_str == "USER_TOKEN":
                        continue

                    # 복호화
                    key_plain = self.crypto.dec_data(key_str)
                    value_plain = self.crypto.dec_data(value_str)

                    # "타입:필드명" 형태 파싱
                    if ":" not in key_plain:
                        continue

                    doc_type, field_name = key_plain.split(":", 1)
                    value_int = int(value_plain.replace(",", ""))

                    if "소득" in doc_type or "income" in doc_type.lower():
                        income_data[field_name] = value_int
                        total_income += value_int
                    elif "지출" in doc_type or "expense" in doc_type.lower():
                        expense_data[field_name] = value_int
                        total_expense += value_int

                except Exception as e:
                    logger.warning(f"Error processing Redis item: {str(e)}")
                    continue

            surplus = total_income - total_expense

            logger.info(f"Loaded financial data from Redis: income={len(income_data)}, expense={len(expense_data)}")

            return {
                "income_data": income_data,
                "expense_data": expense_data,
                "total_income": total_income,
                "total_expense": total_expense,
                "surplus": surplus,
                "source": "redis"
            }

        except Exception as e:
            logger.error(f"Error loading data from Redis: {str(e)}")
            return None

    async def get_card_news_recommendation(
            self,
            session_id: str,
            year: int = None,
            month: int = None
    ) -> Dict:
        """
        카드 뉴스 추천 메인 메서드

        Args:
            session_id: 사용자 세션 ID
            year: 조회 연도 (DB용, 선택)
            month: 조회 월 (DB용, 선택)

        Returns:
            추천 결과 딕셔너리
        """
        try:
            # 1. 로그인 여부 확인
            user_token = self.redis_client.hget(session_id, "USER_TOKEN")

            if isinstance(user_token, bytes):
                user_token = user_token.decode('utf-8')

            is_logged_in = user_token and user_token != "GUEST"

            logger.info(f"User logged in: {is_logged_in}")

            # 2. 자산 정보 가져오기
            financial_data = None

            if is_logged_in and year and month:
                # 로그인 사용자 - DB에서 조회
                financial_data = self._get_financial_data_from_db(session_id, year, month)
                if not financial_data:
                    # DB에 데이터가 없으면 Redis 시도
                    logger.warning("No data in DB, trying Redis...")
                    financial_data = self._get_financial_data_from_redis(session_id)
            else:
                # 비로그인 사용자 또는 연도/월 미지정 - Redis에서 조회
                financial_data = self._get_financial_data_from_redis(session_id)

            if not financial_data:
                return {
                    "success": False,
                    "message": "자산 정보를 찾을 수 없습니다. 먼저 소득/지출 데이터를 입력해주세요."
                }

            logger.debug(f"financial_data {financial_data}")
            # 3. 뉴스 관련 데이터 가져오기
            news_records = await self.news_repository.get_three_month_news_for_card_news()
            community_records = await self.community_repository.get_three_month_community_for_card_news()

            # 4. news와 커뮤니티 게시글 조합
            news_items = [
                {
                    "type_of_content": "NEWS",
                    "title": n.title,
                    "provider": n.provider.value if hasattr(n.provider, "value") else n.provider,
                    "content": n.description,
                    "link": n.link,
                    "published_at": n.published_at
                }
                for n in news_records
            ]

            # 커뮤니티 → 공통 dict
            community_items = [
                {
                    "type_of_content": "COMMUNITY",
                    "title": c.title,
                    "provider": c.provider,
                    "content": c.content[0:50],
                    "link": c.url,
                    "published_at": c.posted_at
                }
                for c in community_records
            ]

            combined = news_items + community_items

            # published_at / posted_at 없을 경우 대비하여 None 처리 → 신규로 정렬
            sorted_news = sorted(
                combined,
                key=lambda x: x["published_at"] or datetime.max,
                reverse=True
            )

            card_news = []

            print(f"sorted_news = {sorted_news}")
            for idx, item in enumerate(sorted_news, 1):
                card_news.append(
                    f"{idx}. {item['title']} | "
                    f"타입: {item['type_of_content']} | "
                    f"제공자: {item['provider']} | "
                    f"본문: {item['content']} | "
                    f"링크: {item['link']} | "
                )

            # 4. AI 추천 실행
            recommendation_result = await CardNewsService.recommend_card_news(
                income_data=financial_data["income_data"],
                expense_data=financial_data["expense_data"],
                total_income=financial_data["total_income"],
                total_expense=financial_data["total_expense"],
                surplus=financial_data["surplus"],
                community_and_news_data=combined
            )

            logger.debug(f"Recommendation result: {recommendation_result}")

            # 5. 프론트엔드 인터페이스에 맞게 응답 형식 변환
            if recommendation_result.get("success"):

                # 1) 추천 이유(문자열 리포트)
                recommendation_reason = recommendation_result.get("recommendation", "")

                # 2) 프론트로 보낼 추천 카드뉴스 목록을 UseCase에서 직접 생성
                #    -> service 리턴이 구조화된 리스트를 반환하지 않으므로, 여기서 top N(예: 5) 선택
                top_n = 5
                recommended_card_news = []
                for item in sorted_news[:top_n]:
                    recommended_card_news.append({
                        "title": item.get("title"),
                        "type_of_content": item.get("type_of_content"),
                        "provider": item.get("provider"),
                        "content": (item.get("content") or "")[:400],  # 길면 400자 컷
                        "link": item.get("link"),
                        "published_at": item.get("published_at").isoformat() if item.get("published_at") else None
                    })

                # 3) 재무 요약 값 안전하게 꺼내기
                total_income = financial_data.get("total_income", 0) or 0
                total_expense = financial_data.get("total_expense", 0) or 0
                surplus = financial_data.get("surplus", 0) or 0
                surplus_ratio = round(surplus / total_income * 100, 1) if total_income > 0 else 0

                # 저축률 계산
                surplus_ratio = round(financial_data["surplus"] / financial_data["total_income"] * 100, 1) if \
                financial_data["total_income"] > 0 else 0

                return {
                    "success": True,
                    "total_income": total_income,
                    "total_expense": total_expense,
                    "available_amount": surplus,
                    "surplus_ratio": surplus_ratio,
                    "recommendation_reason": recommendation_reason,
                    "recommended_card_news": recommended_card_news,
                    "data_source": financial_data.get("source"),
                    "is_logged_in": is_logged_in
                }
            else:
                return recommendation_result

        except Exception as e:
            logger.error(f"Error in Card recommendation usecase: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": f"CardNews 추천 중 오류가 발생했습니다: {str(e)}"
            }