# apiruns-cli

Apiruns CLI is a tool to make self-configurable rest API. Create an API rest has never been so easy.

## Requirements

- Python 3.6+

## Installation.

```bash
poetry install
```

## Example

```bash
apiruns --help

 Usage: apiruns [OPTIONS] COMMAND [ARGS]...
 
╭─ Options───────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                │
╰────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────╮
│ build                                   Build a API rest. 🚀               │
│ version                                 Get current version. 💬            │
╰────────────────────────────────────────────────────────────────────────────╯
```

## Crear a API Rest

```bash
apiruns build --file examples/api.yml 

Building API
Creating DB container.
Creating API container.
Starting services
API listen on 8000
```
