# realtime-collaboration Specification

## Purpose

Keeps everyone viewing a list in sync in real time: changes propagate live, concurrent edits resolve predictably, recent edits are visually attributed by color, and reconnecting clients never end up permanently out of sync.

## Requirements

### Requirement: Live broadcast of changes
The system SHALL push item additions, edits, and removals to every client currently connected to a list, so changes appear for other visitors without a page reload.

#### Scenario: Change appears live for other visitors
- **WHEN** one visitor adds, edits, or removes an item in a list
- **THEN** every other visitor currently connected to that list sees the change reflected without reloading the page

### Requirement: Last-write-wins conflict resolution
The system SHALL resolve concurrent edits to the same item using last-write-wins: when two edits to the same item are submitted close together, the one the system receives last SHALL be the one persisted and broadcast, and all clients SHALL converge to that same final state.

#### Scenario: Concurrent edits to the same item converge
- **WHEN** two visitors submit edits to the same item at nearly the same time
- **THEN** the system persists only the later-received edit, and all connected clients end up displaying that same final value

### Requirement: Edit attribution highlight
The system SHALL visually mark an item with the color of the session that last modified it, and SHALL fade that highlight out over time.

#### Scenario: Edited item shows the editor's color
- **WHEN** a visitor's session edits an item
- **THEN** the item is displayed tagged with that session's color to all connected visitors

#### Scenario: Highlight fades over time
- **WHEN** enough time has passed since an item was last edited
- **THEN** the system fades the edit-attribution highlight until it is no longer shown

### Requirement: Reconnect fetches full state before resubscribing
The system SHALL require any client that is connecting or reconnecting to a list to fetch the full current list state over HTTP before it begins relying on live WebSocket updates, so that updates missed while disconnected are never permanently lost.

#### Scenario: Fresh load fetches full state first
- **WHEN** a client loads a list for the first time in a session
- **THEN** it fetches the complete current list state via HTTP before subscribing to live updates

#### Scenario: Reconnecting after a dropped connection resyncs
- **WHEN** a client's WebSocket connection drops and later reconnects
- **THEN** the client re-fetches the full current list state via HTTP before resuming to apply live updates
