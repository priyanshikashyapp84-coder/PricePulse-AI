# ⚡ PricePulse AI

PricePulse AI is a smart price-tracking platform that collects product data, tracks price history, detects price drops, and helps users make smarter buying decisions.

## Features

- Product price tracking
- Price history
- Price-drop detection
- Product search and sorting
- Price trend visualization
- Scraper health monitoring
- Self-healing scraper with automatic retries

## Tech Stack

- Python
- Flask
- Playwright
- Bright Data Browser API
- HTML
- CSS
- JavaScript
- JSON

## How It Works

Bright Data + Playwright
        ↓
Product Scraper
        ↓
Structured Product Data
        ↓
Flask API
        ↓
PricePulse AI Dashboard

## Problem

Online shoppers often have to repeatedly check products to know if their prices have changed. PricePulse AI automates price tracking and highlights useful price changes.

## Run Locally

```bash
pip install -r requirements.txt
python backend/browser_client.py
python backend/app.py

Open: http://127.0.0.1:5000/
