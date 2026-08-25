# Como colaborar no AFA Z

Este guia foi pensado para duas pessoas aprenderem Git e desenvolvimento web
enquanto evoluem o mesmo projeto.

## Antes de começar

Cada pessoa deve criar o próprio ambiente virtual e banco local. Nunca enviem:

- `.env`;
- `database.db`;
- `.venv/` ou `venv/`;
- `__pycache__/`;
- senhas, chaves ou dados pessoais.

O `.gitignore` já cobre esses arquivos, mas sempre confiram com `git status`.

## Fluxo recomendado

Atualize sua cópia da branch principal:

```powershell
git switch main
git pull
```

Crie uma branch com apenas uma finalidade:

```powershell
git switch -c feat-editar-tarefa
```

Durante o trabalho:

```powershell
git status
git diff
git add app.py templates/dashboard.html
git commit -m "feat: adiciona edição de tarefa"
git push -u origin feat-editar-tarefa
```

Depois, abram um Pull Request no GitHub e façam a leitura juntos antes de unir à
`main`.

## Padrão simples para commits

| Prefixo | Uso | Exemplo |
|---|---|---|
| `feat` | funcionalidade nova | `feat: adiciona busca de tarefas` |
| `fix` | correção | `fix: impede fechar dialog incorreto` |
| `style` | aparência sem mudar regra | `style: ajusta janela do diário` |
| `refactor` | reorganização interna | `refactor: separa consultas do painel` |
| `docs` | documentação | `docs: explica fluxo de autenticação` |
| `test` | testes | `test: cobre criação de categoria` |

Um commit deve responder: **qual mudança lógica este ponto representa?** Evitem
mensagens como `mudanças`, `teste` ou `atualização`.

## Divisão inicial sugerida

- Pessoa A: edição e exclusão de categorias.
- Pessoa B: edição, exclusão e reabertura de tarefas.

Essas áreas se encontram no dashboard, então combinem antes quais trechos cada
um alterará. Quando os dois precisarem do mesmo arquivo, façam commits menores
para reduzir conflitos.

## Antes de abrir um Pull Request

- [ ] Executei o app e testei o caminho alterado.
- [ ] Conferi `git diff`.
- [ ] Não incluí banco, `.env` ou ambiente virtual.
- [ ] Mantive a proteção por `usuario_id` nas consultas.
- [ ] Usei placeholders `?` em valores SQL.
- [ ] Atualizei comentários ou documentação se o fluxo mudou.
- [ ] O commit possui uma mensagem específica.

## Quando houver conflito

Não escolham automaticamente “aceitar tudo”. Leiam as duas versões e montem a
versão final que preserve a intenção de ambas. Depois testem novamente antes do
commit que resolve o conflito.
