# Sai Int Udyog ERP — Starter

A Django web ERP starter for a traditional red clay brick manufacturing and selling business.

## Included in this starter
- Dashboard with production, stock and sales summaries
- Production register with kiln batch details
- Core database models for customers, suppliers, raw materials, purchases, production, stock movements, sales, payments, expenses and double-entry accounting
- Django admin for managing records
- Bootstrap-based responsive interface
- SQLite by default for local development; PostgreSQL via `DATABASE_URL` for production

## Important implementation notes
- Finished brick inventory is stored as **individual bricks**.
- Selling rates are entered **per 1,000 bricks**. Invoice line totals are calculated as `quantity / 1000 * rate_per_1000`.
- Production and stock records are separate concepts. In this starter, production entries record good, damaged and rejected bricks. Stock movement posting should be done through a validated service/transaction in the next phase; do not use direct database edits to correct live inventory.
- GST rates and tax treatment must be configured and confirmed by your accountant. This starter does not hard-code a tax rate or claim GST compliance.
- Accounting models provide the schema foundation; automated journal posting and reconciliation are planned next.

## Run locally (Windows / macOS)
1. Install Python 3.11+.
2. Extract this ZIP and open a terminal in the project directory.
3. Create a virtual environment:
   - Windows: `py -m venv .venv` then `.venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
4. Install packages: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and set a new `SECRET_KEY`.
6. Create database tables: `python manage.py makemigrations core` then `python manage.py migrate`
7. Create an admin login: `python manage.py createsuperuser`
8. Start server: `python manage.py runserver`
9. Open `http://127.0.0.1:8000/` and log in at `http://127.0.0.1:8000/admin/`.

## Project layout
- `config/` — Django settings and URL routing
- `core/` — business models, admin, views and forms
- `templates/` — Bootstrap pages
- `static/` — future local assets

## Next milestones
1. Complete and test forms for purchases, production, sales and payments.
2. Add stock-posting services with atomic transactions and audit trail.
3. Add GST invoice numbering, CGST/SGST/IGST, credit notes and printable invoices.
4. Add journal posting, trial balance, profit & loss, balance sheet and cash/bank reconciliation.
5. Add role permissions, audit logs, backup/restore and deployment hardening.
