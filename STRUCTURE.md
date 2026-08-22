# ELROI FAST FOOD — GitHub folder structure

elroi_fast_food/
├── app.py
├── requirements.txt
├── Procfile
├── render.yaml
├── README.md
├── STRUCTURE.md
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── menu.html
│   ├── product.html
│   ├── checkout.html
│   ├── order_status.html
│   ├── order_not_found.html
│   ├── customer_login.html
│   ├── customer_dashboard.html
│   ├── admin_login.html
│   ├── admin.html
│   ├── product_form.html
│   ├── settings.html
│   ├── scanner.html
│   ├── creator.html
│   └── maintenance.html
└── static/
    ├── css/
    │   └── style.css
    ├── js/
    │   └── app.js
    ├── img/
    │   └── logo.png
    └── uploads/
        └── (admin meal images are uploaded here)

Important:
- `elroi.db` is created automatically on first run and is intentionally not included in the ZIP.
- Set `ADMIN_PASSWORD`, `CREATOR_PASSWORD`, and `SECRET_KEY` in Render Environment Variables.
- Do not store raw card number/CVV/PIN in the dashboard. Configure a secure payment-provider checkout link instead.
