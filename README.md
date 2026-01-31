# LLM Agent Gateway

This is a microservice that acts as a gateway to various Large Language Models (LLMs).

## Versioning

To update the application version, navigate to the `llm-agent-gateway` directory and use the `version.sh` script. This will update the version in `pyproject.toml` and `app/main.py`.

```bash
cd llm-agent-gateway
./version.sh set <new_version>
# Example
./version.sh set 0.2.0
cd ..
```

## API Key Acquisition

To use the LLM Agent Gateway with different providers, you'll need to acquire API keys or ensure local services are running.

### OpenAI

1.  Visit the OpenAI API Key page: [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)
2.  Log in or create an account.
3.  Click on "Create new secret key".
4.  Copy the generated key. This will be your `YOUR_OPENAI_KEY`.

### Google Gemini

1.  Visit the Google AI Studio: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2.  Log in with your Google account.
3.  Click on "Create API key in new project" or select an existing project to create a new key.
4.  Copy the generated API key. This will be your `YOUR_GEMINI_KEY`.

### Ollama

Ollama runs locally and does not require an API key. To use Ollama with the gateway, you need to have an Ollama instance running on your system, accessible from the Docker container. Ensure your Ollama server is started (e.g., `ollama serve`) and that the Docker container can connect to it (e.g., by ensuring network configurations allow communication).

## Running the service

1.  **Build the Docker image:**

    ```bash
    cd llm-agent-gateway
    ./build.sh
    cd ..
    ```

2.  **Run the Docker containers:**

    ```bash
    cd llm-agent-gateway
    ./run.sh
    cd ..
    ```

3.  **The gateway will be available at `http://localhost:8000`.**

## API

### `POST /v1/agent:run`

This is the main endpoint for running tasks with the LLM gateway.

**Example A — OpenAI text (instruction+data)**

```bash
curl -s -X POST http://localhost:8000/v1/agent:run \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "model": "gpt-4o-mini",
    "auth": { "type": "api_key", "key": "YOUR_OPENAI_KEY" },
    "input": {
      "instruction": "Reorganize a agenda e sugira o melhor horário disponível.",
      "data": {
        "dias": [
          {"data":"2026-02-01","slots":["09:00","10:00","15:00"]},
          {"data":"2026-02-02","slots":["11:00","16:00"]}
        ],
        "regras": {"duracao_min":30,"preferencia":"manhã"}
      }
    },
    "response_format": "json",
    "strict_json": true
  }'
```

**Example B — Gemini conversacional (messages)**

```bash
curl -s -X POST http://localhost:8000/v1/agent:run \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "gemini",
    "model": "gemini-1.5-pro",
    "auth": { "type": "api_key", "key": "YOUR_GEMINI_KEY" },
    "input": {
      "messages": [
        {"role":"system","content":"Você é um assistente de atendimento. Responda curto e útil."},
        {"role":"user","content":"Com base nesses dados, qual a melhor opção? Dados: {\"option1\": \"A\", \"option2\": \"B\"} "}
      ]
    },
    "response_format": "text"
  }'
```

**Example C — Ollama local**

```bash
curl -s -X POST http://localhost:8000/v1/agent:run \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "ollama",
    "model": "llama3.1",
    "auth": { "type": "none" },
    "input": {
      "instruction": "Resuma em 5 bullets e extraia riscos.",
      "data": "Texto grande aqui..."
    },
    "response_format": "text"
  }'
```

### Success Response

Upon a successful `POST /v1/agent:run` request, the API will return a JSON object with the following structure:

```json
{
    "ok": true,
    "trace_id": "string",
    "provider": "openai" | "gemini" | "ollama",
    "model": "string",
    "result": {
        "type": "text" | "json",
        "text": "string (if type is text)",
        "json": "object (if type is json)"
    },
    "usage": {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "is_estimated": false
    },
    "billing": {
        "currency": "USD",
        "estimated_cost": 0.0,
        "pricing_source": "config" | "unknown",
        "note": "string (optional)"
    },
    "timing": {
        "started_at": "datetime_string",
        "ended_at": "datetime_string",
        "duration_ms": 0,
        "provider_duration_ms": 0
    },
    "warnings": [
        {
            "code": "string",
            "message": "string"
        }
    ],
    "echo": {
        "metadata": "object (optional)"
    }
}
```

### General Error Response

For other types of errors (e.g., validation errors, provider-specific issues), the API will return a JSON object with a relevant HTTP status code (e.g., 400, 500) and the following structure:

```json
{
    "ok": false,
    "trace_id": "string",
    "error": {
        "code": "string",
        "message": "string",
        "details": "object (optional)"
    }
}
```

### Concurrency Limit Error Response

When the number of concurrent requests exceeds the configured limit (`MAX_CONCURRENCY`), the API will respond with a `429 Too Many Requests` status code. The response body will be a JSON object similar to this:

```json
{
    "ok": false,
    "trace_id": "N/A", // or the actual trace_id if available
    "error": {
        "code": "RATE_LIMIT",
        "message": "Too many concurrent requests."
    }
}
```

Clients receiving this response should implement a retry mechanism, respecting a back-off strategy.

### Health and Readiness

*   `GET /health`: Liveness probe.

    **Response:**

    ```json
    {
        "status": "ok"
    }

*   `GET /ready`: Readiness probe.
    Checks if critical configurations are loaded and the service is ready to handle requests.

    **Response (Ready):**

    ```json
    {
        "status": "ready"
    }
    ```

    **Response (Not Ready - HTTP 503):**

    ```json
    {
        "detail": "Pricing configuration not loaded."
    }
    ```
*   `GET /v1/providers`: Lists available providers.
    Dynamically lists available providers and their capabilities.

    **Response:**

    ```json
    {
        "providers": [
            {
                "name": "openai",
                "capabilities": ["json_mode", "chat_completions"]
            },
            {
                "name": "gemini",
                "capabilities": ["json_mode", "chat_completions"]
            },
            {
                "name": "ollama",
                "capabilities": ["chat_completions"]
            }
        ]
    }
    ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
