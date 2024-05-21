# O que é?
Plataforma desenvolvida em React/Django para monitoramento da presença dos alunos do Cursinho Popular da Escola Politécnica da USP

# Configuração

## Localmente
- Instalar qualquer versão do Python 3.10
- Rodar o script `local_setup.bat` e seguir as instruções contidas

### Banco de Dados - PostgreSQL
- Baixar, no [site oficial](https://www.postgresql.org/download/), e instalar o PostgreSQL 16
- Criar, via pgAdmin4, uma base de dados com nome de sua preferência, ou utilizar a padrão chamada _postgres_
- Copiar o arquivo `.env.sample` e deletar o sufixo `.sample`, alterando os valores das variáveis para as escolhidas por você no momento de configuração do banco de dados
- Dentro da pasta `backend` rodar o comando `pipenv run python manage.py migrate`
- Rodar o serviço normalmente
