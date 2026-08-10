# deployment Specification

## Purpose

Defines how colist is packaged and configured for deployment: a single container image serving both the API and the built frontend, its externally configurable settings, health reporting, and the operational constraints that follow from the app's single-process design.

## ADDED Requirements

### Requirement: Single container image serves API and frontend

The system SHALL be packageable as a single container image that serves both the REST/WebSocket API and the built frontend static assets from the same origin and port.

#### Scenario: Frontend requests the API from the same origin

* **WHEN** the built frontend makes an API or WebSocket request
* **THEN** it targets a relative path on the same origin it was served from, with no separate API host configured at build time

### Requirement: Configurable CORS origin

The system SHALL read its allowed CORS origin(s) from an environment variable at startup, rather than a hardcoded value, so the same image can be deployed under any domain.

#### Scenario: Custom origin via environment variable

* **WHEN** the container is started with an allowed-origins environment variable set to a production domain
* **THEN** the API accepts cross-origin requests from that domain

#### Scenario: Unset environment variable keeps local dev behavior

* **WHEN** the allowed-origins environment variable is not set
* **THEN** the API allows the existing default local development origin

### Requirement: Persistent, volume-mountable database location

The system SHALL default to a database location, inside the container image, that lives under a dedicated directory intended for volume mounting, separate from application code, so data survives container recreation when that directory is persisted.

#### Scenario: Data survives container recreation

* **WHEN** a container is stopped and a new container is started from the same image with the same data volume mounted
* **THEN** previously created lists and items are still present

### Requirement: Health check endpoint

The system SHALL expose an HTTP endpoint reporting whether the application has completed startup and is ready to serve requests.

#### Scenario: Health check after successful startup

* **WHEN** the application has finished initializing its database connection
* **THEN** the health endpoint responds with a success status

### Requirement: Single-instance operation

The system SHALL run as a single process with a single worker; the shipped image SHALL NOT start multiple worker processes, and deployment documentation SHALL state that running multiple concurrent replicas of the image against shared state is unsupported.

#### Scenario: Image starts exactly one worker

* **WHEN** the container starts
* **THEN** it runs a single application process, with no multi-worker or multi-process server configuration

#### Scenario: Documentation warns against replication

* **WHEN** an operator consults the deployment documentation
* **THEN** it states that horizontal scaling (multiple replicas or workers) is unsupported without a shared state store

### Requirement: TLS terminated outside the image

The system SHALL serve plain HTTP internally and SHALL NOT perform TLS termination or certificate management within the container image; HTTPS SHALL be provided by the deployment environment (a PaaS-managed load balancer or an external reverse proxy).

#### Scenario: Application trusts a forwarded HTTPS scheme

* **WHEN** a request arrives via a reverse proxy that terminates TLS and sets a forwarded-proto header
* **THEN** the application treats the original request as HTTPS for purposes that depend on the scheme (such as cookie security), based on that forwarded header