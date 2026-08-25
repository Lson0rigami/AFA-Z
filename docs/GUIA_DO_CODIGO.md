# Guia do código do AFA Z

Este documento é o mapa para quem abriu o projeto pela primeira vez. Ele não
substitui a leitura do código: mostra **em qual ordem ler**, como os arquivos se
conectam e onde procurar quando alguma coisa não funcionar.

## 1. Modelo mental do projeto

Uma ação normalmente percorre este caminho:

```text
navegador
   ↓ envia GET ou POST
rota em app.py
   ↓ lê sessão e formulário
consulta em database.db
   ↓ devolve linhas ou salva alterações
template Jinja em templates/
   ↓ gera HTML
CSS e JavaScript em static/
   ↓
tela do usuário
```

O Flask é o intermediário. O navegador não acessa o SQLite diretamente, e o
banco não conhece HTML.

## 2. Ordem recomendada de leitura

### Primeiro: `database.py`

Leia quais tabelas existem e como elas se relacionam. Sem conhecer os dados,
consultas com `JOIN` em `app.py` parecem mais difíceis do que são.

### Segundo: `app.py`

Comece por uma rota pequena:

1. `home()`;
2. `nova_categoria()`;
3. `login()`;
4. `nova_tarefa()`;
5. `dashboard()`;
6. `concluir_tarefa()`;
7. `feedback_tarefa()`.

Não comece pela consulta do diário: ela é o trecho SQL mais avançado do projeto.

### Terceiro: `templates/base.html`

Entenda os blocos do Jinja e depois abra `login.html`. Veja como uma página filha
herda a estrutura geral sem repetir `<head>`, seletor de temas ou scripts.

### Quarto: `templates/dashboard.html`

Compare cada variável usada no template com os valores enviados no
`render_template()` da rota `dashboard()`.

### Quinto: arquivos estáticos

- `themes.css`: valores das paletas;
- `style.css`: formato e posição dos elementos;
- `app.js`: comportamentos executados no navegador.

## 3. As tabelas do banco

```text
usuarios (1)
    └── (N) categorias (1)
             └── (N) tarefas (1)
                      └── (N) feedback
```

| Tabela | Responsabilidade | Ligação |
|---|---|---|
| `usuarios` | identidade e senha protegida | tabela principal |
| `categorias` | agrupamento das tarefas | `usuario_id` |
| `tarefas` | ação, descrição, estado e datas | `categoria_id` |
| `feedback` | reflexão após conclusão | `tarefa_id` |

Uma categoria possui `usuario_id`, mas uma tarefa não. Para descobrir o dono de
uma tarefa, percorremos:

```text
tarefa → categoria → usuário
```

Esse é o motivo dos `JOIN` usados nas rotas protegidas.

## 4. Anatomia de uma rota

Observe a criação de categoria de forma reduzida:

```python
@app.route("/categoria/nova", methods=["POST"])
def nova_categoria():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    nome_categoria = request.form["nome_categoria"]

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO categorias (usuario_id, nome) VALUES (?, ?)",
        (session["usuario_id"], nome_categoria)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))
```

Ela possui quatro responsabilidades:

1. verificar autenticação;
2. receber o campo HTML;
3. salvar com o usuário correto;
4. redirecionar depois do POST.

Quando forem criar uma rota nova, procurem essas mesmas etapas.

## 5. GET e POST

`GET` pede ou exibe uma informação. Exemplos:

- abrir o login;
- abrir o dashboard;
- selecionar uma categoria.

`POST` envia uma alteração. Exemplos:

- cadastrar;
- criar tarefa;
- concluir tarefa;
- salvar feedback.

Não usem uma rota GET para excluir ou alterar dados. Um link pode ser visitado
automaticamente por navegador, histórico ou ferramenta de pré-visualização.

## 6. Formulário: do HTML ao Python

No template:

```html
<input name="titulo">
```

Na rota:

```python
titulo = request.form["titulo"]
```

O atributo `name`, não o `id`, é a chave que aparece em `request.form`.

Use:

```python
request.form["titulo"]
```

quando o campo é obrigatório, e:

```python
request.form.get("descricao", "")
```

quando ele pode não existir ou ficar vazio.

## 7. Placeholders SQL

O projeto usa:

```python
cursor.execute(
    "SELECT * FROM usuarios WHERE email = ?",
    (email,)
)
```

O `?` separa o comando SQL do valor enviado pelo usuário. Isso evita problemas
com aspas e reduz o risco de SQL Injection.

O valor fica em uma tupla. Quando existe apenas um valor, a vírgula importa:

```python
(email,)  # tupla com um elemento
(email)   # apenas o próprio valor, sem tupla
```

Nunca montem SQL assim:

```python
f"SELECT * FROM usuarios WHERE email = '{email}'"
```

## 8. `commit()`, `fetchone()` e `fetchall()`

- `fetchone()` pega uma linha ou devolve `None`;
- `fetchall()` devolve uma lista com todas as linhas;
- `commit()` confirma `INSERT`, `UPDATE`, `DELETE` ou alteração de tabela;
- `close()` libera a conexão.

Um `SELECT` não precisa de `commit()` porque não modifica dados.

## 9. Sessão e isolamento entre usuários

Após o login:

```python
session["usuario_id"] = usuario["id"]
```

Nas outras rotas:

```python
if "usuario_id" not in session:
    return redirect(url_for("login"))
```

Isso confirma que há uma conta logada, mas não basta. Toda consulta que acessa
um objeto específico também deve confirmar que ele pertence à conta:

```sql
WHERE categorias.id = ? AND categorias.usuario_id = ?
```

Sem isso, alguém poderia trocar um número na URL ou no HTML para acessar dados
de outra pessoa. Essa vulnerabilidade recebe o nome de **IDOR**.

