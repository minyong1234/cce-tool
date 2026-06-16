# init_db.py
# DB에 점검 항목 데이터를 upsert (있으면 UPDATE, 없으면 INSERT)
# 실행 방법: python init_db.py

from checklist_data import CHECKLIST_ITEMS
from database import engine, SessionLocal
from models.checklist import Base, ChecklistItem

def init():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # sort_order 컬럼 없으면 추가 (기존 DB 마이그레이션)
    try:
        from sqlalchemy import text
        db.execute(text("ALTER TABLE checklist_items ADD COLUMN IF NOT EXISTS sort_order INTEGER NOT NULL DEFAULT 0"))
        db.commit()
    except Exception:
        db.rollback()

    inserted = 0
    updated  = 0

    for idx, item in enumerate(CHECKLIST_ITEMS):
        exists = db.query(ChecklistItem).filter_by(code=item["code"]).first()
        if exists:
            changed = False
            for field in ["title", "category", "severity", "standard", "target", "check_method"]:
                if getattr(exists, field) != item.get(field):
                    setattr(exists, field, item[field])
                    changed = True
            # sort_order 항상 갱신
            if exists.sort_order != idx:
                exists.sort_order = idx
                changed = True
            if changed:
                updated += 1
        else:
            db.add(ChecklistItem(**item, sort_order=idx))
            inserted += 1

    # checklist_data에 없는 항목 제거
    current_codes = {item["code"] for item in CHECKLIST_ITEMS}
    deleted = 0
    for row in db.query(ChecklistItem).all():
        if row.code not in current_codes:
            db.delete(row)
            deleted += 1

    db.commit()
    db.close()
    print(f"완료: 신규 {inserted}개 삽입 / {updated}개 업데이트 / {deleted}개 삭제 (전체 {len(CHECKLIST_ITEMS)}개)")

if __name__ == "__main__":
    init()
