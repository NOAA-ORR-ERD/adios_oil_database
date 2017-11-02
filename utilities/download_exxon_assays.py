#!/usr/bin/env python3

"""
Hacked together script to download all the assays from Exxon's web site:

http://corporate.exxonmobil.com/en/company/worldwide-operations/crude-oils/assays
"""

import requests

# oil names copied from the web site
raw_text = """
Aasgard Blend – PDF / 229.25 KB
Aasgard Blend – XLSX / 27.02 KB
Alaska North Slope – PDF / 229.04 KB
Azeri Light – PDF / 226.73 KB
Azeri Light – XLSX / 27.02 KB
Balder Blend – PDF / 229.39 KB
Balder Blend – XLSX / 27.02 KB
Banyu Urip – PDF / 227.16 KB
Banyu Urip – XLSX / 27 KB
Basrah – PDF / 229.39 KB
Basrah – XLSX / 27.03 KB
Basrah Heavy – PDF / 227.27 KB
Basrah Heavy – XLSX / 27.05 KB
Bonga – PDF / 229.67 KB
Bonga – XLSX / 26.98 KB
Brent Blend – PDF / 227.1 KB
Brent Blend – XLSX / 26.98 KB
CLOV – PDF / 226.66 KB
CLOV – XLSX / 27.02 KB
Cold Lake Blend – PDF / 229.18 KB
Cold Lake Blend – XLSX / 27.01 KB
Curlew – PDF / 58.3 KB
Curlew – XLSX / 32.36 KB
Dalia – PDF / 226.69 KB
Dalia – XLSX / 26.99 KB
Doba Blend – PDF / 227.23 KB
Doba Blend – XLSX / 27.01 KB
Ebok – PDF / 229.75 KB
Ebok – XLSX / 26.96 KB
Ekofisk – PDF / 226.72 KB
Ekofisk – XLSX / 26.98 KB
Erha – PDF / 226.83 KB
Erha – XLSX / 27.01 KB
Forties Blend – PDF / 226.75 KB
Forties Blend – XLSX / 26.99 KB
Gippsland Blend – PDF / 227.02 KB
Gippsland Blend – XLSX / 27 KB
Girassol – PDF / 227.13 KB
Girassol – XLSX / 27 KB
Grane – PDF / 229.83 KB
Grane – XLSX / 27.03 KB
Gudrun Blend – PDF / 227.15 KB
Gudrun Blend – XLSX / 27.04 KB
Gullfaks Blend – PDF / 227.11 KB
Gullfaks Blend – XLSX / 27.02 KB
Hibernia Blend – PDF / 226.95 KB
Hibernia Blend – XLSX / 27 KB
HOOPS Blend – PDF / 226.73 KB
HOOPS Blend – XLSX / 27 KB
Hungo Blend – PDF / 229.34 KB
Hungo Blend – XLSX / 27.01 KB
Jotun Blend – PDF / 226.82 KB
Jotun Blend – XLSX / 27.01 KB
Kearl Blend – PDF / 227.28 KB
Kearl Blend – XLSX / 27.02 KB
Kissanje Blend – PDF / 226.72 KB
Kissanje Blend – XLSX / 26.99 KB
Kutubu Blend – PDF / 226.63 KB
Kutubu Blend – XLSX / 27.03 KB
Marib Light – PDF / 226.7 KB
Marib Light – XLSX / 27 KB
Mondo Blend – PDF / 226.55 KB
Mondo Blend – XLSX / 27 KB
Ormen Lange – PDF / 226.6 KB
Ormen Lange – XLSX / 26.99 KB
Oseberg Blend – PDF / 227.22 KB
Oseberg Blend – XLSX / 27.02 KB
Oso Condensate – PDF / 227.11 KB
Oso Condensate – XLSX / 27.03 KB
Pazflor – PDF / 229.3 KB
Pazflor – XLSX / 27 KB
Qua Iboe – PDF / 227.07 KB
Qua Iboe – XLSX / 26.99 KB
Sable Island – PDF / 226.53 KB
Sable Island – XLSX / 27.04 KB
Saxi Batuque – PDF / 226.91 KB
Saxi Batuque – XLSX / 27 KB
Sokol – PDF / 226.41 KB
Sokol – XLSX / 26.99 KB
Statfjord Blend – PDF / 226.93 KB
Statfjord Blend – XLSX / 27 KB
Tapis – PDF / 226.5 KB
Tapis – XLSX / 27.01 KB
Terengganu Condensate – PDF / 226.81 KB
Terengganu Condensate – XLSX / 27.04 KB
Terra Nova – PDF / 226.78 KB
Terra Nova – XLSX / 26.98 KB
Thunder Horse – PDF / 229.37 KB
Thunder Horse – XLSX / 27.03 KB
Triton Blend – PDF / 226.66 KB
Triton Blend – XLSX / 26.98 KB
Troll Blend – PDF / 226.67 KB
Troll Blend – XLSX / 26.98 KB
Upper Zakum – PDF / 229.31 KB
Upper Zakum – XLSX / 27.01 KB
Usan – PDF / 229.55 KB
Usan – XLSX / 27.02 KB
Volve – PDF / 226.68 KB
Volve – XLSX / 27.03 KB
Woollybutt – PDF / 229.6 KB
Woollybutt – XLSX / 27.04 KB
YOHO – PDF / 229.06 KB
YOHO – XLSX / 27.01 KB
Zafiro Blend – PDF / 227.56 KB
Zafiro Blend – XLSX / 27.01 KB
"""

# clean it up to make urls out of it:

oils = raw_text.split('\n')
oils = [oil.split("–")[0].strip() for oil in oils]
oils = [oil for oil in oils if oil]
# remove duplicates:
oils = set(oils)
# lower-case and add underscores
oils = [oil.lower().replace(' ', '_') for oil in oils]
print(oils)

# the main url:
url_template = "http://cdn.exxonmobil.com/~/media/global/files/crude-oil-sales/crude_oil_{}_assay_xls.xlsx"

# download those suckers!
for oil in oils:
    print("downloading:", oil)
    url = url_template.format(oil)
    filename = "../data/Exxon_Assays/" + oil + "exxon_assay.xlsx"
    r = requests.get(url)
    if r.status_code == 200:
        open(filename, 'wb').write(r.content)
    else:
        print(f"Failed to download {oil} -- status code: {r.status_code}")




