# relay server

this is intended to be a demo of how you can make your own relay server similar to the [realtime console example](https://github.com/openai/openai-realtime-console)

# Example

To run the example, we will clone the repo from github and follow their instructions.  Only we will use our own relay server:

```bash

git clone https://github.com/openai/openai-realtime-console && cd openai-realtime-console && npm install

# set the env vars for the relay server
OPENAI_API_KEY=OPENAI_API_KEY
RELAY_SERVER_PORT="${RELAY_SERVER_PORT:=8081}"
# create the env file that the app uses
echo -e "OPENAI_API_KEY=$OPENAI_API_KEY\nREACT_APP_LOCAL_RELAY_SERVER_URL=http://localhost:$RELAY_SERVER_PORT" > .env
```


then start the services, ideally with something like `mise` that can handle running tasks:

```toml
[tasks.relay]
    run = "uv run --directory examples/relay-server relay.py"

[tasks.frontend]
    env = { BROWSER = "None" }
    run = "uv run --directory examples/relay-server/openai-realtime-console -- npm run start"

[tasks.dev]
    depends = ["frontend", "relay"]
```

`mise run dev` which should run the relay server and the frontend server concurrently.

<details>
or with multiple terminals can run something like the following

```bash
# in one terminal (can also use watchmedo to restart the server on file changes: `watchmedo auto-restart --recursive --signal SIGTERM python relay.py`)
uv run relay.py
# in another terminal
npm run start
```
</details>
