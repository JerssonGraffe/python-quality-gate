# Python Quality Gate

[![CI](https://github.com/JerssonGraffe/python-quality-gate/actions/workflows/ci.yml/badge.svg)](https://github.com/JerssonGraffe/python-quality-gate/actions/workflows/ci.yml)

Projeto de portfólio pessoal que demonstra uma **pipeline de qualidade para Python** no GitHub Actions. O código em `app/` e os testes em `tests/` servem como projeto de exemplo para exercitar as verificações; o foco deste repositório é a automação da qualidade.

## Pipeline

O workflow [`.github/workflows/ci.yml`](.github/workflows/ci.yml) roda em cada push e pull request. Os jobs são independentes: uma falha em qualquer um deles reprova a execução.

| Job | Verificação |
| --- | --- |
| `ruff` | Lint (`ruff check`) e formatação (`ruff format --check`) |
| `pyscan` | Vulnerabilidades nas dependências, incluindo o `uv.lock` |
| `pytest` | Testes automatizados com Python 3.13 e dependências travadas pelo `uv.lock` |

## Executar localmente

Requer [`uv`](https://docs.astral.sh/uv/). A versão do Python está em `.python-version` e as dependências em `pyproject.toml` e `uv.lock`.

```bash
uv venv --python 3.13
uv sync --locked
uv run --locked ruff check .
uv run --locked ruff format --check .
uvx --from pyscan-rs==2.1.3 pyscan
uv run --locked pytest -q
```

## Possível evolução

Uma pipeline de entrega poderia acrescentar etapas de **build da imagem**, **obtenção da versão (fetch version)**, publicação no **Amazon ECR** e **deploy da imagem no AWS Lambda**. Este projeto se limita à pipeline de qualidade; essas etapas de entrega não estão implementadas.
