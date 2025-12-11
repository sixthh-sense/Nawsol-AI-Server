from fastapi import APIRouter, Query

from community.application.factory.fetch_community_usecase_factory import FetchCommunityUsecaseFactory

community_router = APIRouter(tags=["community"])

@community_router.get("/fetch")
async def get_latest_paxnet_posts(
    board_id: str = Query("N11022", description="Paxnet board id (N11022=시황분석실)"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    usecase = FetchCommunityUsecaseFactory.create()
    posts = await usecase.fetch_latest(board_id=board_id, page=page, limit=limit)

    return {
        "board_id": board_id,
        "count": len(posts),
        "items": [
            {
                "provider": p.provider,
                "external_post_id": p.external_post_id,
                "title": p.title,
                "author": p.author,
                "content": p.content,
                "url": p.url,
                "view_count": p.view_count,
                "recommend_count": p.recommend_count,
                "comment_count": p.comment_count,
                "posted_at": p.posted_at.isoformat() if p.posted_at else None,
                "fetched_at": p.fetched_at.isoformat(),
            }
            for p in posts
        ],
    }


@community_router.post("/latest")
async def fetch_and_save_paxnet_latest(
    board_id: str = Query("N11022"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
):
    usecase = FetchCommunityUsecaseFactory.create()
    posts = await usecase.fetch_and_save_latest(board_id=board_id, page=page, limit=limit)

    return {
        "message": "Paxnet 게시글 크롤링 및 저장 완료",
        "board_id": board_id,
        "saved_count": len(posts),
        "items": [
            {
                "provider": p.provider,
                "external_post_id": p.external_post_id,
                "title": p.title,
                "author": p.author,
                "content": p.content,
                "url": p.url,
                "view_count": p.view_count,
                "recommend_count": p.recommend_count,
                "comment_count": p.comment_count,
                "posted_at": p.posted_at.isoformat() if p.posted_at else None,
                "fetched_at": p.fetched_at.isoformat(),
            }
            for p in posts
        ]
    }