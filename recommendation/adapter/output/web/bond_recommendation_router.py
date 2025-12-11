"""
채권 추천 Router
로그인 여부에 따라 DB 또는 Redis 데이터 기반 채권 추천
"""
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from account.adapter.input.web.session_helper import get_current_user
from recommendation.application.usecase.bond_recommendation_usecase import BondRecommendationUseCase
from product.application.factory.fetch_product_data_usecase_factory import FetchProductDataUsecaseFactory
from util.log.log import Log

logger = Log.get_logger()
bond_recommendation_router = APIRouter(tags=["bond_recommendation"])
usecase = BondRecommendationUseCase.get_instance()


@bond_recommendation_router.get("/recommend")
async def get_bond_recommendation(
        year: int = Query(None, description="조회 연도 (로그인 사용자용)"),
        month: int = Query(None, description="조회 월 (로그인 사용자용)"),
        investment_goal: str = Query(None, description="투자 목표 (예: 노후 준비, 단기 수익)"),
        risk_tolerance: str = Query(None, description="위험 감수도 (낮음/보통/높음)"),
        session_id: str = Depends(get_current_user)
):
    """
    사용자 재무 정보를 기반으로 채권 추천

    - 로그인 사용자: DB(IE_INFO)의 데이터 기반 추천
    - 비로그인 사용자: Redis 세션 데이터 기반 추천

    Args:
        year: 조회 연도 (로그인 사용자, 선택)
        month: 조회 월 (로그인 사용자, 선택)
        investment_goal: 투자 목표
        risk_tolerance: 위험 감수도
        session_id: 세션 ID (자동 주입)

    Returns:
        채권 추천 결과
    """
    try:
        # 연도/월이 지정되지 않은 경우 현재 날짜 사용
        if not year:
            year = datetime.now().year
        if not month:
            month = datetime.now().month

        logger.info(
            f"Bond recommendation request - "
            f"session: {session_id[:8]}..., "
            f"year: {year}, month: {month}"
        )

        # 채권 추천 실행
        result = await usecase.get_bond_recommendation(
            session_id=session_id,
            year=year,
            month=month,
            investment_goal=investment_goal,
            risk_tolerance=risk_tolerance
        )

        return result

    except Exception as e:
        logger.error(f"Error in Bond recommendation endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"채권 추천 중 오류가 발생했습니다: {str(e)}"
        }


@bond_recommendation_router.get("/bond-info")
async def get_bond_info(session_id: str = Depends(get_current_user)):
    """
    사용자 맞춤 채권 추천 API
    - 로그인 사용자: DB 소득/지출 기반 추천
    - 비로그인 사용자: Redis 세션 소득/지출 기반 추천
    """
    try:
        # 채권 추천 UseCase 호출
        result = await usecase.get_bond_recommendation(
            session_id=session_id,
            year=datetime.now().year,
            month=datetime.now().month,
            investment_goal=None,
            risk_tolerance=None
        )
        # 기존 프론트엔드 인터페이스에 맞춰 응답 형식 변환
        return {
            "source": "recommendation",
            "fetched_at": datetime.utcnow().isoformat(),
            "total_income": result.get("total_income", 0),
            "total_expense": result.get("total_expense", 0),
            "available_amount": result.get("available_amount", 0),
            "recommendation_reason": result.get("recommendation_reason", ""),
            "items": result.get("recommended_bonds", [])
        }
    except Exception as e:
        logger.error(f"Error in Bond recommendation: {str(e)}")
        # 에러 발생 시 외부 API에서 데이터 가져오기 (fallback)
        try:
            fallback_usecase = FetchProductDataUsecaseFactory.create()
            result = await fallback_usecase.get_bond_data()
            return {
                "source": result.source,
                "fetched_at": result.fetched_at.timestamp.isoformat(),
                "total_income": 0,
                "total_expense": 0,
                "available_amount": 0,
                "recommendation_reason": "소득/지출 정보가 없어 전체 채권 목록을 보여드립니다.",
                "items": [
                    {
                        "crno": bond.crno,
                        "bondIsurNm": bond.bondIsurNm,
                        "bondIssuDt": bond.bondIssuDt,
                        "scrsItmsKcd": bond.scrsItmsKcd,
                        "scrsItmsKcdNm": bond.scrsItmsKcdNm,
                        "isinCd": bond.isinCd,
                        "isinCdNm": bond.isinCdNm,
                        "bondIssuFrmtNm": bond.bondIssuFrmtNm,
                        "bondExprDt": bond.bondExprDt,
                        "bondIssuCurCd": bond.bondIssuCurCd,
                        "bondIssuCurCdNm": bond.bondIssuCurCdNm,
                        "bondPymtAmt": bond.bondPymtAmt,
                        "bondIssuAmt": bond.bondIssuAmt,
                        "bondSrfcInrt": bond.bondSrfcInrt,
                        "irtChngDcd": bond.irtChngDcd,
                        "irtChngDcdNm": bond.irtChngDcdNm,
                        "basDt": bond.basDt.isoformat() if hasattr(bond.basDt, 'isoformat') else str(bond.basDt),
                        "bondIntTcd": bond.bondIntTcd,
                        "bondIntTcdNm": bond.bondIntTcdNm
                    } for bond in result.items
                ]
            }
        except:
            return {
                "source": "error",
                "fetched_at": datetime.utcnow().isoformat(),
                "total_income": 0,
                "total_expense": 0,
                "available_amount": 0,
                "recommendation_reason": "채권 데이터를 불러올 수 없습니다.",
                "items": []
            }

