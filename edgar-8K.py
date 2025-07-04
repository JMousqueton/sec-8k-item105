import requests
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": "Ransomware.live/1.0 (contact: support@ransomware.live)",
    "Accept": "application/json"
}

BASE_URL = "https://efts.sec.gov/LATEST/search-index"


def extract_item_105_text(index_url):
    try:
        index_resp = requests.get(index_url, headers=HEADERS)
        soup = BeautifulSoup(index_resp.text, "html.parser")

        # Get the actual .htm document
        table = soup.find("table", class_="tableFile", summary="Document Format Files")
        if not table:
            return None

        href = None
        for row in table.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) >= 4 and "8-K" in cols[3].text:
                href = cols[2].find("a")["href"]
                break

        if not href:
            return None

        if href.startswith("/ix?doc="):
            href = href.replace("/ix?doc=", "")
        full_doc_url = f"https://www.sec.gov{href}"
        doc_resp = requests.get(full_doc_url, headers=HEADERS)
        if doc_resp.status_code != 200:
            return None

        # Try ix:nonNumeric parsing
        doc_soup = BeautifulSoup(doc_resp.content, "lxml-xml")
        texts = []
        seen_ids = set()

        def follow_continuations(elem_id):
            while elem_id and elem_id not in seen_ids:
                seen_ids.add(elem_id)
                cont = doc_soup.find("ix:continuation", attrs={"id": elem_id})
                if cont:
                    texts.append(cont.get_text(" ", strip=True))
                    elem_id = cont.get("continuedat")
                else:
                    break

        for tag in doc_soup.find_all("ix:nonNumeric"):
            name = tag.get("name", "").lower()
            if "cybersecurityincident" in name and "textblock" in name:
                texts.append(tag.get_text(" ", strip=True))
                follow_continuations(tag.get("continuedat"))

        if texts:
            raw = " ".join(texts)
            clean = re.sub(r"\s+", " ", raw).strip()
        else:
            # fallback to HTML parsing
            doc_soup = BeautifulSoup(doc_resp.text, "html.parser")
            lines = doc_soup.get_text(separator="\n").splitlines()
            capture = False
            relevant = []

            for line in lines:
                line_clean = line.strip().lower()
                if "item 1.05" in line_clean:
                    capture = True
                    relevant.append(line.strip())
                elif capture:
                    if re.match(r"item\s+1\.\d+", line_clean) and not line_clean.startswith("item 1.05"):
                        break
                    relevant.append(line.strip())

            clean = "\n".join(relevant).strip()

        clean = re.sub(r'\n{2,}', '\n', clean)
        for word in ["ransomware", "unauthorized", "exfiltrated", "production", "offline", "threat actor"]:
            clean = re.sub(
                rf"(?i)\b({word})\b",
                lambda m: f"\033[4m\033[33m{m.group(1)}\033[0m",
                clean
            )
        return clean if clean else None

    except Exception as e:
        print(f"Error extracting Item 1.05: {e}")
        return None
cl


def search_8k_105(days=3, max_results=100):
    keywords="\"Item 1.05\""
    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=days)

    print(f"🔎 Searching for 8-K Item 1.05: Material Cybersecurity Incidents from {start_date} to {end_date}")

    results = []
    page_size = 100
    fetched = 0
    total = None

    while fetched < max_results:
        params = {
            "q": keywords,
            "forms": ["8-K"],
            "startdt": start_date.strftime("%Y-%m-%d"),
            "enddt": end_date.strftime("%Y-%m-%d"),
            "from": fetched,
            "size": page_size,
            "sort": "desc"
        }

        resp = requests.get(BASE_URL, headers=HEADERS, params=params)
        if resp.status_code != 200:
            print("Error querying SEC:", resp.status_code, resp.text)
            break

        data = resp.json()
        filings = data.get("hits", {}).get("hits", [])
        total = data.get("hits", {}).get("total", {}).get("value", 0)

        if not filings:
            break
        for item in filings:
            src = item["_source"]
            cik = src.get("ciks", [None])[0]
            adsh = src.get("adsh", "N/A")
            accession_no = adsh.replace("-", "")
            link = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_no}/{adsh}-index.htm"

            item_105_text = extract_item_105_text(link)

            results.append({
                "company": src.get("display_names", ["Unknown"])[0],
                "filing_date": src.get("file_date", "N/A"),
                "cik": cik,
                "link": link,
                "item_105": item_105_text
            })

        fetched += len(filings)
        if fetched >= total or len(filings) < page_size:
            break

    print(f"Found {len(results)} result(s).\n")
    return results

def display_filings(results):
    if not results:
        print("No relevant 8-K filings found.")
        return

    for filing in results:
        print(f"📄 {filing['company']}")
        print(f"   📅 Date: {filing['filing_date']}")
        print(f"   🔗 {filing['link']}")
        if filing.get("item_105"):
            print(f"   🧾 Item 1.05:\n{filing['item_105'][:500]}{'...' if len(filing['item_105']) > 500 else ''}")
        else:
            print("   ⚠️ No Item 1.05 text found.")
        print()


if __name__ == "__main__":
    filings = search_8k_105(days=15)
    display_filings(filings)
