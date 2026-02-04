/*
  # NanoToolz Bot - Initial Database Schema

  1. New Tables
    - `users` - Telegram users with balance, tier, referral tracking
      - `id` (bigint, primary key) - Telegram user ID
      - `username` (text) - Telegram username
      - `first_name` (text) - User's first name
      - `balance` (decimal) - Account balance
      - `tier` (text) - Loyalty tier (bronze, silver, gold, platinum)
      - `total_spent` (decimal) - Total amount spent
      - `referral_code` (text) - Unique referral code
      - `referred_by` (bigint) - User ID who referred this user
      - `referral_earnings` (decimal) - Total earned from referrals
      - `created_at` (timestamptz) - Registration date

    - `categories` - Product categories
      - `id` (serial, primary key)
      - `name` (text) - Category name
      - `emoji` (text) - Category emoji
      - `description` (text) - Category description
      - `sort_order` (int) - Display order
      - `is_active` (boolean) - Whether category is visible

    - `products` - Product listings
      - `id` (serial, primary key)
      - `category_id` (int) - Foreign key to categories
      - `name` (text) - Product name
      - `description` (text) - Product description
      - `price` (decimal) - Product price
      - `image_url` (text) - Product image URL
      - `is_active` (boolean) - Whether product is available
      - `created_at` (timestamptz)

    - `stock` - Individual stock items (keys, accounts, etc.)
      - `id` (serial, primary key)
      - `product_id` (int) - Foreign key to products
      - `data` (text) - The actual key/account data
      - `is_sold` (boolean) - Whether item is sold
      - `sold_to` (bigint) - User who purchased
      - `sold_at` (timestamptz) - When sold
      - `created_at` (timestamptz)

    - `orders` - Order records
      - `id` (serial, primary key)
      - `user_id` (bigint) - Foreign key to users
      - `total` (decimal) - Order total
      - `status` (text) - pending, completed, cancelled, refunded
      - `payment_method` (text) - How user paid
      - `created_at` (timestamptz)

    - `order_items` - Items within orders
      - `id` (serial, primary key)
      - `order_id` (int) - Foreign key to orders
      - `product_id` (int) - Foreign key to products
      - `stock_id` (int) - Foreign key to stock (the actual item sold)
      - `price` (decimal) - Price at time of purchase
      - `quantity` (int) - Quantity purchased

    - `coupons` - Discount codes
      - `id` (serial, primary key)
      - `code` (text) - Coupon code
      - `discount_percent` (int) - Percentage discount
      - `discount_amount` (decimal) - Fixed amount discount
      - `min_purchase` (decimal) - Minimum purchase amount
      - `max_uses` (int) - Maximum total uses
      - `used_count` (int) - Current use count
      - `expires_at` (timestamptz) - Expiration date
      - `is_active` (boolean)

    - `wishlist` - User wishlists
      - `id` (serial, primary key)
      - `user_id` (bigint) - Foreign key to users
      - `product_id` (int) - Foreign key to products
      - `created_at` (timestamptz)

    - `support_tickets` - Support ticket system
      - `id` (serial, primary key)
      - `user_id` (bigint) - Foreign key to users
      - `subject` (text) - Ticket subject
      - `status` (text) - open, in_progress, resolved, closed
      - `created_at` (timestamptz)
      - `updated_at` (timestamptz)

    - `ticket_messages` - Messages within tickets
      - `id` (serial, primary key)
      - `ticket_id` (int) - Foreign key to support_tickets
      - `user_id` (bigint) - Who sent the message
      - `message` (text) - Message content
      - `is_admin` (boolean) - Whether sent by admin
      - `created_at` (timestamptz)

    - `settings` - Bot configuration
      - `key` (text, primary key)
      - `value` (text)
      - `updated_at` (timestamptz)

  2. Security
    - RLS enabled on all tables
    - Policies for authenticated access (bot uses service role)
*/

