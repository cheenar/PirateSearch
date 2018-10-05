#!/usr/local/bin/python3

# --- Imports --- #
import os;
import sys;
import requests;
import cfscrape; #using this for safety
from bs4 import BeautifulSoup;
import webbrowser;

# --- Vars --- #
_is_debug = False; 
_base_url = "https://thepiratebay.org" # the idea is that you could use a proxy
_scraper = cfscrape.create_scraper();
_user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36"
_session = requests.session();

def debug_print(msg):
    if _is_debug:
        print("[TPB] " + str(msg));

# --- Argument Handling --- # 
def handle_arguments():
    global _is_debug, _base_url;

    for arg in sys.argv[1:]:
        if arg == "-d":
            _is_debug = True;
            debug_print("Debug Mode Enabled");
        if arg[0:2] == "-U":
            if ":" in arg:
                _base_url = arg.split("=")[1]
                debug_print("Set Base URL: " + _base_url);

# sort_se=True => Sort H->L Seeders        
def build_query(query_title, sort_se=True, page=0):
    return _base_url + "/search/" + query_title.replace(" ", "%20") + "/" + str(page) + "/99/0";

def search(query_title, pag=0, hdrs={"User-Agent":_user_agent}):
    raw = _session.get(build_query(query_title, page=pag), headers=hdrs);
    return raw;

def soup_san(soup):
    return soup.text.replace("\n", "").replace("\t", "");

def parse_row(row):
    items = row.find_all("td");
    _type = soup_san(items[0]);
    _name = soup_san(items[1].find("div", {"class":"detName"}));
    _magnet = items[1].find_all("a")[1].attrs["href"]
    _seeders = items[2].text;
    _leechers = items[3].text;
    out = {
        "Type": _type,
        "Name": _name,
        "Magnet": _magnet,
        "Seeders": _seeders,
        "Leechers": _leechers
    }
    return out;

def pretty_row(index, dict_row):
    # 1|title|seeders|leechers
    return str(index) + "|" + dict_row["Name"] + "|" + dict_row["Seeders"] + "|" + dict_row["Leechers"];

if __name__ == "__main__":
    print("ThePirateBay.org Search");
    handle_arguments();
    while True:
        _title = input("Search: ");
        found_link = False
        pg = 0
        while not found_link:
            _search = search(_title, pag=pg);
            rows = BeautifulSoup(_search.text).find_all("tr")[1:]
            index = 0;
            for row in rows:
                dr = parse_row(row);
                print(pretty_row(index, dr))
                index += 1;
            print("X|Next Page");
            print("Y|Pass");
            _link = input("Link: ")
            if _link == "X":
                pg += 1;
                continue;
            if _link == "Y":
                break;
            print(_link);
            found_link = parse_row(rows[int(_link)])["Magnet"];
		
        if found_link:
            webbrowser.open(found_link);
