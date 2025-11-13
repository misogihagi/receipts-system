# Project Structure

This document defines the proposed file and directory structure for the receipts system project.

## Root Directory

The root directory should contain configuration files and top-level folders for different parts of the application.

- **`.kiro/`**: Contains steering and specification files for AI-driven development.
- **`docs/`**: Project documentation.
- **`src/`**: All source code for the application.
- **`.gitignore`**: Specifies files to be ignored by Git.
- **`README.md`**: Project overview and setup instructions.
- **`package.json`**: Frontend dependencies and scripts (if using Node.js).
- **`requirements.txt`**: Backend dependencies (if using Python).

## Source Directory (`src/`)

The `src/` directory is organized by feature or responsibility.

- **`api/`**: Backend server code, including API endpoints, controllers, and routing.
- **`app/`**: Frontend application code, including UI components, pages, and state management.
- **`services/`**: Shared business logic, such as the OCR processing service, that can be used by both the API and other parts of the system.
- **`database/`**: Database-related files, such as schemas, models, and migration scripts.
- **`types/`**: Shared data type definitions (e.g., TypeScript interfaces) used across the application.
- **`utils/`**: Utility functions and helpers.

## File Naming Conventions

- **Components**: Use `PascalCase` (e.g., `ReceiptScanner.tsx`).
- **Modules/Services**: Use `kebab-case` (e.g., `ocr-parser.js`).
- **Configuration**: Use `kebab-case` (e.g., `vite.config.js`).
