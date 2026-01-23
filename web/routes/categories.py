from html import escape

from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from src.database import get_db
from src.database.models import Category
from web.auth import verify_admin, security
from web.routes.helpers import parse_int
from web.routes.utils import layout

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/categories", response_class=HTMLResponse)
async def categories_page(credentials=Depends(security), db: Session = Depends(get_db)):
    verify_admin(credentials)
    categories = db.query(Category).order_by(Category.display_order.asc()).all()
    body = """
    <div class=\"section\">
        <h2>Add Category</h2>
        <form method=\"post\" action=\"/admin/categories/create\">
            <label>Name</label>
            <input name=\"name\" required />
            <label>Emoji</label>
            <input name=\"emoji\" value=\"📦\" />
            <label>Description</label>
            <textarea name=\"description\"></textarea>
            <label>Display Order</label>
            <input name=\"display_order\" value=\"0\" />
            <label>Featured</label>
            <select name=\"featured\">
                <option value=\"false\">No</option>
                <option value=\"true\">Yes</option>
            </select>
            <button class=\"btn btn-primary\" type=\"submit\">Create</button>
        </form>
    </div>
    <div class=\"section\">
        <h2>Categories</h2>
        <table>
            <thead>
                <tr><th>ID</th><th>Name</th><th>Emoji</th><th>Featured</th><th>Actions</th></tr>
            </thead>
            <tbody>
    """
    for category in categories:
        body += f"""
            <tr>
                <td>{category.id}</td>
                <td>{escape(category.name)}</td>
                <td>{escape(category.emoji or '')}</td>
                <td>{'Yes' if category.featured else 'No'}</td>
                <td>
                    <a class=\"btn btn-secondary\" href=\"/admin/categories/{category.id}\">Edit</a>
                    <form class=\"inline\" method=\"post\" action=\"/admin/categories/{category.id}/delete\">
                        <button class=\"btn btn-danger\" type=\"submit\">Delete</button>
                    </form>
                </td>
            </tr>
        """
    body += """
            </tbody>
        </table>
    </div>
    """
    return layout("Categories", body)


@router.post("/categories/create")
async def create_category(
    name: str = Form(...),
    emoji: str = Form("📦"),
    description: str = Form(""),
    display_order: str = Form("0"),
    featured: str = Form("false"),
    credentials=Depends(security),
    db: Session = Depends(get_db),
):
    verify_admin(credentials)
    category = Category(
        name=name,
        emoji=emoji,
        description=description,
        display_order=parse_int(display_order, 0),
        featured=featured == "true",
    )
    db.add(category)
    db.commit()
    return RedirectResponse("/admin/categories", status_code=303)


@router.get("/categories/{category_id}", response_class=HTMLResponse)
async def category_edit_page(
    category_id: int,
    credentials=Depends(security),
    db: Session = Depends(get_db),
):
    verify_admin(credentials)
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        return layout("Category Not Found", "<p>Category not found.</p>")
    body = f"""
    <div class=\"section\">
        <h2>Edit Category #{category.id}</h2>
        <form method=\"post\" action=\"/admin/categories/{category.id}/update\">
            <label>Name</label>
            <input name=\"name\" value=\"{escape(category.name)}\" required />
            <label>Emoji</label>
            <input name=\"emoji\" value=\"{escape(category.emoji or '')}\" />
            <label>Description</label>
            <textarea name=\"description\">{escape(category.description or '')}</textarea>
            <label>Display Order</label>
            <input name=\"display_order\" value=\"{category.display_order}\" />
            <label>Featured</label>
            <select name=\"featured\">
                <option value=\"false\" {'selected' if not category.featured else ''}>No</option>
                <option value=\"true\" {'selected' if category.featured else ''}>Yes</option>
            </select>
            <button class=\"btn btn-primary\" type=\"submit\">Save</button>
            <a class=\"btn btn-secondary\" href=\"/admin/categories\">Back</a>
        </form>
    </div>
    """
    return layout("Edit Category", body)


@router.post("/categories/{category_id}/update")
async def update_category(
    category_id: int,
    name: str = Form(...),
    emoji: str = Form("📦"),
    description: str = Form(""),
    display_order: str = Form("0"),
    featured: str = Form("false"),
    credentials=Depends(security),
    db: Session = Depends(get_db),
):
    verify_admin(credentials)
    category = db.query(Category).filter(Category.id == category_id).first()
    if category:
        category.name = name
        category.emoji = emoji
        category.description = description
        category.display_order = parse_int(display_order, 0)
        category.featured = featured == "true"
        db.commit()
    return RedirectResponse(f"/admin/categories/{category_id}", status_code=303)


@router.post("/categories/{category_id}/delete")
async def delete_category(
    category_id: int,
    credentials=Depends(security),
    db: Session = Depends(get_db),
):
    verify_admin(credentials)
    category = db.query(Category).filter(Category.id == category_id).first()
    if category:
        db.delete(category)
        db.commit()
    return RedirectResponse("/admin/categories", status_code=303)
