## Purpose

Lets anyone create a shared list and reach it through a single unguessable URL, with no accounts, and permanently remove it when it's no longer needed.

## ADDED Requirements

### Requirement: Create a list
The system SHALL allow any visitor to create a new, empty list without authentication, and SHALL assign it an unguessable unique identifier (UUID) used as its URL.

#### Scenario: Creating a list generates an unguessable URL
- **WHEN** a visitor requests to create a new list
- **THEN** the system creates an empty list and returns a URL containing a UUID that was not derivable from any prior list's URL

### Requirement: View a list by URL
The system SHALL display a list's current content to any visitor who accesses its URL, with no login required.

#### Scenario: Viewing an existing list
- **WHEN** a visitor opens a URL corresponding to a list that exists
- **THEN** the system displays that list's current items

#### Scenario: Viewing an unknown list
- **WHEN** a visitor opens a URL whose identifier does not correspond to any existing list
- **THEN** the system shows a not-found state instead of any list content

### Requirement: Delete a list
The system SHALL allow any visitor with access to a list's URL to permanently delete it, after an explicit confirmation step, and SHALL NOT provide any way to recover a deleted list.

#### Scenario: Delete requires confirmation
- **WHEN** a visitor initiates deleting a list
- **THEN** the system requires an explicit confirmation step before the deletion takes effect

#### Scenario: Confirmed deletion is permanent
- **WHEN** a visitor confirms deletion of a list
- **THEN** the system permanently removes the list and all its items, and the list's URL subsequently resolves to a not-found state for every visitor
