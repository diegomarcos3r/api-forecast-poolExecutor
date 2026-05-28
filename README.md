# Monte Carlo Forecast API

Uma aplicação FastAPI que realiza **simulações de Monte Carlo** para prever o número de semanas necessárias para concluir um backlog, utilizando dados históricos de throughput. A API utiliza `ProcessPoolExecutor` para paralelizar cálculos intensivos e oferece validação de dados com Pydantic.

---

## 📋 Índice

1. [Como Funciona](#como-funciona)
2. [Instalação](#instalação)
3. [Como Subir a Aplicação](#como-subir-a-aplicação)
4. [Entendendo Uvicorn](#entendendo-uvicorn)
5. [Configuração do ProcessPoolExecutor](#configuração-do-processpoolexecutor)
6. [Lógica do Forecast API](#lógica-do-forecast-api)
7. [Como Utilizar](#como-utilizar)
8. [Testes](#testes)
9. [Estrutura de Diretórios](#estrutura-de-diretórios)

---

## 🧮 Como Funciona

### O Problema

Você tem um backlog de trabalho e quer saber: **"Quantas semanas vou levar para concluir?"**

O desafio é que a produtividade (throughput) varia de semana para semana. Então, em vez de fazer uma única previsão, usamos **Monte Carlo** para rodar múltiplas simulações com variações aleatórias.

### A Solução: Monte Carlo

1. **Para cada simulação:**
   - Sorteamos um backlog aleatório entre o mínimo e máximo informado
   - Semana após semana, sorteamos um throughput da sua lista histórica
   - Acumulamos o throughput até cobrir o backlog
   - Contamos quantas semanas levou

2. **Depois de N simulações:**
   - Calculamos percentis (50%, 75%, 85%, 95%)
   - Você sabe: "em 50% dos casos levo 5 semanas, em 95% levo 10 semanas"

### Por que Paralelização?

Com 1.000 ou 10.000 simulações, o cálculo fica pesado. O `ProcessPoolExecutor` divide o trabalho entre os núcleos do processador, rodando tudo em paralelo.

---

## 📦 Instalação

### Pré-requisitos
- Python 3.13+ (recomendado)
- pip
- Docker (opcional)

### Instalação Local

1. **Clone ou copie o projeto**
   ```bash
   cd seu-projeto
   ```

2. **Instale as dependências**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Instalação com Docker

Não precisa de nada além do Docker:

```bash
docker-compose up --build
```

---

## 🚀 Como Subir a Aplicação

### Opção 1: Localmente com Python

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em: **[http://localhost:8000](http://localhost:8000)**

**Explicação dos parâmetros:**
- `main:app` → importa `app` do arquivo `main.py`
- `--reload` → reinicia ao detectar mudanças nos arquivos (desenvolvimento)
- `--host 0.0.0.0` → aceita requisições de qualquer IP
- `--port 8000` → porta 8000

### Opção 2: Docker (Recomendado para Produção)

```bash
docker-compose up --build
```

**O que acontece:**
1. Docker constrói a imagem usando o `Dockerfile`
2. Instala as dependências do `requirements.txt`
3. Executa o uvicorn dentro do container
4. Expõe a porta 8000

Verifique os logs:
```bash
docker-compose logs -f dev-backend
```

Para parar:
```bash
docker-compose down
```

---

## 🔧 Entendendo Uvicorn

### O que é Uvicorn?

**Uvicorn** é um servidor ASGI (Asynchronous Server Gateway Interface) que:
- Roda aplicações FastAPI
- Gerencia requisições HTTP
- Executa código assíncrono (async/await)
- Implementa WebSockets

### Como Funciona com FastAPI

```
Cliente HTTP
    ↓
Uvicorn (servidor)
    ↓
FastAPI (aplicação)
    ↓
Rotas e handlers
```

### Ciclo de Vida no Uvicorn

Quando você inicia o uvicorn, ele:

1. **Startup**: Executa `lifespan` (contexto manager em `config.py`)
2. **Running**: Aguarda requisições
3. **Shutdown**: Limpa recursos

```python
# Em config.py, o lifespan gerencia isso:
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - executa uma vez ao iniciar
    with ProcessPoolExecutor() as pool:
        app.state.pool_executor = pool
        print("✓ ProcessPoolExecutor inicializado")
        yield  # ← Servidor fica rodando aqui
    # Shutdown - executa ao parar a aplicação
    print("✓ ProcessPoolExecutor finalizado")
```

---

## ⚙️ Configuração do ProcessPoolExecutor

### O que é ProcessPoolExecutor?

Um `ProcessPoolExecutor` cria um **pool de processos paralelos** que dividem tarefas CPU-intensivas.

### Por que Usamos?

- Simulações de Monte Carlo são **CPU-bound** (usam muito processador)
- FastAPI roda em uma thread, mas `ProcessPoolExecutor` usa múltiplos processos
- Cada processo usa um núcleo diferente do CPU → verdadeiro paralelismo

### Como Está Configurado

**Arquivo: `config.py`**

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria o pool uma única vez
    with ProcessPoolExecutor() as pool:
        app.state.pool_executor = pool  # ← Armazena no estado da app
        print("✓ ProcessPoolExecutor inicializado")
        yield
    print("✓ ProcessPoolExecutor finalizado")
```

**Vantagens:**
- ✅ Compartilhado entre todas as requisições
- ✅ Criado uma vez (eficiente)
- ✅ Destruído automaticamente ao parar

### Como Usar em uma Requisição

**Em `forecast_routes.py`:**

```python
@forecast_router.post("/run-forecast")
async def create_simulation(request: Request, new_simulation: CreateSimulation) -> dict:
    # ... criar objeto Forecast ...
    
    # Obter o pool do estado da aplicação
    loop = asyncio.get_running_loop()
    pool_executor = request.app.state.pool_executor
    
    # Executar a simulação em paralelo
    result = await loop.run_in_executor(pool_executor, forecast.run_forecast)
    
    return result
```

**O que acontece:**
1. `asyncio.get_running_loop()` → obtém o loop de eventos
2. `loop.run_in_executor()` → executa função síncrona (`run_forecast`) em um worker do pool
3. `await` → aguarda o resultado sem bloquear a requisição

---

## 📊 Lógica do Forecast API

### Fluxo Completo

```
1. Cliente envia:
   {
     "nr_simulations": 1000,
     "backlog_min": 10,
     "backlog_max": 20,
     "throughput": [2, 3, 4, 5]
   }

2. FastAPI valida com Pydantic (models.py)

3. Cria objeto Forecast em services/forecast.py

4. Envia para ProcessPoolExecutor:
   → ProcessPoolExecutor.run_forecast()

5. Simulações rodando em paralelo:
   Simulação 1: Backlog=15 → 7 semanas
   Simulação 2: Backlog=12 → 5 semanas
   Simulação 3: Backlog=18 → 9 semanas
   ...
   Simulação 1000: Backlog=14 → 6 semanas

6. Calcula percentis dos resultados:
   - P50: 6 semanas (mediana)
   - P75: 8 semanas
   - P85: 9 semanas
   - P95: 11 semanas

7. Retorna resposta formatada
```

### Dentro de uma Simulação

```python
def _run_simulations(self) -> List[int]:
    forecast_weeks = []
    
    for _ in range(self.nr_simulations):  # 1000 vezes
        backlog_done = 0
        random_weeks = 0
        
        # Sorteia backlog aleatório
        backlog = np.random.randint(self.backlog_min, self.backlog_max + 1)
        
        # Semana por semana, até cobrir o backlog
        while backlog_done < backlog:
            # Sorteia um throughput da lista histórica
            random_throughput = np.random.choice(self.throughput)
            backlog_done += random_throughput
            random_weeks += 1
        
        # Salva quantas semanas levou
        forecast_weeks.append(random_weeks)
    
    return forecast_weeks
```

### Exemplo Prático

**Entrada:**
- `nr_simulations: 3`
- `backlog_min: 10, backlog_max: 10` (sempre 10)
- `throughput: [2, 3, 4, 5]`

**Simulação 1:**
```
Backlog: 10
Semana 1: throughput=3 → backlog_done=3
Semana 2: throughput=4 → backlog_done=7
Semana 3: throughput=5 → backlog_done=12 (✓ cobriu)
→ Resultado: 3 semanas
```

**Simulação 2:**
```
Backlog: 10
Semana 1: throughput=2 → backlog_done=2
Semana 2: throughput=2 → backlog_done=4
Semana 3: throughput=5 → backlog_done=9
Semana 4: throughput=3 → backlog_done=12 (✓ cobriu)
→ Resultado: 4 semanas
```

**Simulação 3:**
```
Backlog: 10
Semana 1: throughput=5 → backlog_done=5
Semana 2: throughput=5 → backlog_done=10 (✓ cobriu)
→ Resultado: 2 semanas
```

**Cálculo de Percentis:**
```
Resultados: [3, 4, 2]
P50 (mediana): 3 semanas
```

---

## 🔌 Como Utilizar

### Endpoint Principal

**POST** `/forecast/run-forecast`

#### Validações (Pydantic - `models.py`)

- `nr_simulations` → deve ser > 0
- `backlog_min` → deve ser > 0
- `backlog_max` → deve ser ≥ `backlog_min`
- `throughput` → deve ter no mínimo 4 valores

#### Exemplo de Requisição

```bash
curl -X POST "http://localhost:8000/forecast/run-forecast" \
  -H "Content-Type: application/json" \
  -d '{
    "nr_simulations": 1000,
    "backlog_min": 10,
    "backlog_max": 20,
    "throughput": [2, 3, 4, 5]
  }'
```

#### Exemplo de Resposta

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

### Endpoints de Saúde

**GET** `/` → Mensagem de boas-vindas
```json
{
  "message": "API de Forecast - Use POST /forecast/run-forecast"
}
```

**GET** `/forecast/` → Health check
```json
{
  "status": "API de Forecast rodando"
}
```

### Documentação Interativa

FastAPI gera documentação automática! Acesse:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

Lá você pode testar os endpoints diretamente no navegador.

---

## ✅ Testes

### Rodando Testes Localmente

```bash
pytest services/unit_tests.py -v
```

Saída esperada:
```
test_forecast_init PASSED
test_run_simulation_returns_list_of_ints PASSED
test_calculate_percentiles_correct_values PASSED
test_calculate_percentiles_empty_input_raises PASSED
test_format_forecast_response_structure PASSED
```

### Rodando Testes no Docker

```bash
docker exec -it <container_id> pytest services/unit_tests.py -v
```

Ou use docker-compose:
```bash
docker-compose exec dev-backend pytest services/unit_tests.py -v
```

### O que é Testado?

- ✅ Inicialização correta da classe
- ✅ Simulações retornam lista de inteiros
- ✅ Cálculo de percentis está correto
- ✅ Validação de entrada (valores vazios)
- ✅ Formatação da resposta

---

## 📁 Estrutura de Diretórios

```
api_forecast_v-poolExecutor/
│
├── main.py                 # Inicializa a aplicação FastAPI
├── config.py              # Gerencia ProcessPoolExecutor (NEW)
├── forecast_routes.py     # Define as rotas da API
│
├── models/
│   └── models.py          # Validação com Pydantic
│
├── services/
│   ├── forecast.py        # Lógica de Monte Carlo
│   └── unit_tests.py      # Testes unitários
│
├── requirements.txt       # Dependências Python
├── Dockerfile             # Imagem Docker
├── docker-compose.yaml    # Orquestração Docker
├── README.md              # Este arquivo
```

### Responsabilidade de Cada Arquivo

| Arquivo | Responsabilidade |
|---------|-----------------|
| `main.py` | Criar app FastAPI e incluir rotas |
| `config.py` | Gerenciar ciclo de vida do ProcessPoolExecutor |
| `forecast_routes.py` | Definir endpoint `/forecast/run-forecast` |
| `models.py` | Validar dados de entrada com Pydantic |
| `forecast.py` | Implementar lógica de Monte Carlo |
| `unit_tests.py` | Testar cada função isoladamente |

---

## 📦 Requisitos

```
Python 3.13+
fastapi==0.x.x
uvicorn==0.x.x
pydantic==2.x.x
numpy==1.x.x
pytest==7.x.x
```

Veja `requirements.txt` para versões exatas.

---

## 🐛 Resolução de Problemas

### Erro: "Porta 8000 já está em uso"

```bash
# Linux/Mac
lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Erro: "No module named..."

Certifique-se de instalar as dependências:
```bash
pip install -r requirements.txt
```

### Erro: "ProcessPoolExecutor not initialized"

Verifique se o `lifespan` em `config.py` está sendo usado em `main.py`:
```python
app = FastAPI(lifespan=lifespan)
```

---

## 📚 Referências

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [ProcessPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html)
- [Monte Carlo Simulation](https://en.wikipedia.org/wiki/Monte_Carlo_method)
- [Pydantic Validation](https://docs.pydantic.dev/)

---
