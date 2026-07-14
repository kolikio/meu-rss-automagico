# Projeto: RSS Automágico (Agregador Limpo)

## Contexto do Projeto
Este projeto é um agregador de feeds RSS em Python (`rss_merger.py`) criado para o Dan. Ele faz a leitura de 35 blogs de tecnologia/nerd, limpa as notícias com base em palavras-chave indesejadas (Regex) e gera um arquivo `feed_limpo.xml`.

## Arquitetura
- **Hospedagem:** GitHub Actions
- **Frequência:** A cada 5 minutos (`*/5 * * * *`) configurado no arquivo `.github/workflows/update_feed.yml`.
- **Repositório Externo:** https://github.com/kolikio/meu-rss-automagico
- **URL do Feed (Produção):** https://raw.githubusercontent.com/kolikio/meu-rss-automagico/main/feed_limpo.xml

## Regras de Atuação neste Workspace (Rules)
- **NÃO** altere a arquitetura para serviços na nuvem fechados ou soluções que exijam pagamento. O Dan prefere soluções locais, robustas ou de código aberto/gratuitas (como o GitHub Actions).
- Toda vez que o Dan pedir para adicionar uma nova URL ou palavra-chave bloqueada, faça a alteração no `rss_merger.py` usando as ferramentas de edição, faça o commit e o push (não precisa pedir permissão para o push, pois o projeto já está 100% automatizado).
- Mantenha a extração direta para não corromper CDATA e tags de imagem dos feeds originais.

## Histórico de Decisões
1. Abandonamos agregadores online (SiftRSS/RSSMix) porque limitam a quantidade de links e não puxam imagens direito.
2. Tentamos Home Assistant, mas abandonamos porque leitores em nuvem (como Inoreader) não enxergam IPs locais (192.168.x.x).
3. Consolidamos no GitHub Actions para ter URL pública irrestrita.
4. Apps de RSS descartados:
   - Feedly / Inoreader / Newsify: Tem anúncios ou cobram caro.
   - feeeed: Algoritmo bizarro que esconde posts antigos.
   - ReadKit: Cobra para adicionar URL customizada.
   - Unread: Não tem visualização por cards (só texto/lista).
   - Cupfeed: Cobra R$ 59,90 no Brasil (não é freemium real).
   - Your News: Visualização feia e sem cards de verdade.
   - Fiery Feeds: BANIDO/PROIBIDO. O usuário odeia profundamente. Nunca mais sugerir.
   - Ego Reader / NewsBlur: Rejeitados pelo visual feio.
   - Flipboard: Rejeitado porque no app de consumidor atual não permite mais colar URLs customizadas de RSS (só para publishers).
   - Reeder (novo e antigo): Letras pequenas sem opção de ajuste, ou pago.
   - Cappuccino: Deprecated/abandonado.
   - Plenary: Removido da App Store.
