# API de projetos e tarefas

API REST em Python 3.13 com FastAPI, SQLite e `uv`. Permite organizar tarefas em projetos, filtrar tarefas por projeto e status e consultar a documentação interativa. Os dados ficam em `tasks.db` por padrão; configure `TASKS_DB_PATH` para escolher outro arquivo. Bases criadas pela versão anterior são atualizadas automaticamente ao iniciar.

## Executar

```bash
uv venv --python 3.13
uv sync --locked
uv run uvicorn main:app --reload
```

Documentação: http://127.0.0.1:8000/docs

## Endpoints

| Método | Rota | Ação |
| --- | --- | --- |
| GET | `/health` | Verificar o serviço |
| GET / POST | `/projects` | Listar / criar projetos |
| GET / PUT / DELETE | `/projects/{id}` | Consultar / atualizar / excluir projeto |
| GET / POST | `/tasks` | Listar / criar tarefas |
| GET / PUT / DELETE | `/tasks/{id}` | Consultar / atualizar / excluir tarefa |

`GET /tasks` aceita os filtros `completed=true|false` e `project_id=1`, isolados ou combinados. Um projeto com tarefas vinculadas não pode ser excluído (HTTP 409); desvincule ou exclua as tarefas antes. Recursos inexistentes retornam 404, e dados inválidos retornam 422. `title` e `name` devem ter de 1 a 120 caracteres após remover espaços nas extremidades; `description` aceita até 1000.

```bash
curl -X POST http://127.0.0.1:8000/projects \
  -H 'Content-Type: application/json' \
  -d '{"name":"Casa","description":"Reformas"}'
curl -X POST http://127.0.0.1:8000/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title":"Pintar parede","project_id":1}'
curl 'http://127.0.0.1:8000/tasks?project_id=1&completed=false'
curl -X PUT http://127.0.0.1:8000/tasks/1 \
  -H 'Content-Type: application/json' \
  -d '{"title":"Pintar parede","completed":true,"project_id":1}'
```

Tarefas podem existir sem projeto (`project_id: null`). `PUT` substitui os campos editáveis: omitir `description` usa a descrição vazia; omitir `project_id` desvincula a tarefa.

## Organização

```text
app/
  main.py            # inicialização da API e rota de saúde
  db.py              # conexões SQLite e atualização do esquema
  schemas.py         # validação e formatos de entrada/saída
  routes/
    projects.py      # endpoints de projetos
    tasks.py         # endpoints de tarefas
main.py              # ponto de entrada para uvicorn
tests/               # fluxo de tarefas, projetos e migração
```

## Verificar

O workflow de CI executa Ruff, PyScan e pytest em jobs separados. O PyScan verifica vulnerabilidades nas dependências e reprova o job caso encontre alguma.

```bash
uv run --locked pytest -q
uv run --locked ruff check .
uv run --locked ruff format --check .
uvx --from pyscan-rs==2.1.3 pyscan
```
