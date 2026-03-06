# Hotel & Staycation AI Chatbot — Facebook Messenger

A production-grade conversational AI system built for hotels and staycation businesses, integrated with **Facebook Messenger** via the Meta Graph API. The bot handles guest inquiries in real time, qualifies leads, collects structured booking information, and gives the property team a clear operational view of pipeline activity through a command-line admin dashboard.

> **Deployment note:** The core chatbot is fully functional end-to-end. Public deployment to a Facebook Page was blocked when Meta tightened third-party app publication requirements — apps must pass App Review before a Page Access Token can message the general public. The underlying system — conversation logic, database layer, booking intake, lead scoring, and automated reminders — operates independently of that constraint.

---

## Overview

Most hotel chatbots are shallow FAQ responders. This one is built around a real operational workflow: a guest messages the page, the bot qualifies their intent, collects booking details conversationally, stores everything in a structured database, and surfaces the most promising leads to the front desk — ranked by engagement score — so the team knows exactly who to follow up with first.

---

## Features

**Conversational AI**  
Handles natural language inquiries about room rates, availability, amenities, policies, and promotions. Responses are generated via the Claude API and shaped to match the property's tone and voice.

**Booking Intake**  
Guides guests through a structured collection flow — check-in and check-out dates, number of guests, room preference, and contact number — and stores each inquiry as a discrete, queryable database record.

**Lead Scoring**  
Tracks engagement signals per user: number of rate inquiries, availability checks, and booking button interactions. Leads are scored automatically so the front desk can prioritise follow-ups without manual triage.

**Automated Reminders**  
Sends 24-hour pre-arrival reminders and post-stay thank you messages to confirmed guests via the Messenger API on a scheduled basis.

**Admin Dashboard**  
A command-line interface that surfaces hot leads (score 50+), pending booking inquiries with contact details and requested dates, and a full customer list with message history. Supports CSV export for use in external CRM tools.

**Professional Message Templates**  
Booking confirmations are generated with a unique reference number (`PR-YYMMDD-XXXX`), structured reservation details, and a consistent, formal tone suitable for hospitality communication.

---

## Project Structure

```
hotel-chatbot/
├── bot_professional_complete.py   Main chatbot logic and Messenger webhook handler
├── database.py                    SQLAlchemy models and all database operations
├── templates.py                   Booking confirmation and reminder message templates
├── automated_reminders.py         Scheduler for 24-hour reminders and post-stay messages
├── admin_dashboard.py             CLI admin panel for leads, bookings, and customers
├── .env.example                   Environment variable template (copy to .env)
└── .gitignore                     Excludes sensitive files from version control
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Messenger Integration | Meta Graph API v18.0 |
| AI Response Generation | Claude API (Anthropic) |
| Database | SQLite via SQLAlchemy ORM |
| HTTP / Webhook | Flask, Requests |
| Configuration | python-dotenv |

---

## Database Schema

| Table | Purpose |
|---|---|
| `customers` | Guest profiles, contact information, message count, and status |
| `conversations` | Full conversation history per user with timestamps |
| `booking_inquiries` | Structured reservation requests with dates and guest details |
| `lead_scores` | Per-user engagement signals used for sales prioritisation |

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/hotel-chatbot.git
cd hotel-chatbot
```

### 2. Install dependencies

```bash
pip install flask requests sqlalchemy python-dotenv anthropic
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your credentials:

```
PAGE_ACCESS_TOKEN=your_facebook_page_access_token_here
VERIFY_TOKEN=any_string_you_choose
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

Never commit your `.env` file. The included `.gitignore` excludes it automatically.

### 4. Obtain Facebook credentials

1. Go to [developers.facebook.com](https://developers.facebook.com) and create an app
2. Add the **Messenger** product to your app
3. Generate a **Page Access Token** for your Facebook Page
4. Set a **Verify Token** — any string, as long as it matches your webhook configuration
5. Register your webhook URL under Messenger > Webhooks in the developer console

### 5. Run the chatbot

```bash
python bot_professional_complete.py
```

### 6. Use the admin dashboard

```bash
python admin_dashboard.py             # View leads, bookings, and recent customers
python admin_dashboard.py export      # Export lead data to a timestamped CSV
```

### 7. Send automated reminders

```bash
python automated_reminders.py reminders    # Send 24-hour pre-arrival reminders
python automated_reminders.py thankyou     # Send post-stay thank you messages
```

---

## Deployment Constraints

Meta's App Review process requires that any app using a Page Access Token to message the general public be formally reviewed and approved before going live. This policy change was the deployment blocker for this project. The chatbot was built for and tested against a real business use case (Paradise Resort), and the full conversation and booking logic functions correctly in a controlled environment. Completing App Review is the remaining step for public deployment.

---

## Security Notes

- Store all credentials in `.env` — never hardcode tokens directly in source files
- The `.gitignore` in this repository excludes `.env`, `*.db`, and exported CSV files from version control
- If a `PAGE_ACCESS_TOKEN` is ever accidentally exposed in a public repository, rotate it immediately from the Meta Developer Console

---

## Author

**Charles Ivan Valles Tomanglao**  
Bachelor of Science in Computer Science — Data Science  
Perpetual Help System Laguna  
charlesivantomanglao@gmail.com
