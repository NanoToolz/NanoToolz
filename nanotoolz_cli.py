#!/usr/bin/env python3
import os, sys, json, termios, tty
from datetime import datetime

import importlib.util
spec = importlib.util.spec_from_file_location("json_db", "/home/dev/Telegram Bots/NanoToolz/src/database/json_db.py")
json_db_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(json_db_module)
db = json_db_module.db

class C:
    B = '\033[94m'
    G = '\033[92m'
    Y = '\033[93m'
    R = '\033[91m'
    C = '\033[96m'
    W = '\033[97m'
    X = '\033[0m'
    BD = '\033[1m'

def clear(): os.system('clear')

def get_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            sys.stdin.read(1)
            ch = sys.stdin.read(1)
            return ch
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def menu(title, msg, btns):
    sel = 0
    while True:
        clear()
        print(f"\n{C.B}{C.BD}{'='*50}\n{title}\n{'='*50}{C.X}\n")
        print(f"{C.W}{msg}{C.X}\n")
        print(f"{C.Y}{'-'*50}{C.X}")
        for i, (a, t) in enumerate(btns):
            print(f"{C.G}{C.BD}> {t}{C.X}" if i == sel else f"  {t}")
        print(f"{C.Y}{'-'*50}{C.X}\n")
        
        k = get_key()
        if k == 'A': sel = (sel - 1) % len(btns)
        elif k == 'B': sel = (sel + 1) % len(btns)
        elif k == '\r': return btns[sel][0]

