# Auth

## Table of Contents

- [Development](#development)
  - [Local](#local)
  - [Docker compose](#docker-compose)
- [Testing](#testing)
- [Additional](#additional)
  - [Bump version](#bump-version)
  - [Changelogs](#changelogs)
- [Docs](#docs)
  - [License](#license)
  - [Code of Conduct](#code-of-conduct)
  - [Contributing](#contributing)
  - [Security](#security)
  - [Support](#support)

## Development

Use .env file in root directory for set env variables to project. Env vars are same with [template](../../.env.template) file

### Local

For local development you can use uvicorn

```sh
poetry run uvicorn backend.create_app:create_app --factory --app-dir src --port 8081 --reload
```

Or, if you have VSCode, use "Run FastAPI" in "Run and Debug" section.

For more uvicorn options use:

```sh
poetry run uvicorn --help
```

### Docker compose

Docker compose use uvicorn with reload mode by default. Just use docker-compose

```sh
docker compose up --build --abort-on-container-exit
```

## Testing

Use pytest for testing:

```sh
pytest
```

Or, if you have VSCode, use "Run tests" in "Run and Debug" section.

For more pytest options use:

```sh
pytest --help
```

## Additional

### Bump version

WIP

### Changelogs

WIP

## Docs

### License

MIT License
Copyright (c) FellowMate
(See the [LICENSE](/LICENSE) for more information.)

### Code of Conduct

WIP

### Contributing

WIP

### Security

WIP

### Support

WIP
