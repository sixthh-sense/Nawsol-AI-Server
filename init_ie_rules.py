"""
IE_RULE 초기 키워드 데이터 삽입 스크립트
서버 최초 실행 시 한 번만 실행
"""

from config.database.session import get_db_session
from ieinfo.infrastructure.repository.ie_rule_repository_impl import IERuleRepositoryImpl
from ieinfo.infrastructure.orm.ie_info import IEType

# 초기 소득 키워드 (핵심 키워드만)
INITIAL_INCOME_KEYWORDS = [
    "급여", "월급", "연봉", "봉급", "임금",
    "상여", "상여금", "보너스", "성과급", "인센티브",
    "수당", "식대", "교통비", "주거수당",
    "이자", "배당", "배당금", "이자소득"
]

# 초기 지출 키워드 (핵심 키워드만)
INITIAL_EXPENSE_KEYWORDS = [
    "보험료", "국민연금", "건강보험", "고용보험", "산재보험",
    "세금", "소득세", "지방소득세", "주민세",
    "카드", "신용카드", "체크카드", "카드사용액",
    "공제", "공제액", "차감"
]

# 총 소득 키워드
INITIAL_TOTAL_INCOME_KEYWORDS = [
    "총 소득", "총소득", "총수입", "총 수입"
]

# 총 지출 키워드
INITIAL_TOTAL_EXPENSE_KEYWORDS = [
    "총 지출", "총지출", "총 비용", "총비용"
]


def init_ie_rules():
    """IE_RULE 테이블에 초기 키워드 삽입"""
    
    session = get_db_session()
    repo = IERuleRepositoryImpl(session)
    
    print("\n" + "="*80)
    print("🎯 IE_RULE 초기 키워드 삽입 시작")
    print("="*80 + "\n")
    
    # 소득 키워드 삽입
    income_count = 0
    print("📥 소득 키워드 삽입 중...")
    for keyword in INITIAL_INCOME_KEYWORDS:
        if repo.save_keyword(keyword, IEType.INCOME):
            income_count += 1
            print(f"  ✅ {keyword}")
        else:
            print(f"  ⏭️  {keyword} (이미 존재)")
    
    # 지출 키워드 삽입
    expense_count = 0
    print("\n📥 지출 키워드 삽입 중...")
    for keyword in INITIAL_EXPENSE_KEYWORDS:
        if repo.save_keyword(keyword, IEType.EXPENSE):
            expense_count += 1
            print(f"  ✅ {keyword}")
        else:
            print(f"  ⏭️  {keyword} (이미 존재)")
    
    # 총 소득 키워드 삽입
    total_income_count = 0
    print("\n📥 총 소득 키워드 삽입 중...")
    for keyword in INITIAL_TOTAL_INCOME_KEYWORDS:
        if repo.save_keyword(keyword, IEType.TOTAL_INCOME):
            total_income_count += 1
            print(f"  ✅ {keyword}")
        else:
            print(f"  ⏭️  {keyword} (이미 존재)")
    
    # 총 지출 키워드 삽입
    total_expense_count = 0
    print("\n📥 총 지출 키워드 삽입 중...")
    for keyword in INITIAL_TOTAL_EXPENSE_KEYWORDS:
        if repo.save_keyword(keyword, IEType.TOTAL_EXPENSE):
            total_expense_count += 1
            print(f"  ✅ {keyword}")
        else:
            print(f"  ⏭️  {keyword} (이미 존재)")
    
    print("\n" + "="*80)
    print(f"✅ 완료!")
    print(f"   소득: {income_count}개")
    print(f"   지출: {expense_count}개")
    print(f"   총 소득: {total_income_count}개")
    print(f"   총 지출: {total_expense_count}개")
    print("="*80 + "\n")
    
    session.close()


if __name__ == "__main__":
    init_ie_rules()
