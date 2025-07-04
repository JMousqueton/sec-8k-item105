
# SEC EDGAR 8-K Item 1.05 Extractor

This Python script automates the process of searching and extracting **Material Cybersecurity Incidents** (Item 1.05) from recent 8-K filings in the [SEC EDGAR](https://www.sec.gov/edgar.shtml) database.

⚠️ **Note:** This tool is for **research, threat intelligence**, and **educational** purposes only. It highlights companies disclosing cybersecurity incidents per U.S. regulatory requirements.

## Features

- 📅 Searches 8-K filings within a configurable date range.
- 🔍 Filters for those containing `"Item 1.05"` (Material Cybersecurity Incidents).
- 📑 Extracts and formats the content of the Item 1.05 section using:
  - Inline XBRL (iXBRL) parsing
  - HTML fallback parsing
- 🖍️ Highlights keywords such as `ransomware`, `unauthorized`, `exfiltrated`, etc.
- 🔗 Provides direct links to the original filings on the SEC website.
- ✅ Supports command-line execution.

## Example Output

```
🔎 Searching for 8-K Item 1.05: Material Cybersecurity Incidents from 2025-06-20 to 2025-07-05

📄 Sensata Technologies Holding plc
   📅 Date: 2025-04-09
   🔗 https://www.sec.gov/Archives/edgar/data/0001477294/000147729425000047/0001477294-25-000047-index.htm
   ⚠️ No Item 1.05 text found.

📄 Coinbase Global Inc.
   📅 Date: 2025-05-14
   🔗 https://www.sec.gov/Archives/edgar/data/1679788/000167978825000094/coin-20250514.htm
   🧾 Item 1.05:
   On May 13, 2025, Coinbase identified unauthorized access to its cloud infrastructure... [truncated]
```

## Installation

1. **Clone the repo**

```bash
git clone https://github.com/yourusername/sec-8k-item105.git
cd sec-8k-item105
```

2. **Install required dependencies**

```bash
pip install -r requirements.txt
```

_Requirements:_
- `requests`
- `beautifulsoup4`
- `lxml`

## Usage

⚠️ The SEC requires scripts that access EDGAR data to include a descriptive `User-Agent` header with contact information.  

If you are running this script for your own use, **you must change** the User-Agent to reflect your own name, email, or organization.  
This helps the SEC contact you in case of issues or abuse.

Update the `HEADERS` dictionary in the script:

```python
HEADERS = {
    "User-Agent": "YourName/1.0 (contact: your-email@example.com)",
    "Accept": "application/json"
}
```


```bash
python edgar-8K.py
```

Optional parameters (inside the script):
- `days=15`: Number of days back to search.
- `max_results=100`: Max filings to retrieve.

## File Structure

```
edgar-8K.py            # Main script
README.md              # Documentation
requirements.txt       # Python dependencies
```

## Keyword Highlighting

The following keywords are highlighted in console output for visibility:
- `ransomware`
- `unauthorized`
- `exfiltrated`
- `production`
- `offline`
- `threat actor`

## Disclaimer

This is an unofficial tool and not affiliated with the SEC. Always verify disclosures using the official [EDGAR database](https://www.sec.gov/edgar/searchedgar/companysearch.html). Parsing logic may break if SEC changes their HTML/XBRL structure.

---

## License

[MIT License](LICENSE)
