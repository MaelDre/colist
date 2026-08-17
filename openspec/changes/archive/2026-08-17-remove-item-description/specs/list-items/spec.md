## MODIFIED Requirements

### Requirement: Add an item

The system SHALL allow any visitor with access to a list to add an item with a required name.

#### Scenario: Adding an item with a name

* **WHEN** a visitor adds an item providing a name
* **THEN** the system creates the item

#### Scenario: Rejecting an item without a name

* **WHEN** a visitor attempts to add an item without providing a name
* **THEN** the system rejects the request and does not create the item

### Requirement: Edit an item

The system SHALL allow any visitor with access to a list to change an existing item's name.

#### Scenario: Editing an item's name

* **WHEN** a visitor submits a new name for an existing item
* **THEN** the system updates the item to reflect the submitted name