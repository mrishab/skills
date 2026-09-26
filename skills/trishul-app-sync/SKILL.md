---
name: trishul-app-sync
description: Synchronizes backend and frontend by running the backend build, generating openapi.json, and then building the frontend to generate TypeScript models and hooks. Use this when backend models or APIs are updated and need to be reflected in the frontend.
---

# Trishul App Sync Skill

This skill provides a standardized workflow for synchronizing the backend and frontend of a Trishul-based application.

## Synchronization Workflow

### 1. Backend Build and OpenAPI Generation

- **Command**: Run `make install` in the `backend/` directory.
- **Verification**: Ensure the build completes successfully and `backend/api/openapi.json` is updated.
- **Note**: The backend build automatically generates the OpenAPI specification from the Spring Boot controllers (springdoc). `make install` is docker-backed (`mvn clean install`); no local Maven needed.

### 2. Frontend Model & Hook Generation (orval)

- **Command**: In `web/`, run `npm run generate:orval` (the `npm run build` pipeline also runs it). Requires Node `>=24.13`.
- **Verification**: Check `web/src/lib/api/model` and `web/src/lib/api/client.ts` for updated files.
- **Note**: orval consumes `backend/api/openapi.json` and generates type-safe React hooks and models. Generated files are tracked but must never be hand-edited — regenerate instead.

### 3. Model Replacement

- **Process**:
    1. Identify mock data models in `web/src/lib/mockData.ts` or other mock files.
    2. Replace usages of mock models with the auto-generated models from `web/src/lib/api/model`.
    3. Update frontend pages to use the auto-generated hooks (e.g., `useGetAllCustomers`, `useAddOrder`) instead of mock data fetching.

## Enum & type changes

- When a backend field becomes a real enum (e.g. `@Enumerated(EnumType.STRING)`), orval emits a generated const-object enum (e.g. `orderDtoStatus.ts`) rather than a free-form `string`. Update any hand-rolled union types to alias the generated type (e.g. `export type OrderStatus = OrderDtoStatus;`).
- After the backend build, stale generated models for removed endpoints are NOT auto-deleted by orval — manually `git rm` them and drop their `export * from "./..."` lines from the generated `index.ts` and any `exports-*.ts` batch barrels.

## Troubleshooting

- **Build Failures**: If `make install` fails, resolve compilation errors in the backend first.
- **Missing Fields**: If the frontend needs a field not present in the generated model, update the backend `Base<Entity>`, `Entity`, and `Dto` classes, then restart the sync process.
- **Generation Issues**: If `npm run generate:orval` fails to generate models, verify `web/orval.config.ts` points to the correct `openapi.json` path.
- **Stale references**: If generated `index.ts`/`exports-*.ts` still reference endpoints that were removed from the backend, clean those barrel lines by hand after regenerating.