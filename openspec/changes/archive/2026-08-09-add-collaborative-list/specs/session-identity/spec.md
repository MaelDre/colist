## Purpose

Gives each visitor of a list an ephemeral, cookie-based identity and color scoped to that list, and shows who else is currently present, without any accounts or usernames.

## ADDED Requirements

### Requirement: Assign a session and color per list
The system SHALL assign a visitor a session identity and a randomly chosen color the first time they access a given list, persisted via a cookie scoped to that list, and SHALL reuse that same session and color on subsequent visits to the same list from the same browser.

#### Scenario: First-time visitor receives a session and color
- **WHEN** a visitor accesses a list for the first time
- **THEN** the system assigns them a session cookie scoped to that list and a randomly chosen color

#### Scenario: Returning visitor keeps their color
- **WHEN** a visitor with an existing session cookie for a list reloads or revisits that list
- **THEN** the system recognizes their existing session and keeps their previously assigned color

#### Scenario: Same browser, multiple tabs, same list
- **WHEN** a visitor opens the same list in a second browser tab within the same browser
- **THEN** the system treats both tabs as the same session, sharing the same color

#### Scenario: Same visitor, different lists
- **WHEN** the same visitor accesses two different lists
- **THEN** the system assigns independent sessions and colors, not linked to each other

### Requirement: Presence indicator
The system SHALL show all visitors currently connected to a list as colored indicators, with one indicator per session (not per open tab or connection), updated as sessions connect and disconnect.

#### Scenario: New connection appears in presence
- **WHEN** a session connects to a list that has no other open tabs for that session
- **THEN** the system adds one presence indicator in that session's color, visible to all other connected visitors

#### Scenario: Additional tab does not duplicate presence
- **WHEN** a session that already has one open tab on a list opens a second tab on the same list
- **THEN** the presence indicator count for that session remains one

#### Scenario: Last connection closing removes presence
- **WHEN** a session's last open tab or connection to a list closes
- **THEN** the system removes that session's presence indicator for all other connected visitors
