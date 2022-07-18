# apiruns-cli

Apiruns CLI is a tool to make self-configurable rest API. Create an API rest has never been so easy.

## Requirements

- Python 3.6+

## Installation.

```bash
pip install apiruns
```

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
│ build                       Build images & validate schema.🔧              │
│ up                          Make your API rest. 🚀                         │
│ version                     Get current version. 💬                        │
╰────────────────────────────────────────────────────────────────────────────╯
```

## file configuration

Make YAML file to configure your application’s services. `api.yml`

```yml
# This is an example manifest to create microservices in apiruns.

myapi: # Microservices name.

  # first endpoint
  - path: /users/ # Path name.
    schema: # Schema of data structure.
      username:
        type: string
        required: true
      age:
        type: integer
        required: true
      is_admin:
        type: boolean
        required: true
      level:
        type: string
```

## Crear a API Rest

```bash
apiruns up --file examples/api.yml 

Building API
Creating DB container.
Creating API container.
Starting services
API listen on 8000
```
