# Wonder Module Architecture Map

This file documents the service responsibilities and module organization in the Wonder monorepo.

## Project Overview

**Project Name**: Wonder - Food Service Business Management Platform
**Type**: Monorepo with backend services and frontend applications
**Location**: `C:\CT-Project`

## Backend Services

### Core Domain Services

| Service | Path | Database | Description |
|---------|------|----------|-------------|
| internal-recipe-service | `backend/internal-recipe-service/` | MongoDB | Core recipe and item management - most complex service |
| recipe-service-v2 | `backend/recipe-service-v2/` | MongoDB | Public recipe API (gRPC) |
| product-catalog-service | `backend/product-catalog-service/` | MySQL | Product catalog gRPC service |
| product-catalog-internal-service | `backend/product-catalog-internal-service/` | MySQL | Internal product catalog API |
| product-catalog-sync-service | `backend/product-catalog-sync-service/` | MySQL | Product catalog data sync |
| product-catalog-scheduler-service | `backend/product-catalog-scheduler-service/` | MySQL | Product catalog scheduling |

### Master Data Services

| Service | Path | Purpose |
|---------|------|---------|
| master-data-scheduler-service | `backend/master-data-scheduler-service/` | Orchestration and scheduling |
| master-data-file-service | `backend/master-data-file-service/` | File processing, PDF/Excel generation |
| master-data-agent-service | `backend/master-data-agent-service/` | AI/agent operations (LangChain4j) |
| master-data-mongo-stream | `backend/master-data-mongo-stream/` | MongoDB change stream processing |
| master-data-mongo-document-compare-service | `backend/master-data-mongo-document-compare-service/` | Document comparison |
| master-data-non-critical-business-service | `backend/master-data-non-critical-business-service/` | Non-critical operations |
| master-data-backend-test-service | `backend/master-data-backend-test-service/` | Testing utilities |

### Shared Libraries

| Library | Path | Purpose |
|---------|------|---------|
| domain-library | `backend/domain-library/` | Core domain models, enums, value objects |
| common-library | `backend/common-library/` | Common utilities, MongoDB ops, Kafka clients |
| service-common-library | `backend/service-common-library/` | Service base, feature flags (DevCycle), Azure integration |
| product-catalog-domain-library | `backend/product-catalog-domain-library/` | Product catalog domain models |

### Tool Modules

| Tool | Path | Purpose |
|------|------|---------|
| mapper | `tool/mapper/` | MapStruct entity mapping |
| email-library | `tool/email-library/` | SendGrid email integration |
| jira-library | `tool/jira-library/` | Jira API integration |
| executor-library | `tool/executor-library/` | Task execution utilities |
| data-reset-service | `tool/data-reset-service/` | Development data reset |

## Frontend Applications

### Recipe Site Frontend

**Path**: `frontend/recipe-site-frontend/`
**Tech Stack**: React 18, TypeScript, Vite, Ant Design, Tailwind CSS
**Port**: 6443 (HTTPS)

#### Page Modules

| Page | Path | Business Function |
|------|------|-------------------|
| itemDetail | `src/page/itemDetail/` | Core item management |
| recipes | `src/page/recipes/` | Recipe viewing/management |
| attributeV2 | `src/page/attributeV2/` | Attribute management |
| configurations | `src/page/configurations/` | System configuration |
| erpItemField | `src/page/erpItemField/` | ERP field mapping |
| changeHistory | `src/page/changeHistory/` | Change tracking |
| concepts | `src/page/concepts/` | Concept management |
| packSize | `src/page/packSize/` | Pack size management |
| item | `src/page/item/` | Item listing |
| allergen | `src/page/allergen/` | Allergen management |
| account | `src/page/account/` | User account |

### Product Catalog Site Frontend

**Path**: `frontend/product-catalog-site-frontend/`
**Purpose**: Product catalog management UI

## Service Communication Patterns

### gRPC Services

Protocol buffer definitions in `backend/protos/` (git submodule)

| Proto | Services |
|-------|----------|
| recipe-service-v2 | Public recipe APIs |
| product-catalog-service | Product catalog APIs |

### Kafka Topics

Message-driven architecture for:
- Attribute changes
- Allergen updates
- Recipe synchronization
- Item version events

## Database Organization

| Database | Type | Services |
|----------|------|----------|
| Recipe DB | MongoDB | internal-recipe-service, recipe-service-v2 |
| Product Catalog DB | MySQL | product-catalog-* services |
| Cosmos DB | Azure | Some features |

## Key Packages in internal-recipe-service

The most complex service with these main packages:

```
backend/internal-recipe-service/src/main/java/app/
├── internalrecipe/
│   ├── item/              # Core item management
│   │   ├── domain/        # Domain models
│   │   ├── service/       # Business logic (BO* services)
│   │   ├── web/           # REST controllers
│   │   └── kafka/         # Kafka handlers
│   ├── changeticket/      # Change ticket management
│   ├── facility/          # Facility management
│   ├── allergen/          # Allergen tracking
│   ├── attribute/         # Attribute management
│   └── ...
```

## Naming Conventions

### Backend
- `BO*Service.java` - Business Object services (main business logic)
- `*Builder.java` - Builder pattern implementations
- `*QueryService.java` - Query/read operations
- `*ChangeLog.java` - Change tracking entities
- `*StreamService.java` - MongoDB stream handlers

### Frontend
- `page/` - camelCase directories for page modules
- Components - PascalCase directories
- Each component has `index.tsx` entry point

## Finding Code by Business Function

| Business Need | Primary Location | Key Files |
|---------------|-----------------|-----------|
| Item CRUD | internal-recipe-service | `BO*ItemService.java` |
| Version management | internal-recipe-service | `BOItemVersionService.java`, `BOPublishItemVersionBuilder.java` |
| Dormant workflow | internal-recipe-service | `AnalysisDormantService.java` |
| ERP integration | internal-recipe-service | `BOERPItemFieldService.java` |
| BOM operations | internal-recipe-service | `BOBOMService.java`, BOM* files |
| Change tracking | internal-recipe-service | changeticket package |
| Product catalog | product-catalog-* | product-catalog services |
| File generation | master-data-file-service | PDF/Excel handlers |
