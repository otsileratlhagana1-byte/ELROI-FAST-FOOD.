# ELROI FAST FOOD — Ordering Website

A mobile-first local fast-food ordering website built from the Elroi Fast Food price poster.

## GitHub / Render
Upload the whole folder to GitHub and create a Render Web Service.

**Build command**
```bash
pip install -r requirements.txt
```

**Start command**
```bash
gunicorn app:app
```

Set these Render environment variables:
- `SECRET_KEY` — long random secret
- `ADMIN_PASSWORD` — private admin password
- `CREATOR_PASSWORD` — private creator password

## Local / Pydroid 3
```bash
pip install -r requirements.txt
python app.py
```
Then open `http://127.0.0.1:5000`.

## Secure online card payments
The website is set up for **Yoco Checkout API**. The admin does **not** enter a bank-card number, CVV or PIN. Instead, the admin connects the business's Yoco merchant account from **Admin → Settings** by entering the Yoco Secret API Key.

When connected:
1. A customer selects **Pay by card before collection**.
2. The website creates a checkout for the exact order amount in ZAR.
3. The customer is redirected to Yoco's secure hosted card page.
4. Yoco sends a signed `payment.succeeded` webhook to the website.
5. The order automatically changes to **Paid** and the admin can continue preparing it.

The payment gateway handles the customer's card data; Elroi does not store raw card details. Yoco requires the merchant to activate online payments and verify the website domain before live keys can be used.

**Important:** a successful card transaction is immediate from the customer's point of view, but the provider's bank payout/settlement timing is controlled by Yoco and is not guaranteed to mean instant bank settlement.

## Fallback payment link
Admin can optionally save a secure Yoco/payment-provider payment link, but the integrated Yoco checkout is preferred because it supports server-side payment confirmation via webhook.

## Main features
- Poster prices converted into online products
- 5-second branded splash/loading screen
- Admin product pictures
- Quantity, additions, removals and notes
- Multi-item cart and checkout
- Cash on collection
- Secure card-before-collection payment
- Delivery marked “Coming Soon”
- Order number + barcode receipt
- Customer order dashboard/login
- Preparing / Almost Done / Collect Now / Completed statuses
- Admin barcode scanner
- Admin product and order management
- Creator maintenance ON/OFF dashboard
- Mobile-first local-business design
