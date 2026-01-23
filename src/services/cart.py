"""Cart storage backed by the database."""

from sqlalchemy.orm import Session

from src.database.models import CartItem, Product


def get_cart_items(db: Session, user_id: int) -> list[CartItem]:
    return (
        db.query(CartItem)
        .filter(CartItem.user_id == user_id)
        .order_by(CartItem.id.asc())
        .all()
    )


def add_to_cart(db: Session, user_id: int, product_id: int, quantity: int = 1) -> CartItem:
    item = (
        db.query(CartItem)
        .filter(CartItem.user_id == user_id, CartItem.product_id == product_id)
        .first()
    )
    if item:
        item.quantity += quantity
    else:
        item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        db.add(item)
    db.commit()
    return item


def update_quantity(db: Session, item_id: int, delta: int) -> None:
    item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not item:
        return
    item.quantity += delta
    if item.quantity <= 0:
        db.delete(item)
    db.commit()


def remove_item(db: Session, item_id: int) -> None:
    item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()


def clear_cart(db: Session, user_id: int) -> None:
    db.query(CartItem).filter(CartItem.user_id == user_id).delete()
    db.commit()


def get_cart_totals(db: Session, user_id: int) -> tuple[float, float]:
    items = get_cart_items(db, user_id)
    total_usd = 0.0
    total_usdt = 0.0
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            total_usd += float(product.price_usd) * item.quantity
            total_usdt += float(product.price_usdt) * item.quantity
    return total_usd, total_usdt