## 10. Partes mais complexas do dashboard

### Categoria ativa

```python
categoria_ativa = next(
    (categoria for categoria in categorias if categoria["id"] == categoria_id),
    categorias[0] if categorias else None
)
```

O gerador procura uma categoria cujo ID corresponde à URL. O segundo argumento
de `next()` é o valor padrão: primeira categoria ou `None`.

Uma versão mais longa, útil para entender, seria:

```python
categoria_ativa = None

for categoria in categorias:
    if categoria["id"] == categoria_id:
        categoria_ativa = categoria
        break

if categoria_ativa is None and categorias:
    categoria_ativa = categorias[0]
```

As duas produzem o mesmo resultado.

### Pendentes antes das concluídas

```sql
ORDER BY
    CASE WHEN status = 'pendente' THEN 0 ELSE 1 END,
    data_criacao DESC
```

O `CASE` transforma temporariamente cada estado em um número para ordenar. As
pendentes recebem `0` e vêm antes das demais, que recebem `1`.

### Feedback mais recente

A subconsulta dentro do `LEFT JOIN` procura o maior ID de feedback daquela
tarefa. `LEFT JOIN` é usado porque uma tarefa concluída pode existir por alguns
instantes sem feedback, enquanto o usuário ainda está preenchendo a tela.

## 11. Migração simples do banco

`CREATE TABLE IF NOT EXISTS` cria uma tabela nova, mas não adiciona coluna a uma
tabela antiga. `database.py` consulta:

```sql
PRAGMA table_info(tarefas)
```

e executa `ALTER TABLE` apenas quando a coluna não existe. Isso permitiu adicionar
`data_conclusao` sem apagar o banco anterior.

Conforme o projeto crescer, vale estudar uma ferramenta própria de migrações,
como Alembic ou Flask-Migrate. Neste estágio, a solução explícita ajuda a
entender o que realmente acontece no SQLite.

## 12. Herança dos templates

Uma página filha começa com:

```jinja2
{% extends "base.html" %}
```

E preenche regiões declaradas pelo arquivo mestre:

```jinja2
{% block content %}
    ...conteúdo da página...
{% endblock %}
```

`base.html` concentra elementos compartilhados. Se precisarem adicionar um
arquivo JavaScript usado em todas as telas, façam isso uma vez no `base.html`.

## 13. Temas

`themes.css` declara oito posições por paleta. No final do arquivo, essas
posições são associadas a funções:

```css
--ui-background: var(--palette-1);
--ui-accent: var(--palette-7);
--ui-text: var(--palette-8);
```

`style.css` usa somente funções:

```css
background: var(--ui-background);
color: var(--ui-text);
```

Assim, trocar de tema não exige alterar as regras de componentes.

`app.js` altera o atributo:

```html
<html data-theme="hollow">
```

e salva a escolha no `localStorage` do navegador.

## 14. Janelas `<dialog>`

Os botões possuem o ID da janela no atributo:

```html
<button data-dialog-target="new-task">+</button>
```

O JavaScript encontra:

```html
<dialog id="new-task">
```

e chama `showModal()`. A regra abaixo é essencial:

```css
dialog.window:not([open]) {
    display: none;
}
```

Sem ela, o `display: flex` da classe `.window` manteria um diálogo fechado
visível. Esse foi um bug real encontrado durante o desenvolvimento.

## 15. Onde adicionar cada tipo de mudança

| Mudança | Primeiro lugar para procurar |
|---|---|
| nova tabela ou coluna | `database.py` |
| nova URL ou regra | `app.py` |
| novo formulário ou informação | `templates/` |
| tamanho, posição ou aparência | `style.css` |
| nova paleta | `themes.css` e `base.html` |
| clique, relógio ou comportamento no navegador | `app.js` |
| direção futura | `docs/ROADMAP.md` |

## 16. Como investigar um erro

### O formulário não envia o valor

1. Confira o `name` no HTML.
2. Confira a chave de `request.form`.
3. Veja se o `method` é POST.
4. Veja se o `action` aponta para a rota certa.

### A página não encontra uma variável

1. Localize onde o template é renderizado.
2. Confira se a variável foi passada em `render_template()`.
3. Confira se o nome é idêntico no Python e no Jinja.

### O dado não fica salvo

1. Verifique se o SQL executou.
2. Confirme se existe `conn.commit()`.
3. Confirme se o app e a ferramenta de banco estão abrindo o mesmo arquivo.

### Uma janela não fecha

1. Abra o Console do navegador com `F12`.
2. Procure erros em `app.js`.
3. Confira `data-close-dialog`.
4. Confira se o `<dialog>` possui o atributo `open` naquele momento.

## 17. Exercícios seguros para começar

Façam um exercício por branch e por commit:

1. trocar um texto da barra de status;
2. criar uma nova paleta;
3. mostrar a data de criação ao lado da tarefa;
4. adicionar uma mensagem quando o diário estiver vazio;
5. tratar espaços no começo e no fim de um título com `.strip()`;
6. impedir categoria com nome vazio após `.strip()`;
7. implementar edição de categoria;
8. implementar edição de tarefa.

Os seis primeiros são menores. Edição e exclusão envolvem novas rotas, formulários
e validação de proprietário, então devem vir depois.

## 18. Regra para comentários futuros

Comentem decisões, riscos e relações que não são óbvias:

```python
# Confirma o dono porque categoria_id veio do navegador e pode ser alterado.
```

Evitem repetir literalmente a linha seguinte:

```python
# Fecha a conexão.
conn.close()
```

Um bom comentário explica **por que o código existe**, não apenas traduz sua
sintaxe para português.
