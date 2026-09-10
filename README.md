# UrbanSolv AI Engineer Technical Test

An end-to-end AI engineering project covering data collection, data cleaning, REST API development, and an LLM-powered AI Agent for business data analysis.

## Project Overview

This project was developed as part of the **UrbanSolv AI Engineer Technical Test**.

The project processes restaurant business data in **Kecamatan Tembalang**, from data collection to an AI Agent that can answer natural-language questions based on the processed dataset.

### Tasks

* **Task 1:** Google Maps business data scraping
* **Task 2:** Data cleaning and preprocessing
* **Task 3:** FastAPI REST API
* **Task 4:** LLM-powered AI Agent

---

## Project Structure

```text
urbansolv-test/
│
├── agent/
│   └── agent.py
│
├── api/
│   └── main.py
│
├── data/
│   └── clean_data.csv
│
├── scraper/
│   └── ...
│
├── .env.example
├── .gitignore
└── README.md
```

---

# Task 1 — Google Maps Data Scraping

The first task collects business information from Google Maps for **Bakmi and Ramen businesses in Kecamatan Tembalang**.

### Collected Fields

The scraper collects the following information:

* Nama Tempat
* Alamat
* Jenis Bisnis
* Rating
* Jumlah Bintang
* Jumlah Review
* Jam Operasional
* Harga
* Latitude
* Longitude
* Telepon
* Website

The scraping process was implemented using **Python and Playwright**.

The collected data was then stored as a raw dataset for further processing.

---

# Task 2 — Data Cleaning and Preprocessing

The raw dataset was cleaned and standardized before being used by the API and AI Agent.

### Cleaning Process

The preprocessing includes:

* Removing duplicate businesses based on name and address
* Handling missing values
* Standardizing column names
* Extracting Kecamatan
* Extracting Kelurahan
* Cleaning and standardizing relevant data fields
* Saving the final processed dataset as CSV

### Final Dataset

The final dataset contains:

* **77 business records**
* **14 columns**

Output file:

```text
data/clean_data.csv
```

Final columns:

```text
nama_tempat
alamat
jenis_bisnis
rating
jumlah_bintang
jumlah_review
jam_operasional
harga
latitude
longitude
telepon
no
kecamatan
kelurahan
```

---

# Task 3 — FastAPI REST API

The cleaned dataset is exposed through a REST API using **FastAPI**.

The API uses `clean_data.csv` as its primary data source.

## Available Endpoints

### GET `/`

Checks whether the API is running.

Example response:

```json
{
  "message": "UrbanSolv API is running"
}
```

### GET `/businesses`

Returns all businesses from the cleaned dataset.

### GET `/businesses/search`

Searches businesses based on available filters.

Supported parameters include:

* `keyword`
* `kelurahan`
* `kecamatan`
* `rating`
* `jumlah_review`
* `harga`

Example:

```text
/businesses/search?keyword=ramen&rating=4.7
```

### GET `/statistics`

Returns summary statistics from the dataset, including:

* Total businesses
* Average rating
* Total reviews
* Total Bakmi businesses
* Total Ramen businesses

### API Documentation

FastAPI automatically provides interactive Swagger documentation at:

```text
http://127.0.0.1:8000/docs
```

## Running the API

From the project root:

```bash
uvicorn api.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

# Task 4 — LLM-Powered AI Agent

The final task implements an AI Agent that allows users to interact with the restaurant dataset using natural language.

The Agent uses an LLM to understand the user's question and convert it into structured filters or intents.

The Agent then retrieves data through the **FastAPI**, which acts as the data access layer and source of truth.

## Supported Intents

The Agent currently supports:

### 1. Search

Used for searching businesses based on criteria such as:

* Business type
* Rating
* Kelurahan
* Kecamatan
* Number of reviews
* Price

Example:

```text
Cari ramen dengan rating di atas 4.7
```

### 2. Open Until

Finds businesses that are open until a specified time.

Example:

```text
Bakmi mana yang buka sampai jam 22.00?
```

The Agent performs additional time-based filtering using the operating-hours data.

### 3. Maximum Reviews

Finds the business with the highest number of reviews.

Example:

```text
Mana restoran yang reviewnya paling banyak?
```

### 4. Count

Counts businesses matching specific criteria.

Example:

```text
Ada berapa restoran ramen di Kelurahan Bulusan?
```

## AI Agent Architecture

```text
User Question
      │
      ▼
   Gemini LLM
      │
      ▼
Structured Intent / Filters
      │
      ▼
    FastAPI
      │
      ▼
clean_data.csv
      │
      ▼
Python Filtering / Processing
      │
      ▼
    Answer
```

The LLM is primarily used for **natural-language understanding**, while deterministic filtering and calculations are performed using Python and the dataset.

This approach helps ensure that the final results are based on the actual processed dataset rather than information generated from the LLM's general knowledge.

---

# Configuration

The AI Agent requires a Gemini API key.

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

A template is provided in:

```text
.env.example
```

The actual `.env` file is excluded from Git using `.gitignore` to prevent exposing the API key.

---

# Running the AI Agent

Make sure the FastAPI server is running first:

```bash
uvicorn api.main:app --reload
```

Then, in another terminal, run:

```bash
python agent/agent.py
```

The Agent will process the example questions defined in the script.

---

# Technologies

* **Python**
* **Pandas**
* **Playwright**
* **FastAPI**
* **Uvicorn**
* **Google Gemini API**
* **Requests**
* **python-dotenv**
* **Git & GitHub**

---

# Engineering Considerations

Several considerations were applied during development:

* Data cleaning is performed before the dataset is consumed by the API.
* The FastAPI layer provides a centralized interface for accessing the processed dataset.
* Natural-language interpretation is separated from deterministic data filtering.
* Rating comparisons such as **"di atas 4.7"** are handled using the appropriate strict comparison.
* Operating-hour queries are processed using time-based logic rather than relying solely on LLM responses.
* API credentials are stored in environment variables and excluded from version control.
* The project is structured into separate modules for scraping, data processing, API development, and AI Agent functionality.

---

# Conclusion

This project demonstrates an end-to-end AI engineering workflow:

**Data Collection → Data Cleaning → REST API → LLM-based Natural Language Interface**

The final system allows users to query structured business data using natural language while keeping the processed dataset as the primary source of information.
