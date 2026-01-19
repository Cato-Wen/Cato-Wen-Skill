# Wonder Domain Glossary

This file maps business terms to code patterns and locations in the Wonder monorepo.

## Object Types

Source: `backend/domain-library/src/main/java/app/internalrecipe/item/innerclassview/NewObjectType.java`

| Business Term | Enum Value | Code Pattern | Primary Services |
|--------------|------------|--------------|------------------|
| Menu Item | MENU | `Menu*`, `BOMenu*` | internal-recipe-service |
| Packaged Product | PACKAGED | `Package*`, `BOPackage*` | internal-recipe-service |
| Recipe | RECIPE | `Recipe*`, `BORecipe*` | internal-recipe-service, recipe-service-v2 |
| Benchtop Recipe | BENCHTOP | `Benchtop*`, `BOBenchtop*` | internal-recipe-service |
| By-Product | BY_PRODUCT | `ByProduct*` | internal-recipe-service |
| HDR Recipe | HDR_RECIPE | `HDR*`, `Hdr*` | internal-recipe-service |
| Non-Food Item | NON_FOOD | `NonFood*` | internal-recipe-service |
| Ingredient | INGREDIENT | `Ingredient*` | internal-recipe-service |
| Original Item | ORIGINAL | `Original*` | internal-recipe-service |
| Original Subrecipe | ORIGINAL_SUBRECIPE | `OriginalSubrecipe*` | internal-recipe-service |
| Wonder SKU (WSKU) | WSKU | `WSKU*`, `WonderSku*`, `BOItemWSKU*` | internal-recipe-service |
| HDR Consumable | HDR_CONSUMABLE_ITEM | `HDRConsumable*` | internal-recipe-service |

## Business Workflows

| Business Term | Code Pattern | Primary Files | Description |
|--------------|--------------|---------------|-------------|
| 40-Model Item | `40Model`, `40Module`, `Schedule40` | `BOPackageIs40ModuleServiceUtil.java`, `BOUpdatePackage40ModelService.java` | Schedule 40 production model for packaged items |
| 41-Model Item | `41Model` | Various service files | Schedule 41 production model |
| Dormant | `Dormant*`, `dormant` | `AnalysisDormantService.java`, `AnalysisUndormantService.java`, `BulkDormantExecutionLog.java` | Item dormancy workflow - marking items inactive |
| Undormant | `Undormant*`, `undormant` | `AnalysisUndormantService.java` | Reactivating dormant items |
| ERP Sync | `ERP*`, `Erp*` | `BOERPItemFieldService.java`, `ERPItemField.java` | Enterprise Resource Planning data synchronization |
| Hot Hold | `HotHold*`, `hotHold` | Various internal-recipe files | Temperature holding requirements for food items |
| Pack Size | `PackSize*`, `packSize` | `BOPackSizeLinkQueryService.java`, `PackSizeChangeLog.java` | Product packaging size management |
| BOM | `BOM*`, `Bom*`, `bom` | `BOBOMService.java`, various BOM files | Bill of Materials - component listing |
| Version | `Version*`, `ItemVersion*` | `BOItemVersionService.java`, `BOPublishItemVersionBuilder.java` | Item version management and publishing |
| Change Ticket | `ChangeTicket*` | `BOChangeTicketService.java`, changeticket package | Change request tracking system |
| Cost | `Cost*`, `cost` | `BOTransferCostChangeLogService.java`, various cost services | Item cost management |
| Allergen | `Allergen*`, `allergen` | Allergen service files | Food allergen tracking |
| Attribute | `Attribute*`, `attribute` | Attribute service files, `attributeV2` frontend | Item attribute management |
| Customization | `Customization*`, `customization` | Customization service files | Menu item customizations |
| Facility | `Facility*`, `facility` | `BOFacilityService.java`, facility package | Facility/location management |
| Commissary | `Commissary*`, `commissary` | Various service files | Central production facility |
| Concept | `Concept*`, `concept` | Concept service files, `concepts` frontend | Business concept management |

## Frontend Pages to Backend Mapping

| Frontend Page | Path | Backend Service | Business Domain |
|--------------|------|-----------------|-----------------|
| Item Detail | `recipe-site-frontend/src/page/itemDetail/` | internal-recipe-service | Core item management |
| Recipes | `recipe-site-frontend/src/page/recipes/` | recipe-service-v2, internal-recipe-service | Recipe viewing |
| Attributes | `recipe-site-frontend/src/page/attributeV2/` | internal-recipe-service | Attribute management |
| Configurations | `recipe-site-frontend/src/page/configurations/` | internal-recipe-service | System config |
| ERP Item Field | `recipe-site-frontend/src/page/erpItemField/` | internal-recipe-service | ERP field mapping |
| Change History | `recipe-site-frontend/src/page/changeHistory/` | internal-recipe-service | Change tracking |
| Concepts | `recipe-site-frontend/src/page/concepts/` | internal-recipe-service | Concept management |
| Pack Size | `recipe-site-frontend/src/page/packSize/` | internal-recipe-service | Pack size management |

## Search Patterns by Business Concept

### To find code related to a business term:

**Dormant workflow:**
```bash
rg -i "dormant" C:/CT-Project/backend --type java
```

**WSKU management:**
```bash
rg -i "wsku\|wondersku" C:/CT-Project/backend --type java
```

**BOM operations:**
```bash
rg -i "BOM" C:/CT-Project/backend/internal-recipe-service --type java
```

**Version publishing:**
```bash
rg -i "publishversion\|itemversion" C:/CT-Project/backend --type java
```

**ERP integration:**
```bash
rg -i "erp" C:/CT-Project/backend/internal-recipe-service --type java
```

## Jira Ticket Patterns

Jira tickets follow the pattern `MD-XXXXX` (5-digit number).

Common ticket categories (from commit tags):
- `[bug]` - Bug fixes
- `[ERP]` - ERP-related changes
- `[Migration]` - Data migration changes
- `[feature]` - New feature implementations

To find code related to a ticket:
```bash
git -C "C:/CT-Project" log --all --oneline --grep="MD-17329"
```

## MS Card Reference

MS Cards document business requirements in format `MSxx-yy`:
- **MS05 series**: Item detail UI cards (14 cards)
- **MS06 series**: BOM and component operations
- **MS08 series**: Major operations (12 cards)
- **MS13 series**: Complex features (11 cards)
- **MS15 series**: Additional operations (9 cards)

See `references/ms-cards/index.md` for the full index.
