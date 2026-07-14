import urllib.request
import re
import os
import datetime

FEEDS = [
    "https://mundoconectado.com.br/site/rss",
    "http://www.marvel616.com/feeds/posts/default?alt=rss",
    "https://www.rederpg.com.br/feed/",
    "http://bibliotecawod.blogspot.com/feeds/posts/default?alt=rss",
    "https://legadodamarvel.com.br/feed/",
    "https://multiversonoticias.com.br/feed/",
    "http://meiobit.com/index.xml",
    "http://macmagazine.com.br/feed/",
    "https://sociedadejedi.com.br/feed",
    "https://www.tudocelular.com/rss.asp",
    "http://mundotentacular.blogspot.com/feeds/posts/default?alt=rss",
    "https://olhardigital.com.br/rss",
    "https://www.gameblast.com.br/feeds/posts/default?alt=rss",
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

NEGATIVE_REGEX = re.compile(r'samsung|oneUI|one UI|futebol|copa|oppo|redmi|asus|kindle|jbl|huawei|google pixel|league of legends|leage of legends|funk|mega-sena|mega sena|quina|lotofácil|lotofacil|lotomania|dupla sena|timemania|super sete|loteca|loteria federal|loterias|galaxy', re.IGNORECASE)

ITEM_REGEX = re.compile(r'(?s)<item.*?>.*?</item>')
TITLE_REGEX = re.compile(r'(?s)<title.*?>(.*?)</title>')

XMLNS_REGEX = re.compile(r'xmlns:[a-zA-Z0-9_]+\s*=\s*[\'"][^\'"]+[\'"]')

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
all_valid_items = []
all_namespaces = {
    'media': 'xmlns:media="http://search.yahoo.com/mrss/"',
    'content': 'xmlns:content="http://purl.org/rss/1.0/modules/content/"',
    'dc': 'xmlns:dc="http://purl.org/dc/elements/1.1/"',
    'atom': 'xmlns:atom="http://www.w3.org/2005/Atom"',
    'thr': 'xmlns:thr="http://purl.org/syndication/thread/1.0"',
    'georss': 'xmlns:georss="http://www.georss.org/georss"',
    'slash': 'xmlns:slash="http://purl.org/rss/1.0/modules/slash/"',
    'wp': 'xmlns:wp="http://wordpress.org/export/1.1/"',
    'wfw': 'xmlns:wfw="http://wellformedweb.org/CommentAPI/"',
    'sy': 'xmlns:sy="http://purl.org/rss/1.0/modules/syndication/"',
    'itunes': 'xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"',
    'gml': 'xmlns:gml="http://www.opengis.net/gml"'
}

for url in FEEDS:
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode('utf-8', errors='ignore')
            
            namespaces = XMLNS_REGEX.findall(content)
            for ns in namespaces:
                match = re.match(r'xmlns:([a-zA-Z0-9_]+)\s*=', ns)
                if match:
                    prefix = match.group(1)
                    if prefix not in all_namespaces:
                        # Normalize quotes to double quotes for output
                        ns_clean = ns.replace("'", '"')
                        all_namespaces[prefix] = ns_clean
                        
            items = ITEM_REGEX.findall(content)
            for item in items:
                title_match = TITLE_REGEX.search(item)
                if title_match:
                    title_text = title_match.group(1).replace('<![CDATA[', '').replace(']]>', '').strip()
                    if not NEGATIVE_REGEX.search(title_text):
                        # Se não tiver tag oficial de thumbnail, caçamos a imagem no texto HTML
                        if not re.search(r'<enclosure|<media:content|<media:thumbnail', item, re.IGNORECASE):
                            img_matches = re.finditer(r'<img[^>]+src=["\']([^"\']+)["\']', item, re.IGNORECASE)
                            img_url = None
                            for match in img_matches:
                                url = match.group(1)
                                # Ignorar emojis e avatares
                                if 'gstatic.com' in url or 'avatar' in url or 'emoji' in url or '.gif' in url:
                                    continue
                                img_url = url
                                break
                            
                            if img_url:
                                # Injetar a tag enclosure forçando a imagem a ser a capa do card
                                enclosure_tag = f'\n    <enclosure url="{img_url}" type="image/jpeg" />\n  '
                                item = item.replace('</item>', f'{enclosure_tag}</item>')
                                
                        all_valid_items.append(item)
    except Exception as e:
        pass

namespaces_str = " ".join(all_namespaces.values())

rss_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" {namespaces_str}>
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
