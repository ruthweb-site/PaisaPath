# Deploying PaisaPath AI to Nebius AI Cloud ☁️

This guide explains how to deploy **PaisaPath AI** as a production Docker container on **Nebius AI Cloud** for the hackathon submission.

---

## Architecture Overview in Container

The multi-stage `Dockerfile` packages the entire stack:
- **FastAPI Backend + React Frontend (Port 8000)**: Serves both the REST API and the production-optimized React SPA at the root URL `/`.
- **Streamlit Dashboard (Port 8501)**: Provides the alternative all-in-one Streamlit financial companion interface.
- **SQLite Database**: Stored in a persistent Docker volume (`/app/data`).
- **NVIDIA Nemotron Inference**: Communicates directly with Nebius Token Factory (`nvidia/Llama-3_1-Nemotron-Ultra-253B-v1`).

---

## Option 1: Fast Deploy on a Nebius Cloud Compute VM (Recommended)

### Step 1: Create a VM on Nebius AI Cloud
1. Log in to the [Nebius AI Cloud Console](https://console.nebius.com).
2. Navigate to **Compute** $\rightarrow$ **Instances** $\rightarrow$ **Create Instance**.
3. Choose:
   - **OS**: Ubuntu 22.04 LTS or Debian 12
   - **Preset**: Standard CPU preset (e.g. 2–4 vCPUs, 4–8 GB RAM). *Note: The Nemotron model runs via remote API calls to Nebius Token Factory, so expensive GPU instances are not required.*
   - **Network**: Ensure a public IP address is assigned.
   - **Security Groups / Firewall**: Allow inbound TCP traffic on ports **8000** and **8501**.

### Step 2: Connect and Install Docker
SSH into your Nebius VM:
```bash
ssh <username>@<your-nebius-vm-ip>
```

Install Docker and Docker Compose:
```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-v2 git
sudo usermod -aG docker $USER
newgrp docker
```

### Step 3: Clone the Repository & Configure Credentials
```bash
git clone https://github.com/ruthweb-site/PaisaPath.git
cd PaisaPath

# Create your .env file
nano .env
```

Paste your Nebius and Tavily credentials into `.env`:
```env
NEBIUS_API_KEY=your_actual_nebius_api_key
NEBIUS_BASE_URL=https://api.tokenfactory.nebius.com/v1/
NEBIUS_MODEL=nvidia/Llama-3_1-Nemotron-Ultra-253B-v1

TAVILY_API_KEY=your_actual_tavily_api_key
```
Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

### Step 4: Build & Launch with Docker Compose
Run the container:
```bash
docker compose up -d --build
```

Verify that the container is healthy:
```bash
docker compose ps
docker compose logs -f
```

---

## Option 2: Build and Run via Pure Docker CLI

If you prefer building and running with standard Docker commands:

```bash
# 1. Build the multi-stage image
docker build -t paisapath-ai .

# 2. Run both interfaces
docker run -d \
  --name paisapath-ai \
  --restart unless-stopped \
  --env-file .env \
  -e APP_MODE=both \
  -p 8000:8000 \
  -p 8501:8501 \
  -v paisapath_data:/app/data \
  paisapath-ai
```

### Container Modes (`APP_MODE` environment variable):
- `APP_MODE=api` (Default): Runs FastAPI + React Dashboard on port 8000.
- `APP_MODE=streamlit`: Runs Streamlit Dashboard on port 8501.
- `APP_MODE=both`: Runs FastAPI + React on port 8000 AND Streamlit on port 8501.

---

## Verifying Deployment

Once running on your Nebius Cloud instance:

1. **Modern React Dashboard + FastAPI API**:
   - `http://<your-nebius-vm-ip>:8000/` (React Frontend)
   - `http://<your-nebius-vm-ip>:8000/api/health` (Healthcheck endpoint)
   - `http://<your-nebius-vm-ip>:8000/docs` (Interactive Swagger API documentation)

2. **Streamlit Interactive Companion**:
   - `http://<your-nebius-vm-ip>:8501/`

---

## Nebius x NVIDIA Hackathon Submission Tip
When submitting on Devpost or the hackathon platform, provide:
1. Public Demo URL: `http://<your-nebius-vm-ip>:8000/`
2. Streamlit URL: `http://<your-nebius-vm-ip>:8501/`
3. Swagger Docs: `http://<your-nebius-vm-ip>:8000/docs`
4. Note stating: *"Hosted on Nebius AI Cloud with NVIDIA Nemotron model inference executed at runtime via Nebius Token Factory."*

