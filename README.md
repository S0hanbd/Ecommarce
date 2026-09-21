# 🛒 Shopcart - Premium E-Commerce Application

A modern, high-performance Django e-commerce platform engineered for speed, clean UX, and seamless online shopping. Built with robust session management, dynamic category filtering, saved wishlists, promo code handling, multi-step checkout, and an admin management dashboard.

---

## 🚀 Key Features & Capabilities

- **Interactive Product Catalog**: Real-time filtering by categories, price ranges, and sorting (Price Low to High, High to Low, Newest, Name).
- **Instant Search**: Dynamic search functionality across titles and descriptions.
- **Session-Based Cart & Wishlist**: Persistent cart and wishlist storage backed by Django sessions for instant user feedback without unnecessary database overhead.
- **Product Showcase & Interactive Gallery**: Image thumbnail swatches, quantity adjustment controls, stock availability indicators, and interactive postal delivery checker.
- **Promo Codes & Discounts**: Integrated coupon code system with automatic percentage-based discount calculation.
- **Checkout & Order Tracking**: Seamless checkout with multiple payment methods (Cash on Delivery, Credit/Debit Card, PayPal) and order receipt summaries.
- **User Authentication**: Built-in User registration, sign-in, session state tracking, and personal order history.
- **Admin Management System**: Pre-configured superuser dashboard to manage products, categories, stock levels, and customer orders.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend Framework** | Python 3.x, Django 5.x |
| **Database** | SQLite3 (Development) |
| **Frontend UI & Styling** | HTML5, Vanilla CSS3 (Custom Design Token System) |
| **Icons & Typography** | FontAwesome 6 Free, Google Fonts (*Plus Jakarta Sans*) |
| **Client-Side Scripting** | Vanilla JavaScript (ES6+) |
| **Version Control** | Git & GitHub |

---

## ⚡ Critical & Core Components

### 1. Session-Backed Shopping Cart (`shop/cart.py`)
- Manages item quantities, prices, override flags, and dynamic total price computations.
- Serializes cart state directly within Django session storage to maintain high performance and low database latency.

### 2. Wishlist System (`shop/wishlist.py`)
- Provides toggle functionality (`toggle()`) for instant item saving and removal.
- Exposes session state across all site components via custom Django Context Processors (`shop/context_processors.py`).

### 3. Dual-Action Form Handling (`templates/shop/product_detail.html`)
- Utilizes HTML5 `formaction` attributes allowing users to seamlessly toggle between **Buy Now** (direct redirect to checkout) and **Add to Cart** (session cart update) within a single unified form structure.

### 4. Custom Database Seeder (`shop/management/commands/seed_data.py`)
- Includes an automated Django CLI command (`python manage.py seed_data`) to automatically populate default superusers (`admin`), category taxonomies, and initial product catalog data.

---

## 📁 Repository Structure

```
TaskAss/
├── manage.py                   # Django CLI entrypoint
├── db.sqlite3                  # Local SQLite database
├── TaskAss/                    # Core project configurations & main routing
│   ├── settings.py
│   ├── urls.py
│   └── views.py                # Main authentication & static page views
├── shop/                       # Main e-commerce app
│   ├── models.py               # Category & Product models
│   ├── views.py                # Product listing, detail, cart, & wishlist logic
│   ├── cart.py                 # Session cart class
│   ├── wishlist.py             # Session wishlist class
│   ├── context_processors.py   # Global template context providers
│   └── management/commands/    # Data seeding scripts
├── orders/                     # Order management app
│   ├── models.py               # Order & OrderItem models
│   ├── forms.py                # Order shipping details form
│   └── views.py                # Checkout, order receipt & history views
├── static/
│   └── css/styles.css          # Design system & styles
└── templates/                  # Modular HTML5 templates
    ├── base.html
    ├── shop/
    ├── orders/
    └── accounts/
```

---

## 🏁 Quick Start & Setup Guide

### 1. Prerequisites
- Python 3.10+ installed
- Virtual environment tool (`venv`)

### 2. Environment Setup
```bash
# Navigate to project directory
cd TaskAss

# Create a virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies & Run Database Migrations
```bash
# Apply migrations
python manage.py migrate

# Seed catalog & create default admin account
python manage.py seed_data
```

### 4. Run Development Server
```bash
python manage.py runserver 8000
```

Open your browser and navigate to:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🔑 Default Credentials

- **Admin Dashboard**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- **Username**: `admin`
- **Password**: `admin123`
