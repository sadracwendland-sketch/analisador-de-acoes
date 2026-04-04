# Guia de Contribuição

Obrigado por considerar contribuir com o **Stock Analyzer Pro**.

Este projeto foi estruturado para funcionar como base de produto, portfólio técnico e laboratório de evolução para analytics financeiro. Para manter a qualidade do repositório, siga as orientações abaixo.

---

## Como contribuir

Você pode contribuir com:

- correções de bugs
- melhorias de UX/UI
- otimizações de performance
- novos indicadores técnicos
- melhorias no pipeline de forecast
- testes automatizados
- documentação
- DevOps / CI/CD

---

## Fluxo recomendado

1. Faça um **fork** do projeto
2. Crie uma branch descritiva
3. Faça commits pequenos e objetivos
4. Teste localmente antes de abrir o PR
5. Abra um Pull Request com contexto claro

Exemplo:

```bash
git checkout -b feat/add-stochastic-indicator
```

---

## Padrão de branches

Sugestões:

- `feat/...` para novas funcionalidades
- `fix/...` para correções
- `docs/...` para documentação
- `refactor/...` para refatoração
- `ci/...` para pipeline e automação
- `test/...` para testes

---

## Convenção de commits

Exemplos:

```text
feat: add MACD histogram card
fix: handle empty CDI response
refactor: split risk engine into service layer
docs: improve deployment guide
ci: add github actions workflow
```

---

## Checklist antes do Pull Request

Antes de abrir o PR, confira se:

- [ ] o código roda localmente
- [ ] a feature foi implementada de forma isolada
- [ ] não há segredos no código
- [ ] o README continua coerente
- [ ] variáveis novas foram documentadas
- [ ] mudanças visuais relevantes foram descritas
- [ ] o PR explica claramente o problema e a solução

---

## Ambiente local

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Web

```bash
cd web
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Mobile

```bash
cd mobile
npm install
npx expo start
```

---

## Diretrizes técnicas

### Backend
- manter serviços desacoplados em `backend/app/services`
- evitar lógica pesada diretamente nas rotas
- documentar novos campos de resposta
- preferir funções pequenas e testáveis

### Web
- manter foco em responsividade
- evitar quebrar experiência mobile
- preservar clareza visual dos KPIs

### Mobile
- priorizar componentes touch-friendly
- manter interface estável em Android e iOS
- evitar acoplamento de segredo/API key no cliente

---

## Issues

Ao abrir uma issue, tente incluir:

- contexto do problema
- passos para reproduzir
- comportamento esperado
- comportamento atual
- prints ou logs, se necessário

---

## Pull Requests

Ao abrir um PR:

- descreva o problema
- explique a solução
- liste impactos técnicos
- informe riscos conhecidos
- anexe imagens se houver alteração visual

---

## Segurança

Se a contribuição envolver:

- credenciais
- tokens
- autenticação
- permissões
- exposição de dados

consulte primeiro o arquivo `SECURITY.md`.

---

## Licença

Ao contribuir, você concorda que sua contribuição será disponibilizada sob a licença do projeto.
