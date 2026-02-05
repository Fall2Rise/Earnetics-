# OpenMemory Guide

## User Defined Namespaces
- frontend
- backend
- infrastructure

## Overview
AI Revenue Command Center with React frontend and FastAPI backend.

## Architecture
- Frontend: Vite + React + Tailwind + React Three Fiber
- Backend: FastAPI + Python Agents
- Database: SQLite (business, audit, vector)

## Project Info
- **Official Domains**: The AI agents operate on `fallat.digital` and `earnetics.live`. They can use these domains as needed for the agenda.
- **Config**: `SITE_BASE_URL` is `https://www.fallat.digital`. `SECONDARY_SITE_URL` is `https://www.earnetics.live`.

## Components
- **EnvironmentScene**: 3D scene component using `react-three-fiber`. Loads textures from `/public`.

## Patterns
- **Frontend Asset Loading**: Static assets must be in the project root `public/` directory (e.g., `favicon.png`).

## Debug
- **Fix: favicon.png load error**: `EnvironmentScene` failed to load `/favicon.png` because `public` folder was nested in `fallat_crewai_dashboard/fallat_crewai_dashboard/public`. Moved to `fallat_crewai_dashboard/public`.
