# Política de Segurança

## Suporte de versões

Como este projeto está em evolução, a política padrão é dar suporte prioritário à versão principal mais recente presente na branch `main`.

## Como reportar uma vulnerabilidade

Se você identificar uma vulnerabilidade, **não publique detalhes sensíveis em issue pública**.

Prefira um contato privado com o mantenedor do projeto e inclua:

- descrição da falha
- impacto potencial
- passos para reprodução
- sugestão de mitigação, se houver

## Itens sensíveis neste projeto

Preste atenção especial a:

- `BRAPI_API_KEY`
- endpoints de produção
- segredos de cloud/deploy
- configuração do Expo/EAS
- headers CORS e autenticação futura

## Boas práticas mínimas

- nunca commitar `.env`
- nunca expor tokens no frontend
- revisar logs antes de publicá-los
- validar qualquer integração de produção antes de abrir acesso público

## SLA informal

Ao receber um reporte válido, a expectativa é:

- confirmação inicial do recebimento
- triagem da severidade
- correção ou mitigação em prazo razoável

Como este é um projeto de portfólio/MVP, o tempo de resposta pode variar.
