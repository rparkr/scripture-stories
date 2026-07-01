## 1. Service Worker Setup

- [x] 1.1 Create `docs/sw.js` to handle intercepting network requests for API content and cross-origin images, storing them in Cache Storage
- [x] 1.2 Register `sw.js` in `docs/index.html` upon Vue application mounting and ensure registration is successful

## 2. Frontend Cache Utilities and Management UI

- [x] 2.1 Implement helper methods in Vue app to query which stories/books are cached by inspecting Cache Storage keys
- [x] 2.2 Add settings options in the settings modal of `docs/index.html` to view cache status and clear cache for individual stories or entire books

## 3. Parallel Pre-fetching Logic and Progress UI

- [x] 3.1 Implement parallel asynchronous fetching logic in Vue app that fetches all stories and slide images for a selected Scripture Stories Book
- [x] 3.2 Implement a visual download progress bar overlay that displays downloading status, percentage, and allows canceling/closing the progress overlay
- [x] 3.3 Add download/pre-fetch buttons and status indicators to the story list and library book list

## 4. Verification and Testing

- [x] 4.1 Perform verification of offline story reading, parallel pre-fetching, progress reporting, and cache clearing actions
