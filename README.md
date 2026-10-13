# Incubation & Startup Success Predictor Analytics — Telegram Survey Bot

A production-ready async Telegram bot that collects 7-step survey data from
university students using Amharic (Ethiopic script) questions, saves responses
to CSV, and sends instant formatted notifications to the admin.

## Tech Stack

- **Python 3.10+**
- **python-telegram-bot v20+** (async/await, `ConversationHandler`)

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure credentials

Open `bot.py` and fill in the two placeholders at the top:

```python
BOT_TOKEN     = "YOUR_BOT_TOKEN_HERE"     # From @BotFather on Telegram
ADMIN_CHAT_ID = "YOUR_ADMIN_CHAT_ID_HERE" # Your personal or group chat ID (integer)
```

> **Finding your ADMIN_CHAT_ID**: Send any message to your bot, then visit
> `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` — the `chat.id`
> field in the JSON response is your chat ID.

### 3. Run

```bash
python bot.py
```

---

## Features

| Feature | Detail |
|---|---|
| **Language** | Amharic (Ethiopic script) questions |
| **Questions** | 7-step sequential `ConversationHandler` |
| **Input types** | Free text (Q1 Dept) + `ReplyKeyboardMarkup` buttons (Q2–Q7) |
| **Data storage** | `survey_responses.csv` (UTF-8 BOM — Excel-compatible) |
| **Admin alert** | Instant Telegram message with all 11 fields on completion |
| **Cancel** | `/cancel` exits at any step and clears the session |
| **Session timeout** | 30-minute idle auto-expiry |
| **Re-entry** | Users can restart mid-survey with `/start` |

---

## CSV Output Schema

| Column | Description |
|---|---|
| `timestamp` | Response submission time |
| `telegram_user_id` | Numeric Telegram user ID |
| `username` | `@username` or `N/A` |
| `full_name` | Telegram display name |
| `department` | Free-text department entry |
| `year` | Academic year (1st–4th or Graduate) |
| `incubation_awareness` | Awareness level of the incubation center |
| `info_source` | How the student learns about opportunities |
| `has_project` | Whether the student has a startup idea |
| `reason_not_submitted` | Reason for not applying to incubation center |
| `skills` | Main skill area |

---

## Conversation Flow

```
/start
  └─► Q1: Department (free text input)
        └─► Q2: Year [1ኛ / 2ኛ / 3ኛ / 4ኛ / Graduate]
              └─► Q3: Incubation Awareness [3 options]
                    └─► Q4: Info Source [4 options]
                          └─► Q5: Has Project [2 options]
                                └─► Q6: Reason Not Submitted [6 options]
                                      └─► Q7: Main Skills [4 options]
                                            └─► Save CSV + Notify Admin + Thank User
```

At any step the user can type `/cancel` to abort and get a clean keyboard-removal response.
