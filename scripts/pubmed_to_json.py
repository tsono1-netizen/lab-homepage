import json
import xml.etree.ElementTree as ET
from urllib.request import urlopen
from urllib.parse import quote

AUTHOR_QUERY = 'Sono T[Author]'
MAX_RESULTS = 30

search_url = (
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    f"?db=pubmed&term={quote(AUTHOR_QUERY)}&retmax={MAX_RESULTS}&sort=date&retmode=json"
)

with urlopen(search_url) as r:
    ids = json.load(r)["esearchresult"]["idlist"]

if not ids:
    print("No publications found.")
    exit()

fetch_url = (
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    f"?db=pubmed&id={','.join(ids)}&retmode=xml"
)

with urlopen(fetch_url) as r:
    root = ET.parse(r).getroot()

publications = []

for article in root.findall(".//PubmedArticle"):
    pmid = article.findtext(".//PMID", default="")
    title = article.findtext(".//ArticleTitle", default="").strip()

    journal = article.findtext(".//Journal/Title", default="")
    year = (
        article.findtext(".//PubDate/Year")
        or article.findtext(".//PubMedPubDate[@PubStatus='pubmed']/Year")
        or ""
    )

    author_names = []
    for author in article.findall(".//Author")[:8]:
        last = author.findtext("LastName", default="")
        initials = author.findtext("Initials", default="")
        if last:
            author_names.append(f"{last} {initials}".strip())

    authors = ", ".join(author_names)
    if len(article.findall(".//Author")) > 8:
        authors += ", et al."

    publications.append({
        "title": title,
        "authors": authors,
        "journal": journal,
        "year": year,
        "pmid": pmid
    })

with open("data/publications.json", "w", encoding="utf-8") as f:
    json.dump(publications, f, ensure_ascii=False, indent=2)

print(f"Updated {len(publications)} publications.")