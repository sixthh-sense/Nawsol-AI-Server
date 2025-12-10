from dotenv import load_dotenv

load_dotenv()

from datetime import datetime, timedelta
import requests
import os

class BondAPI:

    @staticmethod
    def fetch_bond_list(days=30):
        service_key = os.getenv("FUND_SERVICE_KEY")
        url = "https://apis.data.go.kr/1160100/service/GetBondTradInfoService/getIssuIssuItemStat"

        all_items = []

        today = datetime.today()

        # 최근 30일 내의 채권 정보 수집
        for i in range(days):
            target_date = today - timedelta(days=i)
            basDt = target_date.strftime("%Y%m%d")

            params = {
                "serviceKey": service_key,
                "resultType": "json",
                "basDt": basDt
            }

            print(f"[INFO] 요청 basDt={basDt}")

            res = requests.get(url, params=params)

            if res.status_code != 200:
                print(f"[WARN] {basDt} 요청 실패: {res.status_code}")
                continue

            try:
                data = res.json()
                items = data["response"]["body"]["items"].get("item", [])

                if items:
                    print(f"[INFO] {basDt} 데이터 {len(items)}건")
                    all_items.extend(items)

            except Exception as e:
                print(f"[ERROR] JSON 파싱 실패 ({basDt}):", e)
                continue

        print(f"[INFO] 총 수집된 채권 데이터: {len(all_items)}건")
        return all_items
