# Vital Pragas - Controle de Estoque e Patrimônio

Sistema web em Flask com SQLite para:
- controle de estoque
- inventário
- cadastro de funcionários
- saída e devolução de produtos
- controle de equipamentos
- entrega com assinatura digital no tablet
- manutenção de equipamentos
- relatórios com impressão

## Acesso inicial
- usuário: admin
- senha: admin123

## Como rodar localmente
1. Instale Python 3.11+
2. No terminal, entre na pasta do projeto
3. Crie um ambiente virtual
4. Instale as dependências:
   pip install -r requirements.txt
5. Execute:
   python app.py
6. Abra no navegador:
   http://127.0.0.1:5000

## Banco de dados
- padrão: SQLite local no arquivo app.db
- o banco é criado automaticamente na primeira execução

## Publicação simples
### Render
1. Suba este projeto para um repositório GitHub
2. Crie um novo Web Service na Render
3. Configure:
   - Build Command: pip install -r requirements.txt
   - Start Command: gunicorn app:app
4. Adicione gunicorn ao requirements.txt se desejar publicar na Render
5. Faça o deploy

### Railway
1. Suba no GitHub
2. Crie um projeto no Railway
3. Selecione o repositório
4. Configure start command como:
   gunicorn app:app

## Observações
- Para uso real em produção com múltiplos acessos simultâneos, o ideal é trocar SQLite por PostgreSQL.
- A assinatura é capturada em base64 e salva no banco.
- A impressão usa o próprio navegador.
