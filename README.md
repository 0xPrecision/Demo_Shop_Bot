<div align="center">

# Demo Shop Bot

![Python](https://img.shields.io/badge/Python-3.13+-blue.svg) ![License](https://img.shields.io/badge/License-MIT-green.svg) ![Status](https://img.shields.io/badge/Status-Active-success.svg)


### A professional Telegram bot template for e-commerce.
#### Launch a fully functional online shop in just a few hours — fully modular, scalable, and ready for integration with payments, CRM, and subscriptions.

</div>

---


<table align="center">
  <tr>
    <td align="center" width="550">
      <img src="assets/admin.gif" width="400" alt="Order placement"/><br/>
      <h4> <b>User panel demo. Order placement</b> </h4>
    </td>
    <td align="center" width="550">
      <img src="assets/user.gif" width="400" alt="Admin panel"/><br/>
      <h4>Admin panel demo. Changing order status</h4>
    </td>
  </tr>
</table>

---

## Project Description

##### **Demo Shop Bot** is a professional online store template based on a Telegram bot, designed for small businesses.  
Built with Python using aiogram 3+, FSM, and SQLite (Tortoise ORM).  
It allows you to launch a fully functional e-commerce project in just a few hours, easily adapts to any client's needs, and scales up to a CRM system or online acquiring.  
Ready for integration with payment services and further feature development.

---


## Features at a Glance

- 🛍 **Catalog & cart** — categories, pagination, inline menus, and dynamic updates  
- 👤 **User profile** — CRUD with edit mode, auto-creation after first purchase  
- 📦 **Order processing** — validation + FSM (all temporary states stored in Redis)  
- ⚡ **Admin panel** — search, edit, view users/orders, CSV export, statistics  
- 🔄 **Reusable utilities** — validation, alerts, navigation, message cleanup  
- 🔒 **Error handling & UX** — back/menu at every step, clear notifications  
- 🗂 **Database** — SQLite + Tortoise ORM with universal CRUD functions  
- 🧩 **Modular architecture** — clean separation of handlers, states, keyboards  
- 🚀 **Scalability** — extend with CRM, online payments, subscriptions, analytics  
- 💾 **Backups** — automatic Redis (dump.rdb) and SQLite backups for data safety  


---


## Project Structure

<details>
<summary>Expand project tree</summary>

```
Demo_Shop_Bot/
├── .venv/
├── assets/
├── backups/
├── bot/
│   ├── handlers/
│   │    ├── admin_handlers/
│   │    │     ├── __init__.py
│   │    │     ├── add_category.py
│   │    │     ├── add_product.py
│   │    │     ├── admin_access.py
│   │    │     ├── admin_catalog.py
│   │    │     ├── admin_common.py
│   │    │     ├── admin_help.py
│   │    │     ├── admin_orders.py
│   │    │     ├── admin_stats.py
│   │    │     ├── delete_product.py
│   │    │     ├── edit_category.py
│   │    │     ├── edit_product.py
│   │    │     ├── search_order.py
│   │    │     └── search_product.py
│   │    ├── user_handlers/
│   │    │     ├── __init__.py
│   │    │     ├── user_cart.py
│   │    │     ├── user_catalog.py
│   │    │     ├── user_checkout.py
│   │    │     ├── user_common.py
│   │    │     ├── user_help.py
│   │    │     ├── user_menu.py
│   │    │     ├── user_orders.py
│   │    │     └── user_profile.py
│   │    └── __init__.py
│   ├── keyboards/
│   │    ├── admin/
│   │    │     ├── __init__.py
│   │    │     ├── admin_menu.py
│   │    │     ├── catalog_keyboards.py
│   │    │     ├── help_keyboard.py
│   │    │     ├── order_keyboards.py
│   │    │     └── stats_kb.py
│   │    └── user/
│   │          ├── __init__.py
│   │          ├── order_keyboards.py
│   │          ├── user_cart_keyboards.py
│   │          ├── user_catalog_keyboards.py
│   │          ├── user_checkout_keyboards.py
│   │          ├── user_common_keyboards.py
│   │          ├── user_main_menu.py
│   │          └── user_profile_keyboards.py
│   ├── states/
│   │    ├── admin_states/
│   │    │     ├── __init__.py
│   │    │     ├── category_states.py
│   │    │     ├── order_states.py
│   │    │     └── product_states.py
│   │    └── user_states/
│   │          ├── __init__.py
│   │          ├── order_states.py
│   │          └── profile_states.py
│   └── utils/
│        ├── admin_utils/
│        │     ├── __init__.py
│        │     ├── catalog_utils.py
│        │     └── order_utils.py
│        ├── user_utils/
│        │     ├── __init__.py
│        │     ├── universal_handlers.py
│        │     ├── user_cart_utils.py
│        │     ├── user_checkout_utils.py
│        │     ├── user_common_utils.py
│        │     ├── user_orders_utils.py
│        │     ├── user_profile_utils.py
│        │     └── validators.py
│        ├── common_utils.py
│        ├── logger.py
│        └── constants.py
├── config_data/
│   ├── __init__.py
│   ├── bot_instance.py
│   └── env.py
├── database/
│   ├── __init__.py
│   ├── config.py
│   ├── crud.py
│   ├── init_db.py
│   └── models.py
├── migrations/
├── services/
│   ├── i18n/
│   │    ├── __init__.py
│   │    ├── middleware.py
│   │    └── translations.py
│   ├── locales/
│   │    ├── en
│   │    │   ├── __init__.py
│   │    │   └── en.json
│   │    ├── ru
│   │    │   ├── __init__.py
│   │    │   └── ru.json
│   │    └── __init__.py
│   ├── __init__.py
│   └── locale_repo.py
├── .env
├── .gitignore
├── dump.rdb
├── LICENSE
├── main.py
├── README.md
├── requirements.txt
└── shop.db
```
</details>

---

## Main Features

- Catalog with categories, product pagination and filtering  
- Cart: add, remove, clear, and view items in one place  
- Automatic user profile creation after the first purchase  
- Autofill contact details from profile when placing an order  
- Order placement with validation and FSM (step-by-step scenarios, all temporary states stored in Redis)  
- CRUD user profile with edit mode  
- Navigation and return to menu/catalog from any step  
- Cleanup of old messages for a clean UX  
- Admin panel: view categories, products and orders, search, edit, statistics, export to CSV  
- Flexible architecture for extension into CRM/ERP and online payment integration  
- **Automatic backup of Redis data (dump.rdb) and SQLite database to preserve orders and profiles**

---

## Prerequisites

- Python 3.13+  
- Redis 6+ (default at `localhost:6379`)  
- SQLite (included by default)

---

## Run & Usage

1. Clone the repository and install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2. Configure parameters in `.env` (bot token, database).  
3. Make sure Redis is running (default: `localhost:6379`).  
4. Initialize the database (created automatically on first run).  
5. Start `main.py`:
    ```bash
    python main.py
    ```
6. Control the bot via Telegram using menus and commands.

---

## Customization Guidelines

- Modify categories, styling, and product structure via the admin panel or the database.  
- For integrating online payments, CRM, and subscriptions use the modular architecture (see README and code comments).  
- Documentation and docstring comments will help quickly adapt the project for a client.  

---

## Scaling & Monetization

- Perfect foundation for freelancers and agencies delivering Telegram-based e-commerce solutions.
- The solution is ready for resale and customization for small and medium-sized businesses.  
- The template can be used as a foundation for developing new e-commerce bots, extended for agency sales, support, and store automation.  

---

## Roadmap

- [ ] Integration with payment providers

- [ ] Docker setup for quick deployment

- [ ] Unit and integration tests


## License

This project is distributed under the standard [LICENSE](LICENSE).

---

## Contacts


- Telegram: [@OxPrecision](https://t.me/OxPrecision)
- Email: wrkfrvr@gmail.com

---

© 2025 Nikita OxPrecision. All rights reserved.



