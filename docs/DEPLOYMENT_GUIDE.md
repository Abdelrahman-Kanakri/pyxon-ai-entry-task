# 🚀 Deployment Guide

This guide explains how to deploy the Pyxon AI Document Parser to get a live "Demo Link" for your submission.

We recommend **Hugging Face Spaces** as it is free, easy, and designed for AI demos.

---

## Option 1: Hugging Face Spaces (Recommended)

Hugging Face Spaces is the standard way to host AI demos. We have configured the `Dockerfile` specifically for this platform.

### 1. Create a Space

1.  Go to [huggingface.co/spaces](https://huggingface.co/spaces) and click **"Create new Space"**.
2.  **Space name**: `pyxondemo` (or similar).
3.  **License**: `MIT`.
4.  **SDK**: Select **Docker**.
5.  **Blank**: Choose "Blank" template.
6.  Click **Create Space**.

### 2. Upload Your Code

You can upload files directly via the browser or use Git.

**Via Browser (Easiest):**

1.  In your new Space, go to the **Files** tab.
2.  Click **"Add file"** -> **"Upload files"**.
3.  Drag and drop **ALL** files from your project folder:
    - `Dockerfile`
    - `requirements.txt`
    - `README.md`
    - `src/` folder
    - `api/` folder
    - `interface/` folder
    - `data/` folder
    - `database/` folder
    - `benchmarks/` folder
4.  Click **Commit changes**.

### 3. Set Secrets (Environment Variables)

Your app needs API keys to work. Do NOT commit your `.env` file directly!

1.  In your Space, go to **Settings**.
2.  Scroll to **"Variables and secrets"**.
3.  Click **"New secret"** and add:
    - `MISTRAL_API_KEY`: (Your Mistral key)
    - `GOOGLE_GENAI_API_KEY`: (Your Google key)

### 4. Wait for Build

- Click the **App** tab.
- You will see "Building...". This takes about 3-5 minutes.
- Once finished, you will see "Running" and your Streamlit app will appear!
- **Copy the URL** (e.g., `https://huggingface.co/spaces/username/pyxondemo`). This is your **Demo Link**.

---

## Option 2: Render.com

If you prefer a standard cloud host:

1.  Create a [Render](https://render.com) account.
2.  Click **New +** -> **Web Service**.
3.  Connect your GitHub repository (you must push code to GitHub first).
4.  **Runtime**: Select **Docker**.
5.  **Environment Variables**: Add your API keys under the "Environment" tab.
6.  Click **Create Web Service**.

Render may take longer to build and requires credit card verification for some free tier limits, which is why we recommend Hugging Face.

---

## ⚠️ Troubleshooting

**"Connection Refused"**

- Ensure `Dockerfile` exposes port `7860`.
- Ensure Streamlit is starting on port `7860`.

**"OOM / Out of Memory"**

- The specific `multilingual-e5-small` model is lightweight, but if you crash, try upgrading the hardware tier or switching to a smaller embedding model if strictly necessary.
