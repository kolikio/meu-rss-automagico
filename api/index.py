from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qsl, urlsplit
import urllib.request
import re
from concurrent.futures import ThreadPoolExecutor

def fetch_og_image(url):
    """Acessa a URL da notícia e tenta extrair a imagem de capa (og:image)."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=3) as response:
            html = response.read().decode('utf-8', errors='ignore')
            # Procura pela meta tag og:image
            og = re.search(r'<meta[^>]*property=[\'"]og:image[\'"][^>]*content=[\'"]([^\'"]+)[\'"]', html, re.IGNORECASE)
            if not og:
                og = re.search(r'<meta[^>]*content=[\'"]([^\'"]+)[\'"][^>]*property=[\'"]og:image[\'"]', html, re.IGNORECASE)
            return og.group(1) if og else None
    except Exception:
        pass
    return None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = dict(parse_qsl(urlsplit(self.path).query))
        feed_url = query.get('url')
        
        if not feed_url:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Erro: O parametro 'url' e obrigatorio. Exemplo: /api?url=https://poltronanerd.com.br/feed/")
            return

        try:
            req = urllib.request.Request(feed_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.info().get('Content-Encoding') == 'gzip':
                    import gzip
                    content = gzip.decompress(response.read()).decode('utf-8', errors='ignore')
                else:
                    content = response.read().decode('utf-8', errors='ignore')
                
                # Conserta bug nativo do feed do Jovem Nerd
                content = content.replace('admin.jovemnerd.com.br', 'jovemnerd.com.br')
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Erro ao buscar o feed original: {e}".encode('utf-8'))
            return
            
        items = re.findall(r'(?s)<item.*?>.*?</item>', content)
        
        # Mapeia as noticias que precisam ter a capa extraida remotamente
        items_to_fetch = []
        
        for item in items:
            # Pula se ja possui enclosure, media:content ou media:thumbnail
            if re.search(r'<enclosure|<media:content|<media:thumbnail', item, re.IGNORECASE):
                continue
            
            # Tenta encontrar uma imagem perdida dentro do corpo HTML da noticia
            img_matches = re.finditer(r'<img[^>]+src=["\']([^"\']+)["\']', item, re.IGNORECASE)
            inline_img = None
            for match in img_matches:
                u = match.group(1)
                # Ignora tracking pixels, emojis e avatares
                if 'gstatic.com' not in u and 'avatar' not in u and 'emoji' not in u and '.gif' not in u:
                    inline_img = u
                    break
            
            if inline_img:
                # Injeta a imagem achada no HTML diretamente
                enclosure_tag = f'\n    <enclosure url="{inline_img}" length="0" type="image/jpeg" />\n  '
                new_item = item.replace('</item>', f'{enclosure_tag}</item>')
                content = content.replace(item, new_item)
            else:
                # Nao achou no HTML, entao pega o link original da materia para o scraper visitar
                link_match = re.search(r'<link>(.*?)</link>', item, re.IGNORECASE)
                if link_match:
                    link_url = link_match.group(1).replace('<![CDATA[', '').replace(']]>', '').strip()
                    items_to_fetch.append((item, link_url))

        # Executa as buscas na web em PARALELO usando multiplas threads para evitar timeout (10 seg max na Vercel)
        if items_to_fetch:
            with ThreadPoolExecutor(max_workers=10) as executor:
                urls = [tup[1] for tup in items_to_fetch]
                images = list(executor.map(fetch_og_image, urls))
                
            # Substitui as imagens processadas no XML final
            for (old_item, _), img_url in zip(items_to_fetch, images):
                if img_url:
                    enclosure_tag = f'\n    <enclosure url="{img_url}" length="0" type="image/jpeg" />\n  '
                    new_item = old_item.replace('</item>', f'{enclosure_tag}</item>')
                    content = content.replace(old_item, new_item)

        # Retorna o XML formatado e modificado pro leitor RSS (FeedFlow)
        self.send_response(200)
        self.send_header('Content-type', 'application/xml; charset=utf-8')
        # Cache reduzido para 60 segundos
        self.send_header('Cache-Control', 's-maxage=60, stale-while-revalidate')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))
