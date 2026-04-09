# NutriGuard - Comprehensive Nutrition Tracking & Meal Planning Platform

A full-stack application for nutrition tracking, meal planning, and personalized dietary recommendations powered by AI and machine learning.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Database](#database)
- [Deployment](#deployment)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Project Overview

NutriGuard is an intelligent nutrition management system designed to help users:
- Track daily food consumption and nutritional intake
- Create personalized meal plans based on dietary preferences
- Monitor nutritional goals (calories, protein, carbs, fats)
- Integrate with Discord for bot-based meal tracking
- Receive AI-powered dietary recommendations
- Access a comprehensive database of food items with nutritional information

The platform combines a modern React frontend with a robust FastAPI backend, integrated with Supabase for authentication and data management, and powered by Ollama and n8n for AI orchestration.

## ✨ Features

### User Management
- User registration and authentication via Supabase Auth
- Discord account integration
- User preference and dietary goal configuration
- Subscription management

### Food Tracking
- Comprehensive food database (including Indonesian cuisine)
- Consumption logging with portions and timestamps
- Nutritional information tracking (calories, protein, carbs, fats)
- Semantic search for food items

### Meal Planning
- Personalized meal plan creation
- Support for multiple diet types (Standard, Keto, Vegan, etc.)
- Automatic meal suggestions based on nutritional targets
- Plan history and modifications

### Discord Bot Integration
- Real-time meal logging via Discord commands
- Nutritional summaries and reports
- User meal history retrieval
- Meal plan sharing through Discord

### AI Features
- Semantic search using embeddings
- AI-powered meal recommendations
- Workflow orchestration with n8n
- Local LLM support via Ollama

### Analytics & Monitoring
- Load testing with Locust
- Performance monitoring
- Consumption analytics and reports

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth + Discord OAuth
- **Caching**: Redis
- **AI/ML**: Ollama, Embeddings for semantic search
- **Rate Limiting**: SlowAPI
- **ORM**: Direct SQL with Supabase client

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Components**: Custom components with CSS
- **Authentication**: Keycloak/OAuth integration
- **API Client**: Axios/Fetch with custom API utilities
- **State Management**: React Context API

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Orchestration**: Kubernetes
- **AI Services**: Ollama (Local LLM), Open WebUI (AI Dashboard)
- **Workflow Engine**: n8n
- **Cache**: Redis
- **Monitoring**: Locust (Load Testing)

## 📁 Project Structure

```
FinalProjectKalbe/
├── backend/                          # FastAPI Backend
│   ├── core/                         # Core configurations
│   │   ├── config.py                 # Configuration management
│   │   ├── security.py               # Security utilities
│   │   ├── supabase.py               # Supabase client
│   │   ├── redis.py                  # Redis connection
│   │   └── rate_limit.py             # Rate limiting configuration
│   ├── models/                       # Data models
│   ├── services/                     # Business logic
│   │   ├── auth.py                   # Authentication service
│   │   ├── users.py                  # User management
│   │   ├── food.py                   # Food database service
│   │   ├── consumption_logs.py        # Consumption tracking
│   │   ├── meal_plans.py              # Meal planning service
│   │   ├── bot.py                    # Discord bot logic
│   │   ├── bot_users.py              # Bot user management
│   │   ├── bot_food.py               # Bot food operations
│   │   ├── bot_meal_plans.py         # Bot meal planning
│   │   ├── bot_logs.py               # Bot logging
│   │   ├── embeddings.py             # Semantic search embeddings
│   │   └── meal_processing.py        # Meal processing jobs
│   ├── router/                       # API endpoints
│   │   ├── auth.py                   # Auth endpoints
│   │   ├── users.py                  # User endpoints
│   │   ├── food.py                   # Food endpoints
│   │   ├── consumption_logs.py        # Consumption endpoints
│   │   ├── meal_plans.py              # Meal plan endpoints
│   │   ├── bot.py                    # Bot endpoints
│   │   ├── meal_processing.py        # Processing endpoints
│   │   └── bot_*.py                  # Other bot endpoints
│   ├── migrations/                   # SQL migrations
│   │   ├── 001_init_schema.sql       # Initial schema
│   │   ├── 002_semantic_search_rpc.sql
│   │   ├── 003_grant_schema_permissions.sql
│   │   ├── 004_add_password_column.sql
│   │   ├── 005_meal_processing_jobs.sql
│   │   └── 006_grant_meal_processing_permissions.sql
│   ├── scripts/                      # Utility scripts
│   │   └── import_food_data.py       # Food data import
│   ├── main.py                       # FastAPI application
│   ├── requirements.txt              # Python dependencies
│   ├── Dockerfile                    # Container image
│   └── README.md                     # Backend documentation
│
├── frontend/                         # React Frontend
│   ├── src/
│   │   ├── pages/                    # Page components
│   │   │   ├── DashboardPage.tsx     # Main dashboard
│   │   │   ├── FoodLogPage.tsx       # Food logging
│   │   │   ├── MealChatPage.tsx      # Chat interface
│   │   │   ├── ProfilePage.tsx       # User profile
│   │   │   ├── SearchPage.tsx        # Food search
│   │   │   ├── LoginPage.tsx         # Authentication
│   │   │   ├── SignupPage.tsx        # Registration
│   │   │   └── IntegrationsPage.tsx  # Service integrations
│   │   ├── components/               # Reusable components
│   │   ├── context/                  # React context (Auth)
│   │   ├── utils/                    # Utility functions
│   │   ├── assets/                   # Static assets
│   │   ├── App.tsx                   # Main app component
│   │   └── main.tsx                  # App entry point
│   ├── public/                       # Static files
│   ├── vite.config.ts                # Vite configuration
│   ├── tsconfig.json                 # TypeScript config
│   ├── package.json                  # Node dependencies
│   ├── Dockerfile                    # Container image
│   ├── eslint.config.js              # ESLint configuration
│   └── README.md                     # Frontend documentation
│
├── kubernetes/                       # Kubernetes manifests
│   ├── backend.yaml                  # Backend deployment
│   ├── frontend.yaml                 # Frontend deployment
│   ├── redis.yaml                    # Redis deployment
│   ├── n8n.yaml                      # n8n orchestrator
│   ├── locust.yaml                   # Load testing
│   └── backend-secret.yaml           # Secret management
│
├── load-tests/                       # Performance testing
│   └── locustfile.py                 # Locust test scenarios
│
├── docker-compose.yml                # Docker Compose configuration
├── gizi.json                         # Nutritional database (Indonesian foods)
└── bdlogs.txt                        # Build/deployment logs

```

## 📋 Prerequisites

- **Docker** & **Docker Compose** (for containerized setup)
- **Python 3.9+** (for backend development)
- **Node.js 16+** & **npm** (for frontend development)
- **Supabase Account** (database and authentication)
- **Discord Bot Token** (for bot integration - optional)
- **Ollama** (for AI features)

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd FinalProjectKalbe
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env
# Edit .env with your configuration:
# - SUPABASE_URL
# - SUPABASE_KEY
# - DISCORD_BOT_TOKEN (if using Discord bot)
# - REDIS_URL
# - etc.
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file for API configuration
# Update API_URL to point to your backend
```

### 4. Database Setup

The migrations will be applied automatically when using Docker Compose, or manually:

```bash
# Apply migrations through Supabase Dashboard or using the SQL files in backend/migrations/
```

### 5. Import Food Data

```bash
cd backend/scripts
python import_food_data.py
```

## 🏃 Running the Application

### Option 1: Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up -d

# Services will be available at:
# - Backend: http://localhost:8000
# - Frontend: http://localhost:5173
# - Ollama: http://localhost:11434
# - Open WebUI: http://localhost:3000
# - n8n: http://localhost:5678
# - Redis: localhost:6379
```

### Option 2: Local Development

**Terminal 1 - Backend:**
```bash
cd backend
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Option 3: Kubernetes

```bash
kubectl apply -f kubernetes/backend.yaml
kubectl apply -f kubernetes/frontend.yaml
kubectl apply -f kubernetes/redis.yaml
kubectl apply -f kubernetes/n8n.yaml

# Check deployment status
kubectl get pods
kubectl get svc
```

## 📚 API Documentation

Once the backend is running, access the API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main API Endpoints

#### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `POST /auth/refresh` - Refresh token

#### Users
- `GET /users/profile` - Get user profile
- `PUT /users/profile` - Update user profile
- `GET /users/preferences` - Get dietary preferences
- `PUT /users/preferences` - Update preferences

#### Food
- `GET /food` - List all foods
- `GET /food/search` - Search foods by name
- `POST /food/semantic-search` - AI-powered food search
- `GET /food/{id}` - Get food details
- `POST /food` - Add new food (admin)

#### Consumption Logs
- `POST /consumption-logs` - Log food consumption
- `GET /consumption-logs` - Get user logs
- `GET /consumption-logs/daily` - Get daily summary
- `GET /consumption-logs/stats` - Get statistics

#### Meal Plans
- `POST /meal-plans` - Create meal plan
- `GET /meal-plans` - List user meal plans
- `GET /meal-plans/{id}` - Get meal plan details
- `PUT /meal-plans/{id}` - Update meal plan
- `DELETE /meal-plans/{id}` - Delete meal plan

#### Discord Bot
- `POST /bot/user` - Register bot user
- `POST /bot/log` - Log meal via bot
- `GET /bot/logs/{user_id}` - Get bot logs
- `POST /bot/meal-plan` - Create meal plan via bot

## 🗄️ Database

### Supabase Configuration

The project uses Supabase for:
1. **Authentication** - User registration and login
2. **Database** - PostgreSQL for data storage
3. **Real-time** - Real-time subscriptions (optional)

### Key Tables

- `users` - User accounts and profiles
- `user_preferences` - Dietary preferences and goals
- `foods` - Food database with nutritional info
- `consumption_logs` - Daily food logs
- `meal_plans` - Meal planning data
- `meal_plan_items` - Individual items in meal plans
- `bot_users` - Discord bot user mappings

### Migrations

Run migrations in order:
1. `001_init_schema.sql` - Create tables and RLS policies
2. `002_semantic_search_rpc.sql` - Add semantic search function
3. `003_grant_schema_permissions.sql` - Grant permissions
4. `004_add_password_column.sql` - Add password field
5. `005_meal_processing_jobs.sql` - Create job tables
6. `006_grant_meal_processing_permissions.sql` - Grant job permissions

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Client (Browser)                   │
│                    React + TypeScript                        │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────▼──────────────────────────────────────┐
│                  API Gateway / Load Balancer                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼────┐  ┌──────▼──────┐  ┌───▼─────────┐
│  FastAPI   │  │   Ollama    │  │     n8n     │
│  Backend   │  │  (Local LLM)│  │ (Orchestr.) │
└─────┬──────┘  └──────┬──────┘  └───────┬─────┘
      │                │                 │
      └────────────────┼─────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼────┐  ┌──────▼──────┐  ┌───▼─────────┐
│  Supabase  │  │    Redis    │  │   Discord   │
│    (DB)    │  │   (Cache)   │  │     Bot     │
└────────────┘  └─────────────┘  └─────────────┘
```

### Data Flow

1. **User Input** → Frontend React App
2. **API Request** → FastAPI Backend
3. **Authentication** → Supabase Auth
4. **Data Processing** → Business Logic Layer
5. **Database Operations** → Supabase PostgreSQL
6. **Caching** → Redis (optional)
7. **AI Features** → Ollama/Embeddings
8. **Orchestration** → n8n Workflows
9. **Response** → Frontend React App

## 📊 Load Testing

Run load tests using Locust:

```bash
# Start Locust
locust -f load-tests/locustfile.py

# Access web interface at http://localhost:8089
```

## 🐳 Docker & Docker Compose

### Build Individual Services

```bash
# Backend
docker build -t nutriguard-backend:latest backend/

# Frontend
docker build -t nutriguard-frontend:latest frontend/
```

### Docker Compose Services

The `docker-compose.yml` includes:
- **Ollama** - Local LLM for AI features
- **Open WebUI** - Admin interface for Ollama
- **n8n** - Workflow orchestration
- **Redis** - Caching layer
- **Backend** (optional)
- **Frontend** (optional)

## ☸️ Kubernetes Deployment

Deploy to Kubernetes cluster:

```bash
# Apply all manifests
kubectl apply -f kubernetes/

# Check status
kubectl get pods -l app=nutriguard

# View logs
kubectl logs -f deployment/backend-deployment

# Port forward for local testing
kubectl port-forward svc/backend-service 8000:8000
kubectl port-forward svc/frontend-service 5173:5173
```

## 🔐 Environment Variables

### Backend (.env)

```env
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Discord Bot
DISCORD_BOT_TOKEN=your_discord_token

# Redis
REDIS_URL=redis://localhost:6379

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## 📈 Performance Considerations

- **Rate Limiting**: Implemented with SlowAPI to prevent abuse
- **Caching**: Redis for improved response times
- **Database Indexing**: Optimized queries with proper indexes
- **Semantic Search**: Embedding-based search for better results
- **Pagination**: Large result sets use pagination

## 🔧 Development Workflow

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and test locally
3. Run tests and linting
4. Commit with clear messages: `git commit -m "feat: add feature"`
5. Push to remote: `git push origin feature/your-feature`
6. Create a pull request for review

## 🐛 Troubleshooting

### Backend Issues

- **Database Connection Error**: Check Supabase credentials in .env
- **Redis Connection**: Ensure Redis is running on specified port
- **Discord Bot Not Working**: Verify Discord bot token and permissions

### Frontend Issues

- **API Connection**: Check `VITE_API_URL` environment variable
- **Authentication Failed**: Clear browser cache and try again
- **Build Errors**: Run `npm install` and `npm run build`

### Docker Issues

- **Port Already in Use**: Change port mapping in docker-compose.yml
- **Out of Disk Space**: Prune Docker images: `docker system prune`
- **Container Won't Start**: Check logs: `docker logs container_name`

## 📝 License

[Add your project license here]

## 👥 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues and questions, please create an issue on the repository.

---

**Last Updated**: April 2026
**Version**: 2.0.0
