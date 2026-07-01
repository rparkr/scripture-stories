## ADDED Requirements

### Requirement: Story Caching on Visit
The system SHALL cache a story's text, structure, and images automatically when the user visits the story.

#### Scenario: User visits a story for the first time
- **WHEN** the user selects a story from the story list and it loads
- **THEN** the story metadata, slide texts, and all slide images are saved in the client-side cache

#### Scenario: User visits an already cached story
- **WHEN** the user loads a story that has already been visited and cached
- **THEN** the system loads the text and images directly from the client-side cache, allowing offline viewing

### Requirement: Book Pre-fetching
The system SHALL provide an option to pre-fetch all stories and associated media for any selected Scripture Stories Book.

#### Scenario: User pre-fetches a book
- **WHEN** the user clicks the pre-fetch button for a book in the settings/menu
- **THEN** the system fetches all story contents and images for that book in parallel asynchronously and updates a progress bar with the download progress percentage

### Requirement: Cache Persistence
The client-side cache SHALL persist indefinitely without automatic expiration.

#### Scenario: Cache longevity
- **WHEN** the browser is closed and reopened or the device is offline
- **THEN** the cached story text and images remain available in the client-side cache

### Requirement: Cache Management Controls
The settings menu SHALL provide options to clear the cache for individual stories and for entire books.

#### Scenario: User clears cache for a story
- **WHEN** the user selects to clear cache for a specific story in the settings
- **THEN** the cached data and images for that specific story are removed from the client-side cache

#### Scenario: User clears cache for a book
- **WHEN** the user selects to clear cache for a scripture book in the settings
- **THEN** all cached stories and images associated with that book are removed from the client-side cache
