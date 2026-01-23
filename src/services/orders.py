"""Order and payment helpers."""

from __future__ import annotations

import uuid
from typing import Iterable

from sqlalchemy.orm import Session

from src.database.models import CartItem, Order, Payment, Product, ProductDelivery, Referral, User


def create_payment_from_cart(
    db: Session,
    user_id: int,
    items: Iterable[CartItem],
    method: str,
    currency: str,
    wallet_to: str,
) -> Payment:
    payment_ref = uuid.uuid4().hex
    total_usd = 0.0
    total_usdt = 0.0

    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            continue

        price_usd = float(product.price_usd) * item.quantity
        price_usdt = float(product.price_usdt) * item.quantity
        total_usd += price_usd
        total_usdt += price_usdt

        order = Order(
            user_id=user_id,
            product_id=product.id,
            quantity=item.quantity,
            price_paid_usd=price_usd,
            price_paid_usdt=price_usdt,
            payment_method=method,
            payment_ref=payment_ref,
            payment_status="pending",
            delivery_status="pending",
        )
        db.add(order)

    amount = total_usdt if currency.upper() == "USDT" else total_usd
    payment = Payment(
        user_id=user_id,
        payment_ref=payment_ref,
        amount=amount,
        currency=currency.upper(),
        method=method,
        wallet_to=wallet_to,
        status="pending",
        confirmations=0,
    )
    db.add(payment)
    db.commit()
    return payment


def complete_payment(db: Session, payment_ref: str) -> list[dict]:
    payment = db.query(Payment).filter(Payment.payment_ref == payment_ref).first()
    if not payment:
        return []

    payment.status = "confirmed"

    deliveries: list[dict] = []
    orders = db.query(Order).filter(Order.payment_ref == payment_ref).all()
    for order in orders:
        product = db.query(Product).filter(Product.id == order.product_id).first()
        if not product:
            continue

        order.payment_status = "completed"

        delivery = (
            db.query(ProductDelivery)
            .filter(ProductDelivery.product_id == product.id, ProductDelivery.used == False)
            .first()
        )
        if delivery:
            delivery.used = True
            order.delivery_status = "sent"
            deliveries.append(
                {
                    "product_name": product.name,
                    "content": delivery.delivery_content,
                }
            )
        else:
            order.delivery_status = "pending"

        product.sales_count += order.quantity
        if product.stock is not None:
            product.stock = max(product.stock - order.quantity, 0)

        user = db.query(User).filter(User.id == order.user_id).first()
        if user and user.referred_by_id:
            commission_rate = float(product.affiliate_commission or 0) / 100
            commission = float(order.price_paid_usd or 0) * commission_rate
            if commission > 0:
                referral = (
                    db.query(Referral)
                    .filter(
                        Referral.referrer_id == user.referred_by_id,
                        Referral.referred_user_id == user.id,
                    )
                    .first()
                )
                if referral:
                    referral.earnings = float(referral.earnings) + commission
                else:
                    db.add(
                        Referral(
                            referrer_id=user.referred_by_id,
                            referred_user_id=user.id,
                            earnings=commission,
                        )
                    )
                referrer = db.query(User).filter(User.id == user.referred_by_id).first()
                if referrer:
                    referrer.credits = float(referrer.credits) + commission

    db.commit()
    return deliveries


def cancel_payment(db: Session, payment_ref: str) -> None:
    payment = db.query(Payment).filter(Payment.payment_ref == payment_ref).first()
    if payment:
        payment.status = "failed"
    orders = db.query(Order).filter(Order.payment_ref == payment_ref).all()
    for order in orders:
        order.payment_status = "failed"
    db.commit()