class CLI:
    def __init__(self):
        self.uid = 123456789
        self.cart = db.get_user(self.uid).get("cart", {})
    
    def welcome(self):
        user = db.get_user(self.uid)
        bal = user.get('balance', 0)
        orders = len([o for o in db.orders if o.get('user_id') == self.uid])
        
        clear()
        print(f"\n{C.B}{C.BD}{'='*50}")
        print(f"Welcome to NanoToolz!")
        print(f"{'='*50}{C.X}\n")
        
        print(f"{C.C}{C.BD}Your Account:{C.X}")
        print(f"  User ID: {C.Y}{self.uid}{C.X}")
        print(f"  Balance: {C.G}${bal:.2f}{C.X}")
        print(f"  Orders: {C.G}{orders}{C.X}")
        print(f"  Joined: {C.Y}{user.get('joined_at', 'Today')}{C.X}\n")
        
        print(f"{C.C}{C.BD}Store Info:{C.X}")
        print(f"  Products: {C.G}{len(db.products)}{C.X}")
        print(f"  Categories: {C.G}{len(db.get_categories())}{C.X}")
        print(f"  Status: {C.G}Online{C.X}\n")
        
        print(f"{C.Y}{'-'*50}{C.X}")
        input(f"{C.Y}Press Enter to continue...{C.X}")
    
    def main(self):
        self.welcome()
        while True:
            c = menu("NanoToolz", "Main Menu", [
                ("cat", "Browse Catalog"),
                ("cart", "View Cart"),
                ("topup", "Topup Balance"),
                ("prof", "Profile"),
                ("admin", "Admin"),
                ("exit", "Exit")
            ])
            
            if c == "cat": self.catalog()
            elif c == "cart": self.view_cart()
            elif c == "topup": self.topup()
            elif c == "prof": self.profile()
            elif c == "admin": self.admin()
            elif c == "exit": 
                print(f"\n{C.G}Bye!{C.X}\n")
                sys.exit(0)
    
    def catalog(self):
        cats = db.get_categories()
        btns = [(str(i), c['name']) for i, c in enumerate(cats)] + [("back", "Back")]
        c = menu("Catalog", "Select Category", btns)
        
        if c == "back": return
        cat = cats[int(c)]
        self.products(cat['id'], cat['name'])
    
    def products(self, cid, cname):
        prods = db.get_products(category_id=cid)
        if not prods:
            print(f"{C.R}No products{C.X}")
            input()
            self.catalog()
            return
        
        btns = [(str(i), f"{p['name']} - ${p['price']}") for i, p in enumerate(prods)] + [("back", "Back")]
        c = menu(f"Category: {cname}", "Select Product", btns)
        
        if c == "back": self.catalog()
        else: self.product(prods[int(c)])
    
    def product(self, p):
        stock = db.get_stock_count(p['id'])
        msg = f"Name: {p['name']}\nPrice: ${p['price']}\nStock: {stock}\nDesc: {p.get('description', 'N/A')}"
        
        c = menu(f"Product: {p['name']}", msg, [
            ("add", "Add to Cart"),
            ("back", "Back")
        ])
        
        if c == "add":
            if stock > 0:
                pid = str(p['id'])
                self.cart[pid] = self.cart.get(pid, 0) + 1
                db.update_user(self.uid, {"cart": self.cart})
                print(f"\n{C.G}Added!{C.X}")
                input()
                self.catalog()
            else:
                print(f"\n{C.R}Out of stock{C.X}")
                input()
                self.product(p)
        else: self.catalog()
    
    def view_cart(self):
        self.cart = db.get_user(self.uid).get("cart", {})
        
        if not self.cart:
            print(f"\n{C.R}Cart empty{C.X}")
            input()
            self.main()
            return
        
        total = 0
        msg = "Items:\n\n"
        items = []
        
        for pid, qty in self.cart.items():
            p = db.get_product(int(pid))
            if p:
                sub = p['price'] * qty
                total += sub
                items.append((pid, p, qty))
                msg += f"{p['name']}: {qty} x ${p['price']} = ${sub:.2f}\n"
        
        msg += f"\nTotal: ${total:.2f}"
        
        btns = [(str(i), f"Modify {it[1]['name']}") for i, it in enumerate(items)]
        btns.extend([("checkout", "Checkout"), ("back", "Back")])
        
        c = menu("Cart", msg, btns)
        
        if c == "back": self.main()
        elif c == "checkout": self.checkout(total)
        else: self.modify_item(items[int(c)])
    
    def modify_item(self, item):
        pid, p, qty = item
        c = menu("Modify", f"{p['name']}\nQty: {qty}", [
            ("inc", "Increase"),
            ("dec", "Decrease"),
            ("rem", "Remove"),
            ("back", "Back")
        ])
        
        if c == "inc": self.cart[pid] = qty + 1
        elif c == "dec": self.cart[pid] = qty - 1 if qty > 1 else 0
        elif c == "rem": del self.cart[pid]
        elif c == "back": self.view_cart(); return
        
        if self.cart[pid] == 0: del self.cart[pid]
        db.update_user(self.uid, {"cart": self.cart})
        print(f"\n{C.G}Updated!{C.X}")
        input()
        self.view_cart()
    
    def checkout(self, total):
        c = menu("Checkout", f"Total: ${total:.2f}", [
            ("balance", "Pay with Balance"),
            ("crypto", "Crypto"),
            ("card", "Card"),
            ("back", "Cancel")
        ])
        
        if c == "back": self.view_cart()
        elif c == "balance":
            user = db.get_user(self.uid)
            bal = user.get("balance", 0)
            
            if bal >= total:
                order = {
                    "id": len(db.orders) + 1,
                    "user_id": self.uid,
                    "total": total,
                    "timestamp": datetime.now().isoformat(),
                    "status": "completed",
                    "items": self.cart.copy(),
                    "keys_delivered": []
                }
                db.create_order(order)
                db.update_user(self.uid, {"balance": bal - total, "cart": {}})
                self.cart = {}
                print(f"\n{C.G}Order #{order['id']} placed!{C.X}")
                input()
                self.main()
            else:
                print(f"\n{C.R}Insufficient balance{C.X}")
                input()
                self.checkout(total)
        else:
            print(f"\n{C.G}Payment link generated{C.X}")
            input()
            self.checkout(total)
    
    def topup(self):
        user = db.get_user(self.uid)
        bal = user.get("balance", 0)
        
        c = menu("Topup", f"Balance: ${bal:.2f}", [
            ("10", "Add $10"),
            ("25", "Add $25"),
            ("50", "Add $50"),
            ("100", "Add $100"),
            ("back", "Back")
        ])
        
        if c == "back": self.main()
        elif c in ["10", "25", "50", "100"]:
            amt = int(c)
            db.update_user(self.uid, {"balance": bal + amt})
            print(f"\n{C.G}Added ${amt}!{C.X}")
            input()
            self.main()
    
    def profile(self):
        user = db.get_user(self.uid)
        orders = [o for o in db.orders if o.get('user_id') == self.uid]
        
        msg = f"ID: {self.uid}\nBalance: ${user.get('balance', 0):.2f}\nOrders: {len(orders)}"
        
        c = menu("Profile", msg, [
            ("history", "Order History"),
            ("topup", "Topup"),
            ("back", "Back")
        ])
        
        if c == "history":
            if not orders:
                print(f"\n{C.R}No orders{C.X}")
                input()
                self.profile()
            else:
                msg = "Orders:\n\n"
                for o in sorted(orders, key=lambda x: x.get('timestamp', ''), reverse=True)[:5]:
                    msg += f"#{o['id']}: ${o.get('total', 0):.2f}\n"
                menu("History", msg, [("back", "Back")])
                self.profile()
        elif c == "topup": self.topup()
        elif c == "back": self.main()
    
    def admin(self):
        c = menu("Admin", "Admin Panel", [
            ("prod", "Products"),
            ("stats", "Stats"),
            ("stock", "Stock"),
            ("back", "Back")
        ])
        
        if c == "prod":
            msg = "Products:\n\n"
            for i, p in enumerate(db.products, 1):
                msg += f"{i}. {p['name']} - ${p['price']}\n"
            menu("Products", msg, [("back", "Back")])
            self.admin()
        elif c == "stats":
            rev = sum(o.get('total', 0) for o in db.orders)
            msg = f"Users: {len(db.users)}\nProducts: {len(db.products)}\nOrders: {len(db.orders)}\nRevenue: ${rev:.2f}"
            menu("Stats", msg, [("back", "Back")])
            self.admin()
        elif c == "stock":
            msg = "Stock:\n\n"
            for pid, items in db.stock.items():
                p = db.get_product(int(pid))
                if p: msg += f"{p['name']}: {len(items)}\n"
            menu("Stock", msg, [("back", "Back")])
            self.admin()
        elif c == "back": self.main()

if __name__ == "__main__":
    try:
        CLI().main()
    except KeyboardInterrupt:
        print(f"\n{C.R}Interrupted{C.X}\n")
        sys.exit(0)
