from config.database.session import SessionLocal
from product.infrastructure.orm.product_bond import ProductBondORM
from scheduler.adapter.bond.bond_api import BondAPI
from scheduler.utils.date_utils import to_datetime_yyyymmdd

class BondService:

    @staticmethod
    def save_bond_info():
        db = SessionLocal()

        try:
            items = BondAPI.fetch_bond_list()

            if not items:
                print("[WARN] API에서 아이템이 없습니다.")
                return

            for item in items:
                record = ProductBondORM(
                    basDt=to_datetime_yyyymmdd(item.get("basDt")),
                    cmo=item.get("crno"),  # 법인등록번호
                    bondlsurNm=item.get("bondIsurNm"),  # 발행인명
                    bondlssuDt=to_datetime_yyyymmdd(item.get("bondIssuDt")),  # 발행일자
                    scrsltmsKod=item.get("scrsItmsKcd"),  # 유가증권종류코드
                    scrsItmsKcdNm=item.get("scrsItmsKcdNm"),  # 유가증권종류코드명
                    isinCd=item.get("isinCd"),  # ISIN 코드
                    isinCdNm=item.get("isinCdNm"),  # ISIN 코드명
                    bondIssuFrmtNm=item.get("bondIssuFrmtNm"),  # 채권발행형태명
                    bondExprDt=to_datetime_yyyymmdd(item.get("bondExprDt")),  # 만기일자
                    bondIssuCurCd=item.get("bondIssuCurCd"),  # 발행통화코드
                    bondIssuCurCdNm=item.get("bondIssuCurCdNm"),  # 발행통화코드명
                    bondPymtAmt=item.get("bondPymtAmt"),  # 납입금액
                    bondIssuAmt=item.get("bondIssuAmt"),  # 발행금액
                    bondSrfcInrt=item.get("bondSrfcInrt"),  # 표면이율
                    irtChngDcd=item.get("irtChngDcd"),  # 금리변동구분 코드
                    irtChngDcdNm=item.get("irtChngDcdNm"),  # 금리변동구분 코드명
                    bondIntTcd=item.get("bondIntTcd"),  # 이자유형 코드
                    bondIntTcdNm=item.get("bondIntTcdNm"),  # 이자유형 코드명
                )
                db.add(record)

            db.commit()
            print(f"[INFO] 채권 정보 {len(items)}건 저장 완료")

        except Exception as e:
            db.rollback()
            print("[ERROR] save_bond_info:", e)

        finally:
            db.close()
