# ReportForge

**ReportForge** is an automated report generation API built with FastAPI.  
The goal is to provide a flexible and customizable system for uploading structured data (e.g. CSV files), processing it, and generating clean, downloadable reports (e.g. PDF, Excel, Markdown).

---

## 🚀 Features (planned)

- Upload CSV files via API
- Apply customizable transformations and filters
- Generate downloadable reports in various formats
- RESTful API built with FastAPI
- CLI tools for local generation (future)
- Optional authentication layer (future)

---

## 📁 Project Structure (WIP)
```
ReportForge/ 
├── app/ 
│ ├── main.py # FastAPI entrypoint 
│ └── init.py 
├── requirements.txt 
├── .gitignore 
├── README.md 
└── venv/ # Virtual environment (excluded from version control)
```
---

## 🛠 Setup

```
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```
---
## Available Endpoints

### POST `/upload`

Uploads a CSV file and returns:

- List of columns  
- Data types  
- Basic statistics

#### Example:

```bash
curl -X POST http://127.0.0.1:8000/upload \
  -F 'file=@file.csv'
