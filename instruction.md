# AI Persona Project - Setup Guide

This guide provides instructions to get the AI Persona Project up and running on your local machine.

---

## **Prerequisites**
- Docker Desktop installed and running
- Git installed

---

## **Quick Start (Recommended)**

For the most straightforward setup, we recommend using the automated script. It will detect your operating system, check for necessary software like Docker, and run all the required commands in the correct sequence.

**Step 1: Clone and Setup Environment**
```bash
git clone <repository-url>
cd ai-persona
cp sample.env .env
```

**Step 2: Add API Keys**
Edit the `.env` file and add your API keys:
- `OPENAI_API_KEY=your_openai_api_key_here`
- `COHERE_API_KEY=your_cohere_api_key_here`

**Step 3: Run Startup Script**

**For macOS/Linux:**
```bash
./startup/startup.sh
```

**For Windows:**
```bash
startup\startup.bat
```

Once the script is complete, you can access the application.

* **URL:** `http://localhost:19100`
* **Email:** `admin@example.com`
* **Password:** `TestPass123!`

---

## **Manual Setup (Alternative)**

If you prefer to run the commands yourself or encounter issues with the automated script, follow these steps.

**Step 1: Clone the Repository**
```bash
git clone <repository-url>
cd ai-persona
```

**Step 2: Create Environment File**
Create a `.env` file by copying the sample:
```bash
cp sample.env .env
```

Then edit the `.env` file and add your API keys:
- `OPENAI_API_KEY=your_openai_api_key_here`
- `COHERE_API_KEY=your_cohere_api_key_here`

**Step 3: Start the Services**
```bash
docker network create spiritual-chatbot-traefik-public
docker-compose build prestart frontend
docker-compose up -d
```

**That's it!** The system now automatically creates test users and AI souls during startup.

---

## **Access Your Application**

Once setup is complete, you can access:

* **Frontend:** `http://localhost:19100`
* **Backend API:** `http://localhost:17010`
* **API Documentation:** `http://localhost:17010/docs`
* **Database Admin:** `http://localhost:17080`

**Default Login:**
* **Email:** `admin@example.com`
* **Password:** `TestPass123!`

---

## **Troubleshooting & Other Commands**

**Common Issues:**
* **Docker Not Running:** Ensure Docker Desktop is active on your system before starting.
* **Permission Denied (macOS/Linux):** If you see a permission error, make the startup script executable with the command: `chmod +x startup/startup.sh`.
* **Windows Issues:** If you encounter problems on Windows, try running the `startup.bat` script as an Administrator.
* **Missing API Keys:** Make sure you've added your OPENAI_API_KEY and COHERE_API_KEY to the .env file.

**Useful Commands:**
* **View Application Logs:** `docker-compose logs -f`
* **Stop All Services:** `docker-compose down`
* **Restart All Services:** `docker-compose restart`
* **Reset Everything:** `docker-compose down -v` (removes all data)