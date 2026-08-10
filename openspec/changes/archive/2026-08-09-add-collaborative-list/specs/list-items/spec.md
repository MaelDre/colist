## Purpose

Lets anyone with access to a list add, edit, and remove the items it contains, each carrying a name and an optional description.

## ADDED Requirements

### Requirement: Add an item

The system SHALL allow any visitor with access to a list to add an item with a required name and an optional description.

#### Scenario: Adding an item with a name and description

* **WHEN** a visitor adds an item providing both a name and a description
* **THEN** the system creates the item with both values stored

#### Scenario: Adding an item with only a name

* **WHEN** a visitor adds an item providing a name and no description
* **THEN** the system creates the item with an empty description

#### Scenario: Rejecting an item without a name

* **WHEN** a visitor attempts to add an item without providing a name
* **THEN** the system rejects the request and does not create the item

### Requirement: Edit an item

The system SHALL allow any visitor with access to a list to change an existing item's name and/or description.

#### Scenario: Editing an item's name and description

* **WHEN** a visitor submits a new name and/or description for an existing item
* **THEN** the system updates the item to reflect the submitted values

### Requirement: Remove an item

The system SHALL allow any visitor with access to a list to permanently remove an item from it.

#### Scenario: Removing an item

* **WHEN** a visitor removes an item from a list
* **THEN** the system deletes that item and it no longer appears in the list's contents