# Aceh Weather & Disaster Alert Bot 🌧️🌊🌩️

This bot automatically monitors official Indonesian disaster & weather sources
and reposts any updates relevant to **Aceh**, including:

- BMKG (weather, tsunami warnings, earthquake reports)
- BPBD Aceh (local disaster updates)
- BNPB Indonesia
- And more

The bot filters tweets based on **all Kabupaten/Kota in Aceh**, and posts them
automatically with relevant hashtags.

---

## 🔧 Features

- Monitors official accounts:
  - `@infoBMKG`
  - `@BMKG_ACEH`
  - `@BMKG_Official`
  - `@BNPB_Indonesia`
  - `@BPBD_Aceh`
- Filters content by Aceh districts
- Adds visibility hashtags
- Prevents duplicate posting
- Runs continuously via GitHub Actions

---

## 🛠 Setup

### 1️⃣ Prepare X Developer Credentials

You need these:

- API key
- API secret
- Access token
- Access secret

Add them in:

**GitHub → Settings → Secrets → Actions**

Set:

