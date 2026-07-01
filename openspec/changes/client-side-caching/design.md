## Context

The Scripture Stories frontend is a single-page Vue.js application served statically from `/frontend/index.html`. It currently fetches story structures and slides from the `/api/stories` and `/api/content` endpoints of a local backend, and displays images hosted on `https://www.churchofjesuschrist.org`. Without internet/local server connectivity, the user cannot read the stories. Implementing local caching and pre-fetching will enable a fully offline reading experience once a book or story has been downloaded.

## Goals / Non-Goals

**Goals:**
- Enable caching of visited scripture stories (text + images) automatically.
- Provide a pre-fetch feature for entire scripture books (Old Testament, New Testament, Book of Mormon, Doctrine and Covenants).
- Include a visual progress bar during pre-fetching.
- Optimize download speed by making asynchronous parallel requests to the backend.
- Configure the cache to persist indefinitely.
- Add settings options to clear the cache for a single story or a whole book.

**Non-Goals:**
- Caching the backend application itself (only frontend caching).
- Supporting automated periodic background syncs without user intervention.
- Implementing cache expiration policies (the content is static).

## Decisions

### Decision 1: Service Worker + Cache Storage API for Client-Side Caching

We will implement a Service Worker (`sw.js`) in combination with the browser's Cache Storage API.

- **Rationale**:
  - Image assets are hosted on `https://www.churchofjesuschrist.org`, which may not return permissive CORS headers.
  - A Service Worker can intercept `<img>` network requests and cache opaque responses (`mode: 'no-cors'`). This ensures images are successfully cached and served offline without causing browser security errors or requiring complex blob object URL conversions in the main Vue application code.
  - API responses (`/api/stories`, `/api/content`) can also be intercepted and cached seamlessly.
  - Since Cache Storage API is shared between the main page script and the Service Worker, the main Vue application can inspect cache contents and delete items (to implement clearing of cache) directly.

- **Alternatives Considered**:
  - **IndexedDB for text + Blob URLs for images**: Requires downloading images as blobs. If the image server doesn't support CORS, `fetch` will fail. Thus, this is not viable for cross-origin images without CORS support.
  - **LocalStorage**: Limited to 5MB, which is too small for caching multiple stories with image data.

### Decision 2: Cache Management Strategy

- **Cache Keys**:
  - API requests: `/api/stories?volume=...` and `/api/content?url=...`
  - Image URLs: `https://www.churchofjesuschrist.org/...`
- **Cache Name**: `scripture-stories-v1`
- **Clearing Cache**:
  - To clear a story: The frontend deletes the story's `/api/content?url=...` entry from the cache. It also deletes the corresponding slide images if they are not used by other cached stories. To keep it simple, we can delete the content entry and all slide images retrieved from that story's slides JSON.
  - To clear a book: The frontend retrieves the list of story URLs for that book, and deletes their `/api/content?url=...` entries along with all their slide images.
- **Detection of Cached Status**:
  - A story is considered cached if its `/api/content?url=...` response is present in the cache.
  - A book is considered fully cached if all of its stories' content responses are present in the cache.

### Decision 3: Pre-fetching Mechanics

- **Parallel Downloading**: When a user clicks "Pre-fetch" for a book, the frontend will:
  1. Fetch the list of stories for that book if not already loaded.
  2. Map stories to a list of content fetch operations: `fetch('/api/content?url=...')`.
  3. Execute these content fetches in parallel (with a concurrency limit or direct `Promise.all` since the volume is reasonable).
  4. For each completed content fetch, parse the slides, extract all slide image URLs, and initiate fetches for those images.
  5. Track the overall progress: `(completed_tasks / total_tasks) * 100`.
  6. Display a modal or panel with a progress bar and percentage indicator during pre-fetching.

## Risks / Trade-offs

- **Risk: Browser Storage Quotas**
  - *Description*: Browsers limit the size of cache storage (typically percentage of free disk space).
  - *Mitigation*: Scripture stories and compressed image assets are small in aggregate (usually under 100-200MB total for all books). The UI will display settings to clear cache to allow users to free up space.
- **Risk: Outdated Cache**
  - *Description*: Caching resources indefinitely could lead to stale content if stories or API contracts change.
  - *Mitigation*: The scriptures do not change, but if the API structure changes, registering a new Service Worker with a bumped cache version (e.g., `scripture-stories-v2`) will automatically clear the old cache and fetch fresh files.
