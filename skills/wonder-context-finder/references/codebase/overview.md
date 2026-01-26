# Wonder Codebase Overview

## Project Structure

```
<project-root>/
├── backend/                    # Core Java/Kotlin services
│   ├── internal-recipe-service\    # Main business logic service
│   ├── recipe-service-v2\          # Public recipe API (gRPC)
│   ├── product-catalog-*\          # Product catalog services (MySQL)
│   ├── master-data-*\              # Master data services
│   ├── domain-library\             # Domain models and enums
│   ├── common-library\             # Shared utilities
│   ├── service-common-library\     # Service base functionality
│   └── protos\                     # Protocol buffer definitions (submodule)
├── frontend\                   # React/TypeScript applications
│   ├── recipe-site-frontend\       # Main recipe management UI
│   ├── product-catalog-site-frontend\  # Product catalog UI
│   └── recipe-site\                # Java backend for recipe-site
├── tool\                       # Shared utilities
│   ├── mapper\                     # MapStruct entity mapping
│   ├── email-library\              # SendGrid integration
│   ├── jira-library\               # Jira API integration
│   └── executor-library\           # Task execution
├── buildSrc\                   # Gradle plugin customizations
├── build.gradle.kts            # Root Gradle configuration
├── settings.gradle.kts         # Gradle module declarations
├── docker-compose.yml          # Local development infrastructure
├── Makefile                    # Development automation
├── CLAUDE.md                   # Claude Code guidelines
└── README.md                   # Project overview
```

## Technology Stack

### Backend
- **Language**: Java 17 (Kotlin for build config)
- **Framework**: Core-NG (custom enterprise framework)
- **Build**: Gradle with Kotlin DSL
- **Databases**: MongoDB (primary), MySQL (product catalog), Cosmos DB
- **Messaging**: Apache Kafka
- **Caching**: Redis
- **APIs**: gRPC, REST
- **Cloud**: Azure (ACR, Storage, Cosmos DB)
- **AI**: LangChain4j, Vertex AI Gemini
- **Feature Flags**: DevCycle SDK, OpenFeature

### Frontend
- **Language**: TypeScript 5.3.3
- **Framework**: React 18.2.0
- **Build**: Vite (dev), Webpack (production)
- **Package Manager**: pnpm
- **UI Library**: Ant Design 5.25.2
- **Styling**: Tailwind CSS 3.4.10, LESS
- **Routing**: React Router 6.22.3

## Key Files for Development

### Configuration
- `build.gradle.kts` - Dependencies and build configuration
- `docker-compose.yml` - Local MongoDB, Kafka, Redis setup
- `Makefile` - Common development commands

### Documentation
- `CLAUDE.md` - Claude Code guidelines for this project
- `README.md` - Project setup and prerequisites

### Domain Models
- `backend/domain-library/src/main/java/app/` - Core domain classes

## Development Commands

```bash
# Build all
./gradlew build

# Run specific service
./gradlew :backend:internal-recipe-service:bootRun

# Frontend development
cd frontend/recipe-site-frontend && pnpm dev

# Docker services
docker-compose up -d
```

## Git Workflow

- **Main branches**: `master`, `develop`
- **Feature branches**: `MD-XXXXX` or `MD-XXXXX-descriptor`
- **Commit format**: `MD-XXXXX [tag] Description`
- **Tags**: `[bug]`, `[ERP]`, `[Migration]`, `[feature]`

## Jira Integration

- **Project**: MD (Master Data)
- **Ticket format**: MD-XXXXX (5-digit number)
- **Site**: wonder.atlassian.net

Every commit references a Jira ticket for traceability.
