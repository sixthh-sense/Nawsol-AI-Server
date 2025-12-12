"""
카드뉴스 추천 Router
로그인 여부에 따라 DB 또는 Redis 데이터 기반 ETF 추천
"""
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from account.adapter.input.web.session_helper import get_current_user
from recommendation.application.usecase.card_news_usecase import CardNewsRecommendationUseCase
from util.log.log import Log

logger = Log.get_logger()
card_news_recommendation = APIRouter(tags=["card_news_recommendation"])
usecase = CardNewsRecommendationUseCase.get_instance()


@card_news_recommendation.get("/recommend")
async def get_etf_recommendation(
        year: int = Query(None, description="조회 연도 (로그인 사용자용)"),
        month: int = Query(None, description="조회 월 (로그인 사용자용)"),
        investment_goal: str = Query(None, description="투자 목표 (예: 노후 준비, 단기 수익)"),
        risk_tolerance: str = Query(None, description="위험 감수도 (낮음/보통/높음)"),
        session_id: str = Depends(get_current_user)
):
    """
    사용자 재무 정보를 기반으로 카드뉴스 추천 (소득+지출 정보 필요)

    - 로그인 사용자: DB(IE_INFO)의 데이터 기반 추천
    - 비로그인 사용자: Redis 세션 데이터 기반 추천

    Args:
        year: 조회 연도 (로그인 사용자, 선택)
        month: 조회 월 (로그인 사용자, 선택)
        investment_goal: 투자 목표
        risk_tolerance: 위험 감수도
        session_id: 세션 ID (자동 주입)

    Returns:
        /카드뉴스 추천 결과
    """
    try:
        # 연도/월이 지정되지 않은 경우 현재 날짜 사용
        if not year:
            year = datetime.now().year
        if not month:
            month = datetime.now().month

        logger.info(
            f"CardNews recommendation request - "
            f"session: {session_id[:8]}..., "
            f"year: {year}, month: {month}"
        )

        # ETF 추천 실행
        result = await usecase.get_card_news_recommendation(
            session_id=session_id,
            year=year,
            month=month,
            investment_goal=investment_goal,
            risk_tolerance=risk_tolerance
        )

        # /etf-info와 동일한 형식으로 응답 변환
        if result.get("success"):
            return {
                "source": "recommendation",
                "fetched_at": datetime.utcnow().isoformat(),
                "total_income": result.get("total_income", 0),
                "total_expense": result.get("total_expense", 0),
                "available_amount": result.get("available_amount", 0),
                "surplus_ratio": result.get("surplus_ratio", 0),  # 저축률
                "recommendation_reason": result.get("recommendation_reason", ""),
                "items": result.get("recommended_card_news", [])
            }
        else:
            # 에러 응답도 동일한 형식으로
            return {
                "source": "error",
                "fetched_at": datetime.utcnow().isoformat(),
                "total_income": 0,
                "total_expense": 0,
                "available_amount": 0,
                "surplus_ratio": 0,
                "recommendation_reason": result.get("message", "카드뉴스 추천을 불러오는데 실패했습니다."),
                "items": []
            }

    except Exception as e:
        logger.error(f"Error in ETF recommendation endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "source": "error",
            "fetched_at": datetime.utcnow().isoformat(),
            "total_income": 0,
            "total_expense": 0,
            "available_amount": 0,
            "surplus_ratio": 0,
            "recommendation_reason": f"카드뉴스 추천 중 오류가 발생했습니다: {str(e)}",
            "items": []
        }


@card_news_recommendation.get("/card-news-info")
async def get_etf_info(session_id: str = Depends(get_current_user)):
    """
    사용자 맞춤 카드뉴스 추천 API (Fallback용 - 소득/지출 정보 부족 시)
    - 로그인 사용자: DB 소득/지출 기반 추천
    - 비로그인 사용자: Redis 세션 소득/지출 기반 추천
    """

    try:
        # ETF 추천 UseCase 호출
        result = await usecase.get_card_news_recommendation(
            session_id=session_id,
            year=datetime.now().year,
            month=datetime.now().month,
        )

        # 뉴스 목록을 10개로 제한
        recommended_card_news = result.get("recommended_card_news", [])[:10]

        # 기존 프론트엔드 인터페이스에 맞춰 응답 형식 변환
        return {
            "source": "card_news",  # 구분을 위해 source 변경
            "fetched_at": datetime.utcnow().isoformat(),
            "total_income": result.get("total_income", 0),
            "total_expense": result.get("total_expense", 0),
            "available_amount": result.get("available_amount", 0),
            "surplus_ratio": result.get("surplus_ratio", 0),
            "recommendation_reason": result.get("recommendation_reason", ""),
            "items": recommended_card_news
        }
    except Exception as e:
        logger.error(f"Error in CardNews recommendation: {str(e)}")
        # 에러 발생 시 빈 값 반환 (fallback)
        return {
            "source": "error",
            "fetched_at": datetime.utcnow().isoformat(),
            "total_income": 0,
            "total_expense": 0,
            "available_amount": 0,
            "surplus_ratio": 0,
            "recommendation_reason": "ETF 데이터를 불러올 수 없습니다.",
            "items": []
        }


