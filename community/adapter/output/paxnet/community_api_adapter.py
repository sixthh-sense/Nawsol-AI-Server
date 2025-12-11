import re
from datetime import datetime
from typing import List
import asyncio
from bs4 import BeautifulSoup

from community.domain.value_object.community_post import CommunityPost
from community.infrastructure.api.paxnet_community_client import PaxnetCommunityClient


class PaxnetCommunityAdapter:
    PROVIDER = "PAXNET_COMMUNITY"

    def __init__(self):
        self.client = PaxnetCommunityClient()

    async def fetch_latest(self, board_id: str, page: int = 1, max_posts: int = 20) -> List[CommunityPost]:

        html = await self.client.fetch_board_html(board_id, page)
        soup = BeautifulSoup(html, "html.parser")

        ul = soup.select_one("ul#comm-list")
        if not ul:
            return []

        posts: list[CommunityPost] = []

        for li in ul.find_all("li", recursive=False):
            type_div = li.select_one("div.type")
            if not type_div:
                continue

            seq = type_div.get("data-seq")
            if not seq:
                continue

            external_post_id = seq

            title_a = li.select_one("div.title p.tit a.best-title")
            if not title_a:
                continue

            title = title_a.get_text(strip=True)

            author_tag = li.select_one("div.write a")
            author = author_tag.get_text(strip=True) if author_tag else ""

            view_el = li.select_one("div.viewer")
            view_count = _extract_first_int(view_el.get_text()) if view_el else None

            like_el = li.select_one("div.like")
            recommend_count = _extract_first_int(like_el.get_text()) if like_el else None

            comment_b = li.select_one("b.comment-num")
            comment_count = _extract_first_int(comment_b.get_text()) if comment_b else 0

            date_span = li.select_one("div.date span.data-date-format")
            posted_at = _parse_paxnet_datetime(date_span)

            url = f"https://www.paxnet.co.kr/tbbs/view?id={board_id}&seq={seq}"

            posts.append(
                CommunityPost(
                    provider=self.PROVIDER,
                    board_id=board_id,
                    external_post_id=str(external_post_id),
                    title=title,
                    author=author,
                    content="",  # 상세에서 채움
                    url=url,
                    view_count=view_count,
                    recommend_count=recommend_count,
                    comment_count=comment_count,
                    posted_at=posted_at,
                    fetched_at=datetime.now(),
                )
            )

            if len(posts) >= max_posts:
                break

        await self._fill_contents(board_id, posts)
        return posts

    async def _fill_contents(self, board_id: str, posts: List[CommunityPost]):
        tasks = [
            self.client.fetch_post_html(board_id, p.external_post_id)
            for p in posts
        ]

        html_list = await asyncio.gather(*tasks, return_exceptions=True)

        for post, html in zip(posts, html_list):
            if isinstance(html, Exception):
                post.content = ""
                continue

            post.content = self._extract_body(html)

    @staticmethod
    def _extract_body(html: str) -> str:
        """본문 텍스트 추출"""
        soup = BeautifulSoup(html, "html.parser")

        root = soup.select_one("#bbsWrtCntn")
        if not root:
            return ""

        # script/style 제거
        for t in root(["script", "style"]):
            t.decompose()

        return root.get_text(" ", strip=True)


# ------------------------------------------------------
# 아래는 Adapter가 사용하는 헬퍼 함수들
# ------------------------------------------------------

def _extract_first_int(text: str) -> int | None:
    """문자열 내 첫 번째 숫자를 int로 반환"""
    if not text:
        return None

    m = re.search(r"(\d+)", text.replace(",", ""))
    if not m:
        return None

    try:
        return int(m.group(1))
    except:
        return None


def _parse_paxnet_datetime(span) -> datetime:
    if not span:
        return datetime.now()

    raw = (span.get("data-date-format") or span.get_text(strip=True)).strip()

    # case 1 : "20251211194332"
    if raw.isdigit() and len(raw) == 14:
        return datetime.strptime(raw, "%Y%m%d%H%M%S")

    # case 2 : "Thu Dec 11 21:48:07 KST 2025"
    weekdays = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

    if raw.startswith(weekdays):
        raw2 = raw.replace(" KST", "")
        return datetime.strptime(raw2, "%a %b %d %H:%M:%S %Y")

    # fallback
    return datetime.now()