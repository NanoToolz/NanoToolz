# 🤖 NanoToolz Bot

**Super simple Telegram store bot**

---

## 🚀 Quick Start

### 1. Install
```bash
pip install aiogram python-dotenv
```

### 2. Setup
Edit `.env` file:
```
BOT_TOKEN=your_token_here
ADMIN_IDS=123456789
```

### 3. Run
```bash
python simple_bot.py
```

---

## 📁 Files

### **Simple Version (1 File)**
```
simple_bot.py    ← Sab kuch ek file mein!
```

### **Full Version (Organized)**
```
src/bot/features/
├── start.py      ← /start command
├── catalog.py    ← Products
├── cart.py       ← Cart
├── checkout.py   ← Payment
├── profile.py    ← Profile
├── topup.py      ← Topup
├── admin.py      ← Admin
└── ... etc
```

---

## 🎯 Choose Your Version

### **Option 1: Simple (Beginners)**
```bash
python simple_bot.py
```
- ✅ Ek file mein sab kuch
- ✅ Easy to understand
- ✅ Quick to edit

### **Option 2: Full (Advanced)**
```bash
python main.py
```
- ✅ Organized structure
- ✅ Multiple features
- ✅ Production ready

---

## 📝 How to Edit

### **Simple Version:**
```
1. Open: simple_bot.py
2. Find: @router.message(CommandStart())
3. Edit: Welcome message
4. Save & Run: python simple_bot.py
```

### **Full Version:**
```
1. Open: src/bot/features/start.py
2. Find: def get_welcome_text()
3. Edit: Welcome message
4. Save & Run: python main.py
```

---

## 🎓 Learning Path

1. **Start with Simple** → `simple_bot.py`
2. **Understand basics** → How bot works
3. **Move to Full** → `main.py`
4. **Customize** → Edit features

---

## 💡 Simple Bot Features

- ✅ /start command
- ✅ Shop button
- ✅ Cart button
- ✅ Profile button
- ✅ Back button

---

## 🔧 Add More Features

Edit `simple_bot.py`:

```python
# Add new button
[InlineKeyboardButton(text="🎁 New", callback_data="new")]

# Add new handler
@router.callback_query(F.data == "new")
async def new_handler(callback: CallbackQuery):
    await callback.message.edit_text("New feature!")
    await callback.answer()
```

---

## 📊 Comparison

| Feature | Simple | Full |
|---------|--------|------|
| Files | 1 | 20+ |
| Easy to Edit | ✅ | ❌ |
| Organized | ❌ | ✅ |
| For Beginners | ✅ | ❌ |
| Production Ready | ❌ | ✅ |

---

## 🎯 Recommendation

- **Learning?** → Use `simple_bot.py`
- **Production?** → Use `main.py`

---

## 🚨 Troubleshooting

### Bot not starting?
```
1. Check BOT_TOKEN in .env
2. Install: pip install aiogram python-dotenv
3. Run: python simple_bot.py
```

### Changes not working?
```
1. Save file (Ctrl+S)
2. Stop bot (Ctrl+C)
3. Restart: python simple_bot.py
```

---

## ✅ Summary

**Simple Version:**
- 1 file
- Easy to understand
- Perfect for learning

**Full Version:**
- 20+ files
- Organized structure
- Production ready

---

**Choose what works for you! 🚀**
