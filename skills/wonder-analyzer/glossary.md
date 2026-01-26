# Wonder Business Glossary

Business terms and their code mappings. Update this file as new terms are discovered.

> **Note**: This is a living document. If code implementation differs from documentation, code is the source of truth.

---

## Item Status Terms

### Dormant
- **Definition**: Items that have been inactive for an extended period
- **Business Rule**: Items become dormant after X days of no orders
- **Code Location**:
  - Enum: `backend/master-data-interface/src/.../ItemStatus.java`
  - Logic: `backend/master-data-service/src/.../ItemService.java`
- **Related Tickets**: MD-XXXXX

### Active
- **Definition**: Items available for ordering
- **Code Location**: `ItemStatus.ACTIVE`

### Inactive
- **Definition**: Items temporarily unavailable
- **Code Location**: `ItemStatus.INACTIVE`

---

## Item Types

### WSKU (Wonder SKU)
- **Definition**: Wonder's internal Stock Keeping Unit identifier
- **Format**: Alphanumeric string
- **Code Location**: `NewObjectType.WSKU`
- **Usage**: Primary identifier for inventory tracking

### BOM (Bill of Materials)
- **Definition**: List of raw materials and components needed to produce an item
- **Code Location**: `backend/internal-recipe-service/src/.../BomService.java`
- **Related Concepts**: Recipe, Ingredients

### 40-Model
- **Definition**: Schedule 40 production model items
- **Business Rule**: Special handling for production scheduling
- **Code Location**: TBD

---

## Operations Terms

### Hot Hold
- **Definition**: Temperature holding requirements for food items
- **Business Rule**: Specifies how long and at what temperature food can be held
- **Code Location**:
  - Model: `backend/domain-library/src/.../HotHoldConfig.java`
  - Service: TBD
- **Related**: Food safety, temperature monitoring

### Pack Size
- **Definition**: Standard packaging sizes for products
- **Business Rule**: Determines how products are packaged for distribution
- **Code Location**: `backend/product-catalog-*/src/.../PackSize.java`

### ERP Sync
- **Definition**: Synchronization with Enterprise Resource Planning system
- **Process**: Batch sync of master data between Wonder and ERP
- **Code Location**:
  - Service: `backend/master-data-sync-service/`
  - Jobs: `backend/master-data-job-service/`
- **Related Tickets**: Various migration tickets

---

## Recipe Terms

### Recipe
- **Definition**: Instructions and ingredients for producing a menu item
- **Code Location**:
  - Model: `backend/internal-recipe-service/src/.../Recipe.java`
  - Service: `backend/internal-recipe-service/src/.../RecipeService.java`

### Benchtop Recipe
- **Definition**: Recipe prepared at a benchtop station
- **Code Location**: `NewObjectType.BENCHTOP`

### HDR Recipe
- **Definition**: High-Definition Recipe with detailed preparation steps
- **Code Location**: `NewObjectType.HDR_RECIPE`

### Subrecipe
- **Definition**: A recipe component used as ingredient in other recipes
- **Code Location**: `NewObjectType.ORIGINAL_SUBRECIPE`

---

## Object Types Reference

Located: `backend/domain-library/src/main/java/app/internalrecipe/item/innerclassview/NewObjectType.java`

| Type | Description |
|------|-------------|
| MENU | Menu items |
| PACKAGED | Packaged products |
| RECIPE | Recipe items |
| BENCHTOP | Benchtop recipes |
| BY_PRODUCT | By-products |
| HDR_RECIPE | HDR recipes |
| NON_FOOD | Non-food items |
| INGREDIENT | Ingredients |
| ORIGINAL | Original items |
| ORIGINAL_SUBRECIPE | Original subrecipes |
| WSKU | Wonder SKU items |
| HDR_CONSUMABLE_ITEM | HDR consumable items |

---

## Service Modules Reference

| Domain | Module | Description |
|--------|--------|-------------|
| Recipe | `backend/internal-recipe-service` | Recipe management |
| Recipe API | `backend/recipe-service-v2` | Public recipe API |
| Product | `backend/product-catalog-service` | Product catalog |
| Master Data | `backend/master-data-service` | Core data management |
| Sync | `backend/master-data-sync-service` | ERP synchronization |

---

## How to Update This Glossary

1. When discovering a new business term, add it to the appropriate section
2. Include:
   - Clear definition
   - Business rules (if any)
   - Code location (file paths)
   - Related Jira tickets
3. Verify code location is accurate before adding
4. If code changes, update this document accordingly

---

*Last Updated: 2026-01-18*
