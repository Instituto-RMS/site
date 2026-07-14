# TODO — Rio Maker Space website

> Lista de pendências para tirar o site do "funciona na minha máquina" para produção confiável.
> Itens marcados como `[CRIT]` são blockers para go-live; o resto é polimento ou evolução.

---

## 1. Repositório e hospedagem (o que você já pediu)

- [ ] **Trocar o remote `origin`**: ainda aponta para `https://github.com/st1020/kita.git`.
  - Criar repo próprio no GitHub (ex: `RIO-MAKER-SPACE/site` ou `RIO-MAKER-SPACE-GIT/site`).
  - Rodar `git remote set-url origin https://github.com/ORG/site.git` e fazer push.
- [ ] **Remover `.env` do histórico do Git** se ele contiver token real.
  - `git rm --cached .env` e commitar.
  - Se o token já foi exposto, **revogar e regenerar** o token no Notion.
- [ ] **Adicionar `.github/workflows/`** para CI/CD:
  1. Trigger em `push`/`pull_request` na `main`.
  2. Job que roda `scripts/sync_notion.py` (com secrets `NOTION_TOKEN`, `NOTION_PROJECTS_DB_ID`, `NOTION_EVENTS_DB_ID`).
  3. Job que roda `bun install && bun run build` e `zola build`.
  4. Job extra: `zola check` (verifica links internos quebrados).
  5. Deploy para GitHub Pages / Cloudflare Pages / Vercel / Netlify / outro.
- [ ] **Definir provedor de hospedagem** e configurar:
  - Domínio customizado `riomakerspace.com.br`.
  - HTTPS automático.
  - Build command: `bun install && bun run build && zola build`.
  - Variáveis de ambiente/Secrets do Notion.

---

## 2. Segurança e secrets

- [ ] **Nunca commitar `.env` nem tokens**.
  - `.env` já deve ser ignorado pelo `.gitignore` (verificar).
  - Usar `.env.local` para overrides pessoais (ver seção "Esquema .local" abaixo).
- [ ] **Rotacionar `NOTION_TOKEN` se já foi commitado**.
- [ ] **Restringir o escopo do token** no Notion Integration:
  - Apenas leitura dos databases necessários.
  - Sem acesso a usuários/workspace além do necessário.
- [ ] **Adicionar secret detection no CI** (GitHub `secret-scanning` ou similar).

---

## 3. Notion sync — robustez

- [ ] **Download de imagens e anexos do Notion**.
  - URLs de arquivos Notion expiram (~1h). O sync deve baixar para `static/notion/` e reescrever os links no markdown.
  - Mapear `files`, `images`, `external` blocks e rich-text mentions.
- [ ] **Criar `_index.md` automaticamente**? Hoje os `_index.md` são manuais.
- [ ] **Suporte a deletes/renames**.
  - O sync já remove `.md` que não estão mais publicados; confirmar que isso não apaga rascunhos manuais por engano.
- [ ] **Adicionar retry + timeout** nas chamadas à API do Notion.
- [ ] **Tratamento de erros**: se a API falhar, o CI deve falhar com mensagem clara.
- [ ] **Logging estruturado**: JSON lines para facilitar leitura no CI.
- [ ] **Testar sync em modo dry-run** opcional para validar schema antes de escrever arquivos.
- [ ] **Documentar schema das databases** (quais propriedades `Nome`, `Publicar`, `Status`, `Tags`, `Destaque`, `Início`, `Data`, `Local`, `Público`, `Parceiros`, `Link externo`). Atualizar `AGENTS.md`.

---

## 4. Build e qualidade

- [ ] **Adicionar `zola check` no CI** para detectar links internos quebrados.
- [ ] **Adicionar validação do front matter** (opcional, pode ser um script Python simples).
- [ ] **Verificar build em ambiente limpo** (sem `public/` pré-existente, sem `.env` local).
- [ ] **Cache de dependências no CI**: `~/.bun/install/cache` e `~/.cache/pip`.
- [ ] **Proteger a branch `main`**: exigir PR + checks passando.

---

## 5. SEO, performance e metadados

