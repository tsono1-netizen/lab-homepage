from Bio import Entrez
import json
import time
from xml.etree import ElementTree as ET

Entrez.email = "tsono1@sono-lab.net"

QUERY = '(Sono Takashi[Author])'
MAX_PAPERS = 20

search = Entrez.esearch(
    db="pubmed",
    term=QUERY,
    retmax=MAX_PAPERS,
    sort="pub date"
)

record = Entrez.read(search)
ids = record["IdList"]

papers = []

for pmid in ids:
    try:
        fetch = Entrez.efetch(
            db="pubmed",
            id=pmid,
            rettype="xml"
        )

        xml_data = fetch.read()
        root = ET.fromstring(xml_data)

        article = root.find(".//PubmedArticle")

        title = article.findtext(".//ArticleTitle", default="")

        journal = article.findtext(".//Title", default="")

        year = article.findtext(".//PubDate/Year", default="")

        authors = []

        for a in article.findall(".//Author"):
            lastname = a.findtext("LastName")
            initials = a.findtext("Initials")

            if lastname and initials:
                authors.append(f"{lastname} {initials}")

        papers.append({
            "title": title,
            "authors": ", ".join(authors),
            "journal": journal,
            "year": year,
            "pmid": pmid,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        })

        time.sleep(0.3)

    except Exception as e:
        print("Error:", pmid, e)

with open("data/publications.json", "w", encoding="utf-8") as f:
    json.dump(papers, f, ensure_ascii=False, indent=2)

print(f"Saved {len(papers)} papers.")