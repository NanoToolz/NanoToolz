/*
  # Add Product Type for Digital Products

  1. Changes to `products` table
    - Add `product_type` column to specify delivery type
    - Types: key, credentials, link, text, file, image
    - Default: 'key' for backwards compatibility

  2. Purpose
    - Supports various digital product formats:
      - key: License keys, activation codes (XXXX-XXXX-XXXX)
      - credentials: Email:password format accounts
      - link: Download links, premium links
      - text: Text content, codes, instructions
      - file: Text files sent as documents
      - image: Images sent directly
*/

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'products' AND column_name = 'product_type'
  ) THEN
    ALTER TABLE products ADD COLUMN product_type text DEFAULT 'key';
  END IF;
END $$;