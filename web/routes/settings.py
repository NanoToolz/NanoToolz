from html import escape

from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from src.config import settings
from src.database import get_db
from src.database.models import Setting
from web.auth import verify_admin, security
from web.routes.utils import layout

router = APIRouter(prefix="/admin", tags=["admin"])


def fetch_setting(db: Session, key: str, default: str) -> str:
    item = db.query(Setting).filter(Setting.key == key).first()
    return item.value if item else default


def upsert_setting(db: Session, key: str, value: str) -> None:
    item = db.query(Setting).filter(Setting.key == key).first()
    if item:
        item.value = value
    else:
        db.add(Setting(key=key, value=value))


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(credentials=Depends(security), db: Session = Depends(get_db)):
    verify_admin(credentials)
    store_name = fetch_setting(db, "store_name", settings.STORE_NAME)
    support_contact = fetch_setting(db, "support_contact", settings.SUPPORT_CONTACT)
    wallet_tron = fetch_setting(db, "payment_usdt_tron_wallet", settings.PAYMENT_WALLET_TRON)
    wallet_ltc = fetch_setting(db, "payment_ltc_wallet", settings.PAYMENT_WALLET_LTC)
    payment_notice = fetch_setting(db, "payment_notice", "Send the exact amount and tap 'I Paid' after payment.")
    commission_rate = fetch_setting(db, "commission_rate", "10")
    tax_percent = fetch_setting(db, "tax_percent", "0")
    maintenance_mode = fetch_setting(db, "maintenance_mode", "off")

    body = f"""
    <div class=\"section\">
        <h2>Store Settings</h2>
        <form method=\"post\" action=\"/admin/settings/update\">
            <label>Store Name</label>
            <input name=\"store_name\" value=\"{escape(store_name)}\" />
            <label>Support Contact</label>
            <input name=\"support_contact\" value=\"{escape(support_contact)}\" />
            <label>USDT (TRON) Wallet</label>
            <input name=\"wallet_tron\" value=\"{escape(wallet_tron)}\" />
            <label>Litecoin Wallet</label>
            <input name=\"wallet_ltc\" value=\"{escape(wallet_ltc)}\" />
            <label>Payment Notice</label>
            <textarea name=\"payment_notice\">{escape(payment_notice)}</textarea>
            <label>Commission Rate (%)</label>
            <input name=\"commission_rate\" value=\"{escape(commission_rate)}\" />
            <label>Tax Percentage</label>
            <input name=\"tax_percent\" value=\"{escape(tax_percent)}\" />
            <label>Maintenance Mode</label>
            <select name=\"maintenance_mode\">
                <option value=\"off\" {'selected' if maintenance_mode == 'off' else ''}>Off</option>
                <option value=\"on\" {'selected' if maintenance_mode == 'on' else ''}>On</option>
            </select>
            <button class=\"btn btn-primary\" type=\"submit\">Save</button>
        </form>
    </div>
    """

    return layout("Settings", body)


@router.post("/settings/update")
async def settings_update(
    store_name: str = Form("NanoToolz Store"),
    support_contact: str = Form("@YourSupport"),
    wallet_tron: str = Form(""),
    wallet_ltc: str = Form(""),
    payment_notice: str = Form(""),
    commission_rate: str = Form("10"),
    tax_percent: str = Form("0"),
    maintenance_mode: str = Form("off"),
    credentials=Depends(security),
    db: Session = Depends(get_db),
):
    verify_admin(credentials)

    upsert_setting(db, "store_name", store_name)
    upsert_setting(db, "support_contact", support_contact)
    upsert_setting(db, "payment_usdt_tron_wallet", wallet_tron)
    upsert_setting(db, "payment_ltc_wallet", wallet_ltc)
    upsert_setting(db, "payment_notice", payment_notice)
    upsert_setting(db, "commission_rate", commission_rate)
    upsert_setting(db, "tax_percent", tax_percent)
    upsert_setting(db, "maintenance_mode", maintenance_mode)
    db.commit()

    return RedirectResponse("/admin/settings", status_code=303)
