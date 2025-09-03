# Monte Carlo Forecast API

Esta aplicação realiza simulações de Monte Carlo para prever o número de semanas necessárias para concluir um backlog, utilizando dados históricos de throughput. A API foi desenvolvida com FastAPI, validação de dados com Pydantic e inclui testes automatizados.

---

## Instalação

1. **Instale as dependências**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## Configuração

- Os arquivos principais estão organizados em:
  - `main.py`: inicialização da API FastAPI
  - `forecast_routes.py`: rotas da API
  - `models/models.py`: validação dos dados de entrada
  - `services/forecast.py`: lógica de simulação
  - `services/unit_tests.py`: testes unitários

---

## Como subir a API

### Usando Docker

1. **Construa e suba o container**
   ```bash
   docker-compose up --build
   ```
   O servidor estará disponível em [http://localhost:8000](http://localhost:8000).

### Usando Python localmente


## Como utilizar

### Endpoint principal

- **POST** `/forecast/create-simulation`

#### Exemplo de requisição

```json
{
  "nr_simulations": 1000,
  "backlog_min": 10,
  "backlog_max": 20,
  "throughput": [2, 3, 4, 5]
}
```

#### Exemplo de resposta

```json
{
  "Backlog-min": 10,
  "Backlog-max": 20,
  "Throughput": [2, 3, 4, 5],
  "Simulations": 1000,
  "Percentil-50": 5,
  "Percentil-75": 7,
  "Percentil-85": 8,
  "Percentil-95": 10
}
```

### Documentação automática

Acesse [http://localhost:8000/docs](http://localhost:8000/docs) para testar e visualizar os endpoints da API.

---

## Testes

Para rodar os testes unitários e garantir o funcionamento da lógica:

```bash
pytest services/unit_tests.py
```

Se estiver usando Docker, entre no container e execute:

```bash
pytest services/unit_tests.py
```

---

## Requisitos

- Python 3.10+
- FastAPI
- Uvicorn
- Pydantic
- Numpy
- Pytest
- Docker (opcional)

---

## Estrutura de diretórios

```
v3_forecast/
├── main.py
├── forecast_routes.py
├── models/
│   └── models.py
├── services/
│   ├── forecast.py
│   └── unit_tests.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yaml
└── README.md
```

---
