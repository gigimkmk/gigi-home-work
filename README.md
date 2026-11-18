# Task Management API — Docker Networking

Open Docker Desktop (Linux containers), then open this folder in VS Code and run the following in PowerShell. These are local demo credentials only.

## Run

```powershell
docker network create task-network
docker volume create task-db-data
docker run -d --name task-db --network task-network -e POSTGRES_USER=taskuser -e POSTGRES_PASSWORD=taskpass -e POSTGRES_DB=taskdb -v task-db-data:/var/lib/postgresql/data postgres:16
docker build -t task-api .
docker run -d --name task-api --network task-network -p 8000:8000 task-api
```

The database hostname is `task-db`, not `localhost`. The database is not published to the host. FastAPI automatically creates the tasks table and retries the database connection during startup.

Check startup:

```powershell
docker logs task-api
```

Open http://localhost:8000/docs after startup completes.

## Screenshots to submit

1. `docker network ls` — task-network exists.
2. `docker ps` — task-db and task-api are running.
3. `docker network inspect task-network` — both names appear under Containers.
4. Execute the following in PowerShell and capture the actual output (API successful operations):

```powershell
$body = @{title='Learn Docker';description='Practice Docker networking';is_completed=$false} | ConvertTo-Json
$task = Invoke-RestMethod -Method Post -Uri http://localhost:8000/tasks -ContentType 'application/json' -Body $body
$task | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/tasks | ConvertTo-Json -Depth 5
Invoke-RestMethod -Uri "http://localhost:8000/tasks/$($task.id)" | ConvertTo-Json
Invoke-RestMethod -Method Delete -Uri "http://localhost:8000/tasks/$($task.id)" | ConvertTo-Json
```

Use Win+Shift+S to capture the terminal. Screenshots must be from a real Docker run; Docker was not available in the preparation environment.

## Stop (optional, after screenshots)

```powershell
docker stop task-api task-db
```

To restart existing containers, use `docker start task-db task-api` rather than creating them again. The named volume retains the database data.
