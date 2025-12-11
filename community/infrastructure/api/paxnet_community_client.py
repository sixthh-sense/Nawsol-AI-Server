import aiohttp
from typing import Optional


class PaxnetCommunityClient:
    BASE_URL = "https://www.paxnet.co.kr"

    async def fetch_board_html(
        self,
        board_id: str,
        page: int = 1,
    ) -> str:
        """
        거래소시황, 종목토론실 등 목록 HTML 가져오기
        예: /tbbs/list?id=N00801&tbbsType=L&pageNo=1
        """
        params = {
            "id": board_id,
            "tbbsType": "L",
            "pageNo": str(page),
        }
        url = f"{self.BASE_URL}/tbbs/list"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                resp.raise_for_status()
                return await resp.text()

    async def fetch_post_html(self, board_id: str, seq: str) -> str:
        """
        개별 글 상세 페이지 HTML
        예: /tbbs/view?id=N00801&seq=953466
        """
        params = {
            "id": board_id,
            "seq": str(seq),
        }
        url = f"{self.BASE_URL}/tbbs/view"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                resp.raise_for_status()
                return await resp.text()