# FACEIT Mully Rating Bot

Telegram bot for analyzing FACEIT CS2 players using a custom **Mully Rating** system.

The project evaluates player performance beyond basic stats (K/D, ADR) by combining combat impact, clutch ability, entry success, and multikill contribution into a single score.

---

## 🚀 Features

### 📊 Player Analysis

* Calculates **Mully Rating (0–100)**
* Displays rank tier (S–D)
* Shows ELO, level, and country

---

### 📈 Match Trend

* Performance graph across recent matches
* Detects consistency and performance changes

---

### 🗺 Map Statistics

* Rating per map
* Tier-based visualization (S–D)
* Performance bars for quick comparison

---

### ⚡ Performance Optimizations

* Parallel API requests (ThreadPoolExecutor)
* Smart caching by `match_id`
* Reduced API load (no duplicate requests)

---

## 🧠 Mully Rating System

The rating is based on multiple weighted components:

* **Combat** (ADR, K/D, K/R, MVP)
* **Entry impact**
* **Clutch success (1v1–1v5)**
* **Multikills (double → ace)**

Final score is normalized to **0–100** and adjusted with penalties for low performance.

---

## 📦 Project Structure

```text
FACEIT_MULLY_RATING/
│
├── src/
│   ├── analyzer.py      # Main analysis logic
│   ├── match.py         # Match-level API + caching
│   ├── player.py        # Player info & matches
│   ├── maps.py          # Map performance
│   ├── trend.py         # Trend + visualization
│   ├── score.py         # Rating formula
│
├── bot.py               # Telegram bot entry point
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## ⚙️ Setup

### 1. Clone repository

```bash
git clone https://github.com/your-username/faceit-mully-rating.git
cd faceit-mully-rating
```

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Create `.env` file

```env
FACEIT_API_KEY=your_faceit_api_key
TG_BOT_TOKEN=your_telegram_bot_token
```

---

### 4. Run bot

```bash
python bot.py
```

---

## 🔐 Environment Variables

| Variable       | Description           |
| -------------- | --------------------- |
| FACEIT_API_KEY | FACEIT public API key |
| TG_BOT_TOKEN   | Telegram bot token    |

---

## ⚠️ Notes

* Do NOT commit your `.env` file
* API requests are optimized but still limited by FACEIT rate limits
* Designed for analytical purposes, not official ranking

---

## 🛠 Tech Stack

* Python
* python-telegram-bot
* requests
* matplotlib

---

## 📈 Future Improvements

* Player comparison system
* Advanced playstyle detection
* Recommendations based on weaknesses
* Persistent cache (Redis)
* Web interface

---

## 📄 License

MIT
