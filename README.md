# Real Estate Data Pipeline

Still in development. An automated ETL pipeline for scraping, transforming, and storing real estate property listings with semantic search capabilities.

## Overview

This project extracts rental property data from real estate websites, validates and transforms the data, stores it in a local database, and enables semantic search using vector embeddings. Designed for learning CI/CD practices, testing patterns, and data pipeline development.

## Currently includes a prototype of the following features

- **Config-driven scraping** - JSON configs define extraction logic per site
- **Automated validation** - Test suite ensures data quality
- **Vector embedding** - Vector embeddings for natural language property search
- **Duplicate handling** - Automatic upsert logic by property ID
- **Scrape history** - Track when properties were last updated
- **Headless operation** - Runs in background without browser UI

## Upcoming

- **Semantic Search**: Users search for the "vibe" of their ideal house, search vector database for a property description that is semantically similar to their wants
- **Automated Notification System**: Saves all user searches, notifies them if a new property added is something they might like




Testing repo changes
# test
