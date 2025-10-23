# Taskly - Task Management with GitHub Integration

Taskly is a modern task management application that integrates seamlessly with GitHub issues, providing a powerful Kanban-style board for managing your development workflow.

## Features

- **Kanban Board**: Drag-and-drop interface for managing tasks across different stages
- **GitHub Integration**: Sync tasks with GitHub issues bidirectionally
- **Real-time Updates**: WebSocket-based real-time collaboration
- **Sprint Planning**: Create and manage sprints with velocity tracking
- **Time Tracking**: Track time spent on tasks with Pomodoro integration
- **Analytics**: Comprehensive burndown charts and velocity metrics

## Tech Stack

### Frontend
- **Next.js 14.1** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Beautiful, accessible UI components
- **Zustand** - Client state management
- **TanStack Query** - Server state management
- **@dnd-kit** - Drag-and-drop functionality

### Backend
- **FastAPI 0.109** - Modern Python web framework
- **SQLAlchemy 2.0** - Async ORM
- **PostgreSQL 15+** - Primary database
- **Redis 7.2** - Caching and real-time features
- **Celery** - Background task processing
- **UV** - Fast Python package manager

## Prerequisites

Before running Taskly, ensure you have the following installed:

- **Docker** 24.0+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose** 2.24+ (included with Docker Desktop)
- **Node.js** 20 LTS ([Install Node](https://nodejs.org/))
- **npm** 10+ (comes with Node.js)

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd taskly
```

### 2. Set Up Environment Variables

Run the setup script to create environment files:

```bash
./scripts/setup-env.sh
```

This creates:
- `backend/.env` from `backend/.env.example`
- `frontend/.env.local` from `frontend/.env.local.example`

### 3. Configure GitHub OAuth (Optional)

To enable GitHub integration:

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Fill in the details:
   - **Application name**: Taskly
   - **Homepage URL**: `http://localhost:3000`
   - **Authorization callback URL**: `http://localhost:3000/auth/callback`
4. Copy the Client ID and Client Secret
5. Update both `backend/.env` and `frontend/.env.local` with your credentials:
   ```bash
   # backend/.env
   GITHUB_CLIENT_ID=your_client_id
   GITHUB_CLIENT_SECRET=your_client_secret

   # frontend/.env.local
   NEXT_PUBLIC_GITHUB_CLIENT_ID=your_client_id
   ```

### 4. Start the Application

Start all services with Docker Compose:

```bash
docker-compose up
```

Or use the npm script:

```bash
npm run dev
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## Common Commands

### Development

```bash
# Start all services
docker-compose up

# Start services in background (detached mode)
docker-compose up -d

# Stop all services
docker-compose down

# View logs for all services
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart a specific service
docker-compose restart backend
```

### Working with Services

```bash
# Execute command in backend container
docker-compose exec backend bash

# Execute command in frontend container
docker-compose exec frontend sh

# Run database migrations
docker-compose exec backend alembic upgrade head

# Create a new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Run backend tests
docker-compose exec backend pytest

# Run frontend tests
docker-compose exec frontend npm test
```

### Maintenance

```bash
# Remove all containers, networks, and volumes
docker-compose down -v

# Rebuild containers after dependency changes
docker-compose up --build

# View running containers
docker-compose ps

# Check resource usage
docker stats
```

## Project Structure

```
taskly/
├── frontend/                # Next.js frontend application
│   ├── src/
│   │   ├── app/            # Next.js App Router pages
│   │   ├── components/     # React components
│   │   ├── lib/            # Utilities and configurations
│   │   └── types/          # TypeScript type definitions
│   ├── public/             # Static assets
│   ├── Dockerfile          # Frontend container definition
│   └── package.json        # Frontend dependencies
├── backend/                # FastAPI backend application
│   ├── app/
│   │   ├── api/           # API routes and endpoints
│   │   ├── models/        # Database models
│   │   ├── services/      # Business logic
│   │   ├── repositories/  # Data access layer
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── core/          # Core configurations
│   │   └── utils/         # Utility functions
│   ├── tests/             # Test suites
│   ├── alembic/           # Database migrations
│   ├── Dockerfile         # Backend container definition
│   └── pyproject.toml     # Backend dependencies
├── docs/                  # Project documentation
├── scripts/               # Utility scripts
├── docker-compose.yml     # Docker Compose configuration
├── package.json           # Root workspace configuration
└── README.md             # This file
```

## Development Workflow

### Hot Reload

Both frontend and backend support hot reload in development:

- **Frontend**: Changes to files in `frontend/src/` automatically refresh the browser
- **Backend**: Changes to Python files automatically restart the Uvicorn server

### Making Code Changes

1. Edit files in `frontend/` or `backend/` directories
2. Changes are automatically detected and reloaded
3. Check the logs for any errors: `docker-compose logs -f`

### Running Tests

```bash
# Backend tests
docker-compose exec backend pytest

# Frontend tests
docker-compose exec frontend npm test

# Run with coverage
docker-compose exec backend pytest --cov=app
```

### Code Quality

```bash
# Backend linting and formatting
docker-compose exec backend ruff check .
docker-compose exec backend black .
docker-compose exec backend mypy .

# Frontend linting and formatting
docker-compose exec frontend npm run lint
docker-compose exec frontend npm run format
```

## Troubleshooting

### Port Conflicts

If you see port already in use errors:

```bash
# Check what's using the port
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis

# Kill the process or change ports in docker-compose.yml
```

### Volume Permissions

If you encounter permission errors:

```bash
# On Linux/Mac, ensure proper ownership
sudo chown -R $USER:$USER data/

# Or remove volumes and recreate
docker-compose down -v
docker-compose up
```

### Health Check Failures

If services fail health checks:

```bash
# Check service logs
docker-compose logs backend
docker-compose logs postgres
docker-compose logs redis

# Verify database connection
docker-compose exec backend python -c "from app.core.database import engine; print(engine)"

# Verify Redis connection
docker-compose exec redis redis-cli ping
```

### Container Build Issues

If containers fail to build:

```bash
# Clear Docker cache and rebuild
docker-compose down
docker system prune -a
docker-compose up --build
```

### Database Issues

```bash
# Reset database
docker-compose down -v
docker-compose up -d postgres
docker-compose exec backend alembic upgrade head

# Access PostgreSQL directly
docker-compose exec postgres psql -U taskly -d taskly
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and commit: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/your-repo/issues)
- Documentation: `/docs` directory

## Acknowledgments

- Built with [Next.js](https://nextjs.org/), [FastAPI](https://fastapi.tiangolo.com/), and [PostgreSQL](https://www.postgresql.org/)
- UI components from [shadcn/ui](https://ui.shadcn.com/)
- Icons from [Lucide](https://lucide.dev/)