-- Users table
CREATE TABLE IF NOT EXISTS users (
  id bigint PRIMARY KEY,
  username text,
  first_name text,
  balance decimal(10,2) DEFAULT 0.00,
  tier text DEFAULT 'bronze',
  total_spent decimal(10,2) DEFAULT 0.00,
  referral_code text UNIQUE,
  referred_by bigint REFERENCES users(id),
  referral_earnings decimal(10,2) DEFAULT 0.00,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access to users"
  ON users
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Categories table
CREATE TABLE IF NOT EXISTS categories (
  id serial PRIMARY KEY,
  name text NOT NULL,
  emoji text DEFAULT '📦',
  description text,
  sort_order int DEFAULT 0,
  is_active boolean DEFAULT true,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE categories ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access to categories"
  ON categories
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Products table
CREATE TABLE IF NOT EXISTS products (
  id serial PRIMARY KEY,
  category_id int REFERENCES categories(id) ON DELETE CASCADE,
  name text NOT NULL,
  description text,
  price decimal(10,2) NOT NULL,
  image_url text,
  is_active boolean DEFAULT true,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE products ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access to products"
  ON products
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Stock table (individual items like keys, accounts)
CREATE TABLE IF NOT EXISTS stock (
  id serial PRIMARY KEY,
  product_id int REFERENCES products(id) ON DELETE CASCADE,
  data text NOT NULL,
  is_sold boolean DEFAULT false,
  sold_to bigint REFERENCES users(id),
  sold_at timestamptz,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE stock ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access to stock"
  ON stock
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
  id serial PRIMARY KEY,
  user_id bigint REFERENCES users(id),
  total decimal(10,2) NOT NULL,
  discount_applied decimal(10,2) DEFAULT 0.00,
  coupon_code text,
  status text DEFAULT 'pending',
  payment_method text DEFAULT 'balance',
  created_at timestamptz DEFAULT now()
);

ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access to orders"
  ON orders
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Order items table
CREATE TABLE IF NOT EXISTS order_items (
  id serial PRIMARY KEY,
  order_id int REFERENCES orders(id) ON DELETE CASCADE,
  product_id int REFERENCES products(id),
  stock_id int REFERENCES stock(id),
  price decimal(10,2) NOT NULL,
  quantity int DEFAULT 1
);

ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access to order_items"
  ON order_items
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Coupons table
CREATE TABLE IF NOT EXISTS coupons (
  id serial PRIMARY KEY,
  code text UNIQUE NOT NULL,
  discount_percent int,
  discount_amount decimal(10,2),
  min_purchase decimal(10,2) DEFAULT 0.00,
  max_uses int,
  used_count int DEFAULT 0,
  expires_at timestamptz,
  is_active boolean DEFAULT true,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE coupons ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access to coupons"
  ON coupons
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Wishlist table
CREATE TABLE IF NOT EXISTS wishlist (
  id serial PRIMARY KEY,
  user_id bigint REFERENCES users(id) ON DELETE CASCADE,
  product_id int REFERENCES products(id) ON DELETE CASCADE,
  created_at timestamptz DEFAULT now(),
  UNIQUE(user_id, product_id)
);

ALTER TABLE wishlist ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access to wishlist"
  ON wishlist
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Support tickets table
CREATE TABLE IF NOT EXISTS support_tickets (
  id serial PRIMARY KEY,
  user_id bigint REFERENCES users(id),
  subject text NOT NULL,
  status text DEFAULT 'open',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE support_tickets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access to support_tickets"
  ON support_tickets
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Ticket messages table
CREATE TABLE IF NOT EXISTS ticket_messages (
  id serial PRIMARY KEY,
  ticket_id int REFERENCES support_tickets(id) ON DELETE CASCADE,
  user_id bigint REFERENCES users(id),
  message text NOT NULL,
  is_admin boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE ticket_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access to ticket_messages"
  ON ticket_messages
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Cart table (persistent cart storage)
CREATE TABLE IF NOT EXISTS cart (
  id serial PRIMARY KEY,
  user_id bigint REFERENCES users(id) ON DELETE CASCADE,
  product_id int REFERENCES products(id) ON DELETE CASCADE,
  quantity int DEFAULT 1,
  created_at timestamptz DEFAULT now(),
  UNIQUE(user_id, product_id)
);

ALTER TABLE cart ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access to cart"
  ON cart
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Settings table
CREATE TABLE IF NOT EXISTS settings (
  key text PRIMARY KEY,
  value text,
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE settings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access to settings"
  ON settings
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Transactions table (balance history)
CREATE TABLE IF NOT EXISTS transactions (
  id serial PRIMARY KEY,
  user_id bigint REFERENCES users(id),
  type text NOT NULL,
  amount decimal(10,2) NOT NULL,
  description text,
  reference_id text,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access to transactions"
  ON transactions
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Insert default settings
INSERT INTO settings (key, value) VALUES
  ('welcome_message', 'Welcome to NanoToolz! Browse our catalog to find what you need.'),
  ('welcome_image', ''),
  ('referral_commission', '10'),
  ('min_withdrawal', '10'),
  ('support_username', ''),
  ('announcement', '')
ON CONFLICT (key) DO NOTHING;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_stock_product ON stock(product_id);
CREATE INDEX IF NOT EXISTS idx_stock_unsold ON stock(product_id) WHERE is_sold = false;
CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_wishlist_user ON wishlist(user_id);
CREATE INDEX IF NOT EXISTS idx_cart_user ON cart(user_id);
CREATE INDEX IF NOT EXISTS idx_tickets_user ON support_tickets(user_id);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON support_tickets(status);
CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id);