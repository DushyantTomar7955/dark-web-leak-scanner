import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

# ================== PAGE CONFIG ==================
st.set_page_config(page_title="Dark Web Leak Scanner", layout="centered")

# ================== SIMPLE STYLES ==================
st.markdown("""
<style>
.title { font-size: 30px; font-weight: bold; color: #2C3E50; }
.subtitle { font-size: 14px; color: #555; margin-bottom: 15px; }
.box { padding: 12px; border-radius: 8px; margin-bottom: 10px; background-color: #F4F6F7; }
.safe { color: #117A65; font-weight: bold; }
.risk { color: #922B21; font-weight: bold; }
.info { color: #1B4F72; font-weight: bold; }
.link { color: #1A73E8; text-decoration: none; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ================== HEADER ==================
st.markdown('<div class="title">🔍 Dark Web Leak Scanner</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Check if email or phone appears in public leak dumps & paste sites (free sources)</div>', unsafe_allow_html=True)

# ================== UTIL ==================
def is_email(text):
    return re.match(r"[^@]+@[^@]+\.[^@]+", text)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# ================== PSBDMP (FREE PASTE DUMP DB) ==================
def check_psbdmp(query):
    try:
        url = f"https://psbdmp.ws/api/search/{query}"
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

# ================== PASTEBIN SEARCH ==================
def search_pastebin(query):
    results = []
    try:
        search_url = f"https://pastebin.com/search?q={query}"
        r = requests.get(search_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        links = soup.find_all("a")
        for link in links:
            href = link.get("href")
            if href and href.startswith("/"):
                full_link = "https://pastebin.com" + href
                if "/archive/" not in full_link:
                    results.append(full_link)
    except:
        pass
    return list(set(results))[:5]

# ================== FILTERED DUCKDUCKGO LEAK SEARCH ==================
def duckduckgo_leak_search(query):
    results = []
    blocked_domains = [
        "haveibeenpwned.com",
        "breachdirectory.org",
        "ipqualityscore.com",
        "databreach.com",
        "beenleaked.com",
        "leakcheck.net"
    ]

    try:
        search_url = f'https://duckduckgo.com/html/?q="{query}"+("leak"+OR+"dump"+OR+"password"+OR+"database")'
        r = requests.get(search_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        links = soup.find_all("a", class_="result__a")

        for link in links:
            href = link.get("href")
            title = link.text.strip()

            if href:
                if any(domain in href for domain in blocked_domains):
                    continue

                results.append({
                    "title": title,
                    "link": href
                })
    except:
        pass

    return results[:5]

# ================== UI ==================
st.markdown("### 📥 Enter Email or Phone Number")
user_input = st.text_input("", placeholder="e.g. test@gmail.com or 9876543210")

scan_btn = st.button("🚀 Scan")

if scan_btn:

    if not user_input:
        st.warning("Please enter email or phone number.")
    else:
        st.markdown("---")
        st.markdown("## 🔎 Results")

        # ========== PSBDMP ==========
        st.markdown("### 🗄 Paste Dump Database (PSBDMP)")
        psb_results = check_psbdmp(user_input)

        if psb_results and len(psb_results) > 0:
            st.markdown('<div class="box risk">⚠ Found in leaked paste dumps</div>', unsafe_allow_html=True)

            for item in psb_results[:5]:
                paste_id = item.get("id")
                paste_time = item.get("time")
                paste_title = item.get("title") or "Untitled Dump"

                if paste_id:
                    paste_link = f"https://pastebin.com/{paste_id}"
                    clickable_link = f'<a class="link" href="{paste_link}" target="_blank">Open Source</a>'
                else:
                    clickable_link = "N/A"

                st.markdown(f"""
**Title:** {paste_title}  
**Date:** {paste_time}  
**Source:** {clickable_link}  
---
""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="box safe">✓ Not found in PSBDMP database</div>', unsafe_allow_html=True)

        # ========== PASTEBIN ==========
        st.markdown("### 📄 Pastebin Public Search")
        paste_results = search_pastebin(user_input)

        if paste_results:
            st.markdown('<div class="box risk">⚠ Found on Pastebin</div>', unsafe_allow_html=True)
            for link in paste_results:
                st.markdown(f'<a class="link" href="{link}" target="_blank">{link}</a>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="box safe">✓ No public Pastebin results</div>', unsafe_allow_html=True)

        # ========== DUCKDUCKGO ==========
        st.markdown("### 🌐 Public Leak Pages & Dumps")
        ddg_results = duckduckgo_leak_search(user_input)

        if ddg_results:
            st.markdown('<div class="box risk">⚠ Possible leak pages found</div>', unsafe_allow_html=True)
            for item in ddg_results:
                title = item["title"]
                link = item["link"]
                st.markdown(f'**{title}**  \n<a class="link" href="{link}" target="_blank">Open Source</a>', unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.markdown('<div class="box safe">✓ No public leak pages found</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.success("Scan Completed")