- [ ] **Criar `static/robots.txt`**.
  - Permitir tudo; apontar sitemap.
- [ ] **Habilitar `generate_feed` / sitemap no `zola.toml`**.
  - Adicionar `generate_feeds = true` e `feed_filenames = ["atom.xml", "rss.xml"]`.
  - Zola gera `sitemap.xml` automaticamente se `generate_sitemap = true`.
- [ ] **Criar imagem social/Open Graph real** (`static/images/social.png`, 1200×630).
  - Descomentar `social_image` no `zola.toml`.
- [ ] **Revisar `<title>` e `<meta name="description">`** em todas as páginas.
- [ ] **Adicionar Schema.org/LD-JSON** para Organization, Event, Project (opcional, ajuda SEO).
- [ ] **Favicon e touch icon reais**.
  - O `favicon.ico` e `apple-touch-icon.png` ainda parecem genéricos do tema Kita.
  - Gerar a partir do `RMS-logo.png`.
- [ ] **Verificar performance mobile** no PageSpeed Insights.
- [ ] **Lazy loading de imagens** e `width`/`height` nos cards.

---

## 6. Conteúdo e UX

- [ ] **Página de Equipe/Colaboradores** (opcional).
- [ ] **Página de Contato/FAQ** com formulário ou apenas links.
- [ ] **Adicionar links reais** de WhatsApp, Instagram e LinkedIn no `zola.toml`.
- [ ] **Adicionar CTA de inscrição em eventos** se houver link de formulário.
- [ ] **Melhorar 404**: hoje é só "404" gigante. Adicionar mensagem amigável e link para home.
- [ ] **Remover conteúdo de demo** quando o conteúdo real estiver completo:
  - `content/shortcodes/index.md` (demo de shortcodes do tema Kita).
  - `static/images/markdown-syntax.png` (imagem demo).
  - `static/giallo-dark.css` / `giallo-light.css` se não forem usados.
- [ ] **Adicionar menu "Arquivo"?** O `pages/archive.md` existe mas não está no menu.
- [ ] **Revisar textos do `theme.toml`**: ainda credita Kita/st1020. Manter atribuição é correto, mas atualizar `name`/`description` se quiser.

---

## 7. Analytics e monitoramento

- [ ] **Adicionar analytics leve** (Plausible, Fathom, Google Analytics 4, etc.) via inject `templates/injects/head.html`.
- [ ] **Monitorar uptime** (UptimeRobot, Better Uptime, etc.) após deploy.
- [ ] **Verificar logs de build** do host escolhido.

---

## 8. Acessibilidade e legal

- [ ] **Auditoria de acessibilidade** (axe/Lighthouse).
- [ ] **Verificar contraste de cores** (verde `#adf758` sobre fundo escuro pode passar, mas validar).
- [ ] **Adicionar política de privacidade** se usar analytics/forms.
- [ ] **Verificar se precisa de página de "Termos de Uso"** para conteúdo open source.

---

## 9. Esquema de extensão `.local` (ver `AGENTS.md` / scripts)

- [ ] **Usar `.env.local` + `sync_notion.local.py`** para customizações locais sem commitar.
  - Já implementado; manter documentado.
- [ ] **Carregar `.env.local` no CI?** Não — CI deve usar secrets, nunca arquivo local.

---

## 10. Backlog / ideias futuras

- [ ] **Calendário de eventos** (iCal / subscribe).
- [ ] **Newsletter** (Buttondown, Mailchimp, etc.).
- [ ] **Busca no site** (Pagefind ou Stork).
- [ ] **Tag cloud / filtros** em projetos e eventos.
- [ ] **Página de "Como apoiar" / doações / patrocínio**.
- [ ] **Multilíngue** (inglês) se quiser alcance internacional.

---

## Observações rápidas

- O **sync do Notion já está funcionando** e gera Markdown em `content/projects/` e `content/events/`.
- O **design da home está bem avançado** (hero, números, serviços, pilares, destaques, agenda, parceiros, CTAs).
- A maior dor agora é **colocar isso em produção de forma segura e automática**.
