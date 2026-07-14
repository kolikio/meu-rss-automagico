import urllib.request
import re
import os
import datetime

FEEDS = [
    "https://mundoconectado.com.br/site/rss",
    "http://www.marvel616.com/feeds/posts/default",
    "https://www.rederpg.com.br/feed/",
    "http://bibliotecawod.blogspot.com/feeds/posts/default",
    "https://legadodamarvel.com.br/feed/",
    "https://multiversonoticias.com.br/feed/",
    "http://meiobit.com/index.xml",
    "http://macmagazine.com.br/feed/",
    "https://sociedadejedi.com.br/feed",
    "https://www.tudocelular.com/rss.asp",
    "http://mundotentacular.blogspot.com/feeds/posts/default",
    "https://olhardigital.com.br/rss",
    "https://www.gameblast.com.br/feeds/posts/default",
    "https://legadodadc.com.br/feed/",
    "https://feeds2.feedburner.com/oficinadanet_rss",
    "http://feeds.feedburner.com/tecnoblog",
    "http://feeds.feedburner.com/ovicio",
    "http://www.legiaodosherois.com.br/feed/",
    "https://jogaod20.com/feed/",
    "http://feeds.feedburner.com/planocritico",
    "https://feeds2.feedburner.com/canaltechbr",
    "https://universohq.com/feed/",
    "http://podcast.universohq.com/feed/",
    "https://www.showmetech.com.br/feed/",
    "https://manualdousuario.net/feed/",
    "https://br.ign.com/feed.xml",
    "https://jovemnerd.com.br/feed-completo",
    "https://www.b9.com.br/feed/",
    "https://www.hardware.com.br/feed/",
    "https://pipocamoderna.com.br/feed/",
    "https://seriemaniacos.tv/feed/",
    "https://poltronanerd.com.br/feed/",
    "https://coxinhanerd.com.br/feed/",
    "https://observatoriodocinema.uol.com.br/feed/",
    "https://startups.com.br/feed/"
]

NEGATIVE_REGEX = re.compile(r'samsung|oneUI|one UI|futebol|copa|oppo|redmi|asus|kindle|jbl|huawei|google pixel|league of legends|leage of legends|funk|mega-sena|mega sena|quina|lotofácil|lotofacil|lotomania|dupla sena|timemania|super sete|loteca|loteria federal|loterias', re.IGNORECASE)

ITEM_REGEX = re.compile(r'(?s)(<item.*?>.*?</item>|<entry.*?>.*?</entry>)')
TITLE_REGEX = re.compile(r'(?s)<title.*?>(.*?)</title>')

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
all_valid_items = []

for url in FEEDS:
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode('utf-8', errors='ignore')
            items = ITEM_REGEX.findall(content)
            for item in items:
                title_match = TITLE_REGEX.search(item)
                if title_match:
                    title_text = title_match.group(1).replace('<![CDATA[', '').replace(']]>', '').strip()
                    if not NEGATIVE_REGEX.search(title_text):
                        all_valid_items.append(item)
    except Exception as e:
        pass

rss_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Meu Feed Limpo e Turbinado</title>
    <link>https://github.com/</link>
    <description>Feed Consolidado hospedado no GitHub Actions</description>
    <lastBuildDate>{datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")}</lastBuildDate>
    {chr(10).join(all_valid_items)}
  </channel>
</rss>
"""

output_file = "feed_limpo.xml"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(rss_template)
