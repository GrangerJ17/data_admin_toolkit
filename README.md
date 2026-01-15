# Real Estate Data Pipeline

An automated ETL pipeline for scraping, transforming, and storing real estate property listings with semantic search capabilities.

## Overview

This project extracts rental property data from real estate websites, validates and transforms the data, stores it in a local database, and enables semantic search using vector embeddings. Designed for learning CI/CD practices, testing patterns, and data pipeline development.

## Features

- **Config-driven scraping** - JSON configs define extraction logic per site
- **Automated validation** - Test suite ensures data quality
- **Semantic search** - Vector embeddings for natural language property search
- **Duplicate handling** - Automatic upsert logic by property ID
- **Scrape history** - Track when properties were last updated
- **Headless operation** - Runs in background without browser UI
