# Elroi Fast Food — Card Payment Setup

## Important
Do **not** put a bank-card number, CVV, PIN or OTP into the Elroi dashboard.

The website uses a secure payment gateway. The business owner connects the business's Yoco merchant account, and Yoco hosts the card-entry page.

## Admin setup

1. Create/activate a Yoco business account with online payments.
2. Verify the Render website domain with Yoco.
3. Get the Yoco Secret API Key.
4. Log into Elroi Admin.
5. Open **Admin → Settings**.
6. Paste the Yoco Secret API Key.
7. Press **Connect / Register Secure Payments**.
8. The website registers `/api/webhooks/yoco` with Yoco and saves the webhook secret.
9. Test with Yoco test credentials before switching to a live key.

## Customer flow

1. Customer adds meals to the cart.
2. Customer chooses **Pay by card before collection**.
3. Elroi creates a Yoco checkout for the exact order total.
4. Customer is redirected to Yoco's secure payment page.
5. Yoco processes the card and sends a signed webhook to Elroi.
6. Elroi changes the order's payment status to **Paid**.
7. Admin can then move the food order through **Preparing → Almost Done → Collect Now → Completed**.

## Money timing

Card authorization/payment confirmation happens during checkout, but the merchant's bank payout is controlled by the payment provider's payout schedule. The website cannot force a bank to settle funds instantly.
