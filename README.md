# AFA Z

> Um espaço retrô e personalizável para tarefas, foco e registro de progresso.

O nome **AFA Z** vem do trocadilho com “a fazer”. O projeto começou como um
To-Do em Flask e está evoluindo para um ambiente no qual uma tarefa concluída
não simplesmente desaparece: ela pode gerar uma reflexão, entrar no diário do
dia e, futuramente, voltar como revisão.

Este é também um projeto de aprendizagem. O código prioriza clareza, comentários
e decisões que possam ser discutidas por quem está estudando Python e web.

## Estado atual

- cadastro e login com senha armazenada como hash;
- sessões de usuário;
- categorias isoladas por usuário;
- criação e conclusão de tarefas;
- feedback sobre o que foi aprendido e o que precisa de revisão;
- diário automático com as conclusões do dia;
- interface inspirada em janelas de sistema;
- 11 paletas selecionáveis;
- fonte Minecraft incorporada localmente;
- layout responsivo.

## Tecnologias

- Python
- Flask
- SQLite
- Jinja2
- HTML e CSS
- JavaScript sem framework

## Estrutura

```text
AFA Z/
├── app.py                    # rotas, sessão e regras da aplicação
├── database.py               # conexão, tabelas e migrações simples
├── database.db               # banco local; não deve ir para o Git
├── requirements.txt          # dependências Python
├── .env.example              # modelo das variáveis locais
├── .gitignore                # arquivos que o Git deve ignorar
├── CONTRIBUTING.md           # fluxo de trabalho para colaboradores
├── docs/
│   ├── GUIA_DO_CODIGO.md     # leitura guiada do projeto
│   └── ROADMAP.md            # direção planejada do produto
├── templates/
│   ├── base.html             # esqueleto herdado por todas as páginas
│   ├── login.html
│   ├── cadastro.html
│   ├── dashboard.html
│   ├── categoria.html        # compatibilidade; a rota hoje redireciona
│   └── feedback.html
└── static/
    ├── css/
    │   ├── themes.css        # paletas e variáveis semânticas
    │   └── style.css         # layout e aparência dos componentes
    ├── fonts/                # fonte Minecraft e licença OFL
    └── js/app.js             # temas, relógio e janelas <dialog>
```

## Como executar no Windows

Abra o PowerShell dentro da pasta do projeto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
```

Copie a chave exibida, abra `.env` e substitua o valor de `SECRET_KEY`. Depois:

```powershell
python app.py
```

Acesse `http://127.0.0.1:5000` no navegador.

Se o PowerShell bloquear a ativação do ambiente virtual, libere scripts apenas
para a janela atual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Por onde começar a ler

1. Abra [`docs/GUIA_DO_CODIGO.md`](docs/GUIA_DO_CODIGO.md).
2. Leia `database.py` para conhecer os dados.
3. Leia uma rota simples, como `nova_categoria()` em `app.py`.
4. Encontre o formulário correspondente em `templates/dashboard.html`.
5. Faça uma alteração pequena e acompanhe o resultado no navegador.

## Visão do projeto

O diferencial pretendido não é ser apenas um To-Do com uma aparência retrô. O
AFA Z deve conectar este ciclo:

```text
tarefa → foco → conclusão → reflexão → diário → revisão futura
```

Ele deve continuar útil para estudo, programação, projetos pessoais e outros
contextos, sem presumir por que cada pessoa está usando suas categorias.

Consulte [`docs/ROADMAP.md`](docs/ROADMAP.md) para a sequência sugerida.

## Fonte e licença

Os arquivos `Minecraft.otf` e `Minecraft-Bold.otf` são do projeto aberto
**Minecraft Font**, de Idrees Hassan. A licença OFL acompanha os arquivos em
`static/fonts/OFL-Minecraft-Font.txt`.

A licença do código do AFA Z ainda deve ser escolhida antes de uma distribuição
pública definitiva.
