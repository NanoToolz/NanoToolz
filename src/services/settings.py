"""Settings helpers stored in DB."""

from sqlalchemy.orm import Session

from src.database.models import Setting


def get_setting(db: Session, key: str, default: str | None = None) -> str | None:
    item = db.query(Setting).filter(Setting.key == key).first()
    if item:
        return item.value
    return default


def set_setting(db: Session, key: str, value: str) -> None:
    item = db.query(Setting).filter(Setting.key == key).first()
    if item:
        item.value = value
    else:
        db.add(Setting(key=key, value=value))
    db.commit()
