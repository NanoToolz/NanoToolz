# 🚀 NanoToolz Bot - Complete Setup Guide

## 📋 System Architecture

```
GitHub → Push Code
    ↓
GitHub Actions → Auto Deploy
    ↓
Docker Container → Bot Running
    ↓
MongoDB Atlas → Database + Images
    ↓
Telegram → Admin Panel (No Web)
```

---

## 🔧 Setup Steps

### **1. MongoDB Atlas Setup**

```bash
1. Go to: https://cloud.mongodb.com
2. Create free cluster
3. Create database user
4. Whitelist IP: 0.0.0.0/0 (Allow all)
5. Get connection string
```

**Connection String:**
```
mongodb+srv://username:password@cluster.mongodb.net/nanotoolz
```

---

### **2. Environment Variables**

Create `.env` file:

```env
# Bot Token
BOT_TOKEN=your_telegram_bot_token

# Admin IDs (comma-separated)
ADMIN_IDS=123456789,987654321

# MongoDB Atlas
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/nanotoolz
DB_NAME=nanotoolz
```

---

### **3. Docker Setup**

**Build & Run:**
```bash
# Build image
docker-compose build

# Start bot
docker-compose up -d

# View logs
docker-compose logs -f

# Stop bot
docker-compose down

# Restart bot
docker-compose restart
```

---

### **4. GitHub Actions Setup**

**Add Secrets to GitHub:**

1. Go to: `Settings → Secrets → Actions`
2. Add these secrets:
   - `SERVER_HOST` = Your server IP
   - `SERVER_USER` = SSH username
   - `SSH_KEY` = Your private SSH key

**Auto Deploy:**
```
Push to main branch → GitHub Actions → Auto restart bot
```

---

## 📊 Database Structure

### **Collections:**

```javascript
// users
{
  user_id: 123456789,
  username: "john",
  balance: 100.50,
  cart: {},
  created_at: ISODate()
}

// products
{
  _id: ObjectId(),
  name: "Product Name",
  price: 10.99,
  category_id: 1,
  image_id: "gridfs_file_id",
  stock: 50,
  created_at: ISODate()
}

// orders
{
  _id: ObjectId(),
  user_id: 123456789,
  product_id: ObjectId(),
  quantity: 2,
  total: 21.98,
  status: "completed",
  created_at: ISODate()
}

// settings
{
  key: "welcome_message",
  value: "Welcome text...",
  updated_at: ISODate()
}
```

### **GridFS (Images):**
```
fs.files → Image metadata
fs.chunks → Image data (chunks)
```

---

## 🎯 Admin Panel (Telegram Bot)

**All admin operations via Telegram:**

```
/admin → Admin Panel
    ├── 📦 Manage Products
    │   ├── Add Product
    │   ├── Edit Product
    │   ├── Upload Image
    │   └── Add Stock
    ├── 🎨 Customize Welcome
    │   ├── Change Text
    │   └── Change Image
    └── ⚙️ Settings
        ├── View Stats
        └── Manage Admins
```

**No web panel needed!** ✅

---

## 🔄 Workflow

### **User Flow:**
```
1. User: /start
2. Bot: Welcome message + image (from MongoDB)
3. User: Browse products
4. Bot: Show products with images (from GridFS)
5. User: Add to cart
6. User: Checkout
7. Bot: Process payment → Save order to MongoDB
8. Bot: Deliver product keys
```

### **Admin Flow:**
```
1. Admin: /admin
2. Admin: Add Product
3. Admin: Upload product image → Saved to GridFS
4. Admin: Add stock keys → Saved to MongoDB
5. Admin: Customize welcome → Saved to MongoDB
6. Changes reflect immediately for all users
```

### **Deploy Flow:**
```
1. Developer: git push origin main
2. GitHub Actions: Triggered
3. Server: Pull latest code
4. Docker: Rebuild container
5. Bot: Auto restart
6. Users: No downtime (graceful restart)
```

---

## 📝 Commands

### **Docker Commands:**
```bash
# Start bot
docker-compose up -d

# Stop bot
docker-compose down

# Restart bot
docker-compose restart

# View logs
docker-compose logs -f bot

# Rebuild
docker-compose up -d --build
```

### **Manual Deploy:**
```bash
# SSH to server
ssh user@server

# Go to project
cd /home/dev/Telegram\ Bots/NanoToolz

# Pull latest code
git pull origin main

# Restart bot
docker-compose down
docker-compose up -d --build
```

---

## 🔐 Security

### **MongoDB:**
- ✅ Use MongoDB Atlas (managed)
- ✅ Enable authentication
- ✅ Whitelist IPs
- ✅ Use strong passwords

### **Bot:**
- ✅ Keep BOT_TOKEN secret
- ✅ Verify admin IDs
- ✅ Validate user inputs
- ✅ Use environment variables

### **Server:**
- ✅ Use SSH keys (not passwords)
- ✅ Keep server updated
- ✅ Use firewall
- ✅ Monitor logs

---

## 📊 Monitoring

### **Check Bot Status:**
```bash
docker-compose ps
```

### **View Logs:**
```bash
docker-compose logs -f bot
```

### **MongoDB Stats:**
```bash
# Connect to MongoDB
mongosh "mongodb+srv://cluster.mongodb.net/nanotoolz"

# Check collections
show collections

# Count documents
db.users.countDocuments()
db.products.countDocuments()
db.orders.countDocuments()
```

---

## 🚨 Troubleshooting

### **Bot not starting:**
```bash
# Check logs
docker-compose logs bot

# Check environment
docker-compose config

# Rebuild
docker-compose up -d --build
```

### **MongoDB connection failed:**
```bash
# Check connection string
echo $MONGODB_URI

# Test connection
mongosh "your_connection_string"
```

### **GitHub Actions failed:**
```bash
# Check secrets in GitHub
# Check SSH connection
ssh user@server

# Check server disk space
df -h
```

---

## ✅ Checklist

- [ ] MongoDB Atlas cluster created
- [ ] Database user created
- [ ] Connection string added to .env
- [ ] BOT_TOKEN added to .env
- [ ] ADMIN_IDS added to .env
- [ ] Docker installed on server
- [ ] GitHub secrets configured
- [ ] Bot tested locally
- [ ] Bot deployed to server
- [ ] Auto-deploy tested

---

## 🎉 Summary

**System:**
- ✅ MongoDB Atlas (Database + Images)
- ✅ Docker Container (Bot)
- ✅ GitHub Actions (Auto Deploy)
- ✅ Telegram Bot (Admin Panel)

**Features:**
- ✅ Image storage in GridFS
- ✅ Admin panel in Telegram
- ✅ Auto restart on code push
- ✅ No web panel needed
- ✅ Production ready

---

**Everything automated! Push code → Bot restarts! 🚀**
