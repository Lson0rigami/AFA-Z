# Roadmap do AFA Z

O roadmap é uma direção, não uma lista imutável. Uma versão só deve avançar
quando a anterior estiver estável e compreendida pelos colaboradores.

## Princípios

- interface retrô, mas comportamento moderno;
- uso rápido e sem textos que expliquem o óbvio;
- personalização sem sacrificar legibilidade;
- cada dado pertence ao usuário correto;
- tarefas concluídas devem alimentar memória e revisão;
- recursos novos entram apenas quando resolvem um problema real.

## Sequência sugerida

### 0.2 — Núcleo confiável

- editar e excluir tarefas;
- editar e excluir categorias;
- reabrir tarefa concluída;
- confirmação antes de exclusões;
- mensagens de erro na própria interface;
- tratar tentativa de cadastro com e-mail repetido;
- adicionar proteção CSRF;
- testes automatizados das rotas principais.

### 0.3 — Personalização

- editor de paleta usando variáveis semânticas;
- importar e exportar temas;
- controlar fonte, sombras e densidade;
- salvar posição e tamanho das janelas;
- sons opcionais e originais.

### 0.4 — Diário

- nota livre para cada dia;
- navegação entre datas;
- histórico de tarefas concluídas;
- pesquisa no diário;
- mover uma pendência para outro dia.

### 0.5 — Revisões

- transformar “o que precisa ser revisado” em item de revisão;
- reapresentar em intervalos configuráveis;
- registrar se o assunto ficou claro;
- visualizar assuntos compreendidos, em revisão ou não iniciados.

### 0.6 — Foco

- cronômetro ligado à tarefa;
- pausas;
- histórico de sessões;
- estatísticas sem pontuação ou cobrança artificial.

### 0.7 — Uso rápido

- central de comandos;
- atalhos de teclado;
- pesquisa global;
- ações sem depender do mouse.

### 1.0 — Publicação

- layout final estável;
- documentação completa;
- licença definida;
- aplicação instalável como PWA;
- estratégia de backup e recuperação;
- implantação pública com configuração segura.

## O que evitar

- adicionar gamificação apenas por aparência;
- copiar imagens, músicas ou sons protegidos de jogos;
- criar muitas telas antes de completar editar e excluir;
- misturar regras de banco dentro dos templates;
- guardar preferências essenciais somente no navegador sem planejar sincronização;
- tentar implementar todas as versões ao mesmo tempo.
