# 🤖 Assistente Financeiro IA

Sistema de chat com IA especializada em finanças pessoais, desenvolvido com foco em **segurança**, **performance** e **boas práticas**.

## ✨ Funcionalidades

- **Múltiplos Chats**: Contexto separado por conversa
- **IA Especializada**: Assistente financeiro brasileiro
- **Segurança**: Rate limiting, validação, sanitização XSS
- **Performance**: Connection pooling, context managers
- **Arquitetura**: Separação de responsabilidades (MVC)

## 🔒 Recursos de Segurança

- **Rate Limiting**: Proteção contra spam e ataques
- **Validação de Entrada**: Sanitização de dados
- **Headers de Segurança**: Proteção contra ataques comuns
- **Sessões Seguras**: Cookies HTTPOnly e Secure
- **Logging**: Monitoramento de erros e atividades

## 🚀 Instalação

### 1. Clonar e Configurar
```bash
git clone <repo>
cd projeto-IA-py
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configurar Banco
```bash
mysql -u root -p -e "CREATE DATABASE projeto_ia;"
mysql -u root -p projeto_ia < database_setup.sql
```

### 3. Variáveis de Ambiente
```bash
cp .env.example .env
# Edite o .env com suas configurações
```

### 4. Executar
```bash
python app.py
```

## 📁 Arquitetura

```
projeto-IA-py/
├── app.py              # Aplicação Flask (Controllers)
├── config.py           # Configurações centralizadas
├── database.py         # Gerenciador de conexões
├── models.py           # Modelos de dados
├── services.py         # Lógica de negócio
├── templates/          # Templates HTML
├── requirements.txt    # Dependências
└── database_setup.sql  # Schema do banco
```

## 🛡️ Padrões de Segurança Implementados

- **OWASP Top 10** compliance
- **SQL Injection** prevention (prepared statements)
- **XSS Protection** (sanitização de entrada/saída)
- **CSRF Protection** (Flask built-in)
- **Rate Limiting** (Flask-Limiter)
- **Input Validation** (comprimento, caracteres)
- **Error Handling** (logs seguros, mensagens genéricas)
- **Session Security** (HTTPOnly, Secure, SameSite)

## 📊 Performance

- **Connection Pooling**: Reutilização de conexões DB
- **Context Managers**: Gerenciamento automático de recursos
- **Prepared Statements**: Cache de queries
- **Logging Estruturado**: Monitoramento eficiente
- **Rate Limiting**: Proteção contra sobrecarga

## 🔧 APIs

| Endpoint | Método | Descrição | Rate Limit |
|----------|--------|-----------|------------|
| `/api/novo-chat` | POST | Criar chat | 10/min |
| `/api/chat/{id}/mensagens` | GET | Listar mensagens | 30/min |
| `/api/chat/{id}` | POST | Enviar mensagem | 20/min |
| `/api/chat/{id}` | DELETE | Deletar chat | 10/min |

## 🧪 Qualidade de Código

- **Separação de Responsabilidades**: Models, Services, Controllers
- **Type Hints**: Tipagem estática
- **Error Handling**: Tratamento robusto de exceções
- **Logging**: Rastreabilidade completa
- **Validação**: Entrada e saída de dados
- **Documentação**: Docstrings e comentários

## 📈 Monitoramento

- **Logs Estruturados**: Formato padronizado
- **Error Tracking**: Captura de exceções
- **Performance Metrics**: Tempo de resposta
- **Security Events**: Tentativas de ataque