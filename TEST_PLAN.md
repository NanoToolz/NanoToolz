# NanoToolz Manual Test Plan

## Concurrency Testing
1. **Setup**:
   - Create product with stock=5
   - Prepare 10 test accounts with balance > $50

2. **Test Execution**:
   - Simultaneously have all 10 users add product to cart
   - Have all 10 users start checkout simultaneously
   - Verify only 5 succeed, 5 get stock errors
   - Confirm inventory shows 0 after test

3. **Payment Edge Cases**:
   - Test with insufficient balance:
     - Verify proper error message
     - Confirm cart remains unchanged
   - Test with sufficient balance but stock depletion during payment:
     - Verify stock error message
     - Confirm refund/balance restoration

4. **Admin Security Tests**:
   - Non-admin accessing /admin:
     - Verify access denied
   - Admin permission bypass attempts:
     - Test modified user IDs in URLs
     - Test invalid admin IDs in config

5. **Error Handling Verification**:
   - Force API failures during checkout
   - Verify user-friendly error messages
   - Confirm no sensitive data leaks
