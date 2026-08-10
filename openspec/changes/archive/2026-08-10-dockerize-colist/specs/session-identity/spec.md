# session-identity Specification

## MODIFIED Requirements

### Requirement: Assign a session and color per list

The system SHALL assign a visitor a session identity and a randomly chosen color the first time they access a given list, persisted via a cookie scoped to that list, and SHALL reuse that same session and color on subsequent visits to the same list from the same browser. The session cookie SHALL be marked `Secure` whenever the request is served over HTTPS (directly, or as reported by a trusted reverse proxy's forwarded-proto header), and SHALL remain usable over plain HTTP in local development.

#### Scenario: First-time visitor receives a session and color

* **WHEN** a visitor accesses a list for the first time
* **THEN** the system assigns them a session cookie scoped to that list and a randomly chosen color

#### Scenario: Returning visitor keeps their color

* **WHEN** a visitor with an existing session cookie for a list reloads or revisits that list
* **THEN** the system recognizes their existing session and keeps their previously assigned color

#### Scenario: Same browser, multiple tabs, same list

* **WHEN** a visitor opens the same list in a second browser tab within the same browser
* **THEN** the system treats both tabs as the same session, sharing the same color

#### Scenario: Same visitor, different lists

* **WHEN** the same visitor accesses two different lists
* **THEN** the system assigns independent sessions and colors, not linked to each other

#### Scenario: Session cookie is Secure over HTTPS

* **WHEN** a visitor accesses a list over HTTPS, directly or via a reverse proxy that reports the original request as HTTPS
* **THEN** the session cookie is set with the `Secure` attribute

#### Scenario: Session cookie still works over local HTTP

* **WHEN** a visitor accesses a list over plain HTTP in local development
* **THEN** the session cookie is set without the `Secure` attribute, and the session still functions
