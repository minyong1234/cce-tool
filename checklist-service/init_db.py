# init_db.py
# DB에 점검 항목 초기 데이터를 한 번만 삽입하는 스크립트
# 실행 방법: python init_db.py

from checklist_data import CHECKLIST_ITEMS
from database import engine, SessionLocal
from models.checklist import Base, ChecklistItem

def init():
    # 테이블 생성 (없으면 만들고, 있으면 그대로 둠)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    count = 0
    for item in CHECKLIST_ITEMS:
        # 이미 존재하는 항목은 건너뜀 (중복 삽입 방지)
        exists = db.query(ChecklistItem).filter_by(code=item["code"]).first()
        if not exists:
            db.add(ChecklistItem(**item))
            count += 1
    db.commit()
    db.close()
    print(f"{count}개 항목 신규 삽입 완료 (전체 {len(CHECKLIST_ITEMS)}개)")

if __name__ == "__main__":
    init()
