# Todo App

Beautiful todo list with a Python Flask backend and dark glassmorphic UI.

## Features

- Add, toggle, delete, edit (double-click or click edit button)
- Filter: All / Active / Completed
- Undo delete with toast notification
- Clear completed button
- Drag-and-drop reorder
- Relative timestamps ("2m ago", "yesterday")
- Keyboard shortcuts: Enter to add, Escape to cancel edit
- Filter persistence via localStorage
- Error handling with toast messages
- Staggered list animations, check-pop animation, slide-out delete
- Animated gradient orbs in background
- Dark glassmorphic card with backdrop blur
- Responsive design with `prefers-reduced-motion` support
- 28 Playwright E2E tests

## Stack

- **Backend**: Python / Flask (REST API, JSON file storage)
- **Frontend**: Vanilla HTML / CSS / JS (no frameworks)

## Usage

```bash
py server.py
```

Open http://localhost:5000

## Tests

```bash
playwright install chromium
py test_todo.py
```
