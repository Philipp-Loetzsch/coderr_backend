# Coderr Backend API

This is the backend API service for the **Coderr** platform, built with Django and Django REST Framework.  
It handles user authentication, profiles, service offers, orders, reviews, and provides base platform statistics.

## !! INFORMATION FOR GUESTLOGIN !!

const GUEST_LOGINS = {
    customer : {
        username: 'CustomerTester',
        password: 'asdasd'
    },
    business : {
        username: 'BusinessTester',
        password: 'asdasd'
    }
}

---

## 📚 Table of Contents

- [Coderr Backend API](#coderr-backend-api)
  - [!! INFORMATION FOR GUESTLOGIN !!](#-information-for-guestlogin-)
  - [📚 Table of Contents](#-table-of-contents)
  - [🛠️ Prerequisites](#️-prerequisites)
  - [⚙️ Setup and Installation](#️-setup-and-installation)
    - [1. Clone the repository](#1-clone-the-repository)
    - [2. Create and activate a virtual environment](#2-create-and-activate-a-virtual-environment)
    - [3. Install dependencies](#3-install-dependencies)
    - [4. Apply database migrations](#4-apply-database-migrations)
    - [5. Create a superuser (optional)](#5-create-a-superuser-optional)
  - [🚀 Running the Development Server](#-running-the-development-server)
  - [🧪 Running Tests](#-running-tests)
  - [🔌 API Endpoints](#-api-endpoints)
    - [🔐 User Authentication (`user_auth_app`)](#-user-authentication-user_auth_app)
    - [👤 Profiles (`profile_app`)](#-profiles-profile_app)
    - [💼 Offers (`offers_app`)](#-offers-offers_app)
    - [📦 Orders (`orders_app`)](#-orders-orders_app)
    - [⭐ Reviews (`reviews_app`)](#-reviews-reviews_app)
    - [📊 Base Info (`base_app`)](#-base-info-base_app)
  - [🧰 Built With](#-built-with)

---

## 🛠️ Prerequisites

- Python (3.9+ recommended)  
- pip (Python package installer)  
- Virtual environment tool (like `venv`)

---

## ⚙️ Setup and Installation

### 1. Clone the repository

```bash
git clone (https://github.com/Philipp-Loetzsch/coderr_backend)
cd coderr_backend
```

### 2. Create and activate a virtual environment

**On macOS/Linux:**
```bash
python3 -m venv env
source env/bin/activate
```

**On Windows:**
```bash
python -m venv env
.\env\Scripts\activate
```

### 3. Install dependencies

Ensure your `requirements.txt` file includes:
- `django`
- `djangorestframework`
- `django-cors-headers`
- `django-filter`
- `pillow`
- `sqlpars`
- `tzdata`


```bash
pip install -r requirements.txt
```

### 4. Apply database migrations

Ensure your database settings are correctly configured in `settings.py`.

```bash
python manage.py migrate
```

### 5. Create a superuser (optional)

```bash
python manage.py createsuperuser
```

---

## 🚀 Running the Development Server

```bash
python manage.py runserver
```

The API will typically be available at `http://127.0.0.1:8000/`.  
Most endpoints are prefixed with `/api/` (configured in `core/urls.py`).

---

## 🧪 Running Tests

Run all tests:

```bash
python manage.py test
```

Run tests for a specific app:

```bash
python manage.py test <app_name>
```

---

## 🔌 API Endpoints

**Base URL:** `/api/`

### 🔐 User Authentication (`user_auth_app`)
- `POST /registration/` — Register a new user (customer/business).  
- `POST /login/` — Login and receive auth token, username, and user ID.  

**Permissions:** `AllowAny`

---

### 👤 Profiles (`profile_app`)
- `GET /profiles/{user_pk}/` — Retrieve a specific user profile.  
- `PATCH /profiles/{user_pk}/` — Update profile (owner only).  
- `GET /profiles/customer/` — List all customer profiles.  
- `GET /profiles/business/` — List all business profiles.  

**Permissions:** `IsAuthenticated`, `IsOwnerOrReadOnly` (where applicable)

---

### 💼 Offers (`offers_app`)
- `GET /offers/` — List offers with filters, search, ordering.  
- `POST /offers/` — Create a new offer (business users only).  
- `GET /offers/{id}/` — Retrieve an offer with details.  
- `PATCH /offers/{id}/` — Update an offer (owner only).  
- `DELETE /offers/{id}/` — Delete an offer (owner only).  
- `GET /offerdetails/{id}/` — Get specific package (basic, standard, premium).  

**Permissions:** Mixed (`AllowAny`, `IsAuthenticated`, `IsOfferOwner`, `IsBusinessUser`)

---

### 📦 Orders (`orders_app`)
- `GET /orders/` — List user’s orders.  
- `POST /orders/` — Create order from an OfferDetail.  
- `GET /orders/{id}/` — Get specific order.  
- `PATCH /orders/{id}/` — Update order status (provider only).  
- `DELETE /orders/{id}/` — Delete order (admin only).  
- `GET /orders/business/{business_user_id}/` — List orders by business user.  
- `GET /completed-order-count/{business_user_id}/` — Get count of completed orders.  
- `GET /order-count/{business_user_id}/` — Get count of in-progress orders.  

**Permissions:** Varies (`IsAuthenticated`, `IsOrderParticipant`, etc.)

---

### ⭐ Reviews (`reviews_app`)
- `GET /reviews/` — List all reviews with filters.  
- `POST /reviews/` — Add review (one per reviewer/target).  
- `GET /reviews/{id}/` — Get review with nested details.  
- `PATCH /reviews/{id}/` — Update review (owner only).  
- `DELETE /reviews/{id}/` — Delete review (owner only).  

**Permissions:** `IsAuthenticated`, `IsReviewOwner`, `IsCustomerUser`

---

### 📊 Base Info (`base_app`)
- `GET /base-info/` — Get platform statistics:
  - Total reviews  
  - Average rating  
  - Business user count  
  - Offer count  

**Permissions:** `AllowAny`

> **Note:** URL parameters like `{user_pk}` or `{id}` refer to dynamic values in the request path.

---

## 🧰 Built With

- [Django](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [django-cors-headers](https://pypi.org/project/django-cors-headers/)
- [django-filter](https://django-filter.readthedocs.io/en/stable/)

