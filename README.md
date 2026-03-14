# 🤖 E-Commerce Bot

![Python](https://img.shields.io/badge/python-3.13+-blue?logo=python)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)
![Platform](https://img.shields.io/badge/platform-Telegram-blue?logo=telegram)

**Инструменты разработки:**  
![Black](https://img.shields.io/badge/code%20style-black-000000) 
![isort](https://img.shields.io/badge/imports-isort-orange) 
![Ruff](https://img.shields.io/badge/linter-ruff-red)

---

### Шаблон интернет-магазина на базе Telegram-бота

Это готовый фундамент для e-commerce, который можно адаптировать под свой проект без сборки всего с нуля.
Он построен на модульной архитектуре, поддерживает несколько языков (i18n) и легко расширяется интеграциями с оплатой, CRM и подписками.

---

<table align="center">
  <tr>
    <td align="center" width="550">
      <img src="assets/admin.gif" width="400" alt="Оформление заказа"/><br/>
      <h4> <b>Демонстрация панели пользователя. Оформление заказа</b> </h4>
    </td>
    <td align="center" width="550">
      <img src="assets/user.gif" width="400" alt="Панель администратора"/><br/>
      <h4>Демонстрация панели администратора. Изменение статуса заказа</h4>
    </td>
  </tr>
</table>

---

## Описание проекта

##### **Demo Shop Bot** — это готовая база для запуска интернет-магазина в Telegram с возможностью адаптации под задачи малого бизнеса.
Создан на Python с использованием aiogram 3+, FSM и SQLite (Tortoise ORM).  
Позволяет запустить полностью рабочий e-commerce проект всего за несколько часов, легко адаптируется под задачи любого клиента и масштабируется до CRM-системы или онлайн-эквайринга.  
Готов к интеграции с платёжными сервисами и дальнейшему развитию функциональности.

---


## Ключевые возможности

- 🛍 **Каталог и корзина** — категории, пагинация, inline-меню и динамические обновления  
- 👤 **Профиль пользователя** — CRUD с режимом редактирования, автоматическое создание профиля после первой покупки  
- 📦 **Обработка заказов** — валидация + FSM (все временные состояния хранятся в Redis)  
- ⚡ **Админ-панель** — поиск, редактирование, просмотр пользователей/заказов, экспорт CSV, статистика  
- 🔄 **Переиспользуемые утилиты** — валидация, уведомления, навигация, очистка сообщений  
- 🔒 **Обработка ошибок и UX** — кнопки назад/в главное меню на каждом шаге, понятные уведомления  
- 🗂 **База данных** — SQLite + Tortoise ORM с универсальными CRUD-функциями  
- 🧩 **Модульная архитектура** — чёткое разделение handlers, states, keyboards  
- 🚀 **Масштабируемость** — расширение до CRM, онлайн-платежей, подписок, аналитики  
- 💾 **Резервные копии** — автоматические бэкапы Redis (dump.rdb) и SQLite для хранения данных  


---


## Структура проекта

<details>
<summary>Развернуть дерево проекта</summary>

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
├── logging_config.py
├── main.py
├── pyproject.toml
├── README.md
├── requirements.txt
└── shop.db
```
</details>

---

## Основные возможности

- Каталог с категориями, пагинацией товаров и фильтрацией  
- Корзина: добавление, удаление, очистка и просмотр товаров в одном месте  
- Автоматическое создание профиля пользователя после первой покупки  
- Автозаполнение контактных данных из профиля при оформлении заказа
- Встроенная многоязычность (i18n на базе JSON-словарей + middleware)
- Оформление заказа с валидацией и FSM (пошаговые сценарии, все временные состояния хранятся в Redis)  
- CRUD-профиль пользователя с режимом редактирования  
- Навигация и возврат в меню/каталог с любого шага  
- Очистка старых сообщений для аккуратного UX  
- Админ-панель: просмотр категорий, товаров и заказов, поиск, редактирование, статистика, экспорт в CSV  
- Гибкая архитектура для расширения до CRM/ERP и интеграции онлайн-платежей  
- **Автоматическое резервное копирование данных Redis (dump.rdb) и базы SQLite для сохранения заказов и профилей**

---

## Что понадобится

- Python 3.13+  
- Redis 6+ (по умолчанию `localhost:6379`)  
- SQLite (входит по умолчанию)

---

## Запуск и использование

1. Клонируйте репозиторий и установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```
2. Настройте параметры в `.env` (токен бота, база данных).  
3. Убедитесь, что Redis запущен (по умолчанию: `localhost:6379`).  
4. Инициализируйте базу данных (она создаётся автоматически при первом запуске).  
5. Запустите `main.py`:
    ```bash
    python main.py
    ```
6. Управляйте ботом через Telegram с помощью меню и команд.

---

## Рекомендации по кастомизации

- Изменяйте категории, оформление и структуру товаров через админ-панель или базу данных.  
- Для интеграции онлайн-платежей, CRM и подписок используйте модульную архитектуру (см. README и комментарии в коде).  
- Документация и комментарии в docstring помогут быстро адаптировать проект под клиента.
- Проект полностью готов к интернационализации (i18n). Вы можете расширять переводы, редактируя JSON-словари в /services/locales.

---

## Масштабирование и монетизация

- Отличная основа для фрилансеров и агентств, которые делают Telegram-решения для e-commerce.
- Решение готово к перепродаже и кастомизации для малого и среднего бизнеса.  
- Шаблон можно использовать как базу для разработки новых e-commerce ботов, расширения агентских продаж, поддержки и автоматизации магазинов.  

---

## Дорожная карта

- [ ] Интеграция с платёжными провайдерами

- [ ] Настройка Docker для быстрого развёртывания

- [ ] Unit- и integration-тесты


## Лицензия

Этот проект распространяется по стандартной [LICENSE](LICENSE).

---

## Контакты

- Telegram: [@OxPrecision](https://t.me/OxPrecision)
- Email: wrkfrvr@gmail.com

---

© 2025 Nikita OxPrecision. All rights reserved.