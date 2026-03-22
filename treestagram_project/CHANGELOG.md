# Changelog — Home Feed Posts Feature

**Date:** March 15, 2026  

---

## Problem

`Home.svelte` imports `apiFetchPosts`, `apiToggleLike`, and `apiAddComment` from `src/lib/api.js`, but none of these functions were defined. This caused a `TypeError: apiFetchPosts is not a function` at runtime inside `onMount`, leaving the page stuck on "Loading posts…" indefinitely. Additionally, the Django backend had no Post model, no API views, and no URL routes for any post-related functionality.

---

## Files Changed

### 1. `treestagram-svelte/src/lib/api.js` (Frontend)

**What changed:** Added three missing exported functions at the bottom of the file (lines 137–155).

| Function | HTTP Method | Endpoint | Purpose |
|---|---|---|---|
| `apiFetchPosts()` | `GET` | `/api/posts/` | Fetch all posts for the feed. Returns `{ success, posts }`. Falls back to `{ success: false, posts: [] }` on error. |
| `apiToggleLike(postId)` | `POST` | `/api/posts/<postId>/like/` | Toggle a like on a post. Returns `{ success, liked, likes_count }`. |
| `apiAddComment(postId, text)` | `POST` | `/api/posts/<postId>/comment/` | Add a comment to a post. Sends `{ text }` in body. Returns `{ success, comment }`. |

---

### 2. `accounts/models.py` (Backend — Django Models)

**What changed:** Added three new models after the existing `User` model (lines 48–94).

#### `Post` model
| Field | Type | Details |
|---|---|---|
| `author` | `ForeignKey(User)` | `on_delete=CASCADE`, `related_name='posts'` |
| `tree_name` | `CharField(max_length=200)` | Name of the tree |
| `body` | `TextField(blank=True)` | Optional post body text |
| `health` | `CharField(max_length=10)` | Choices: `Good`, `Fair`, `Poor`. Default: `Good` |
| `borough` | `CharField(max_length=50, blank=True)` | Optional borough location |
| `image` | `ImageField(upload_to='post_images/')` | Optional photo upload |
| `created_at` | `DateTimeField(auto_now_add=True)` | Auto-set on creation |
| `updated_at` | `DateTimeField(auto_now=True)` | Auto-set on save |

- **Meta:** `ordering = ['-created_at']` (newest first)

#### `Like` model
| Field | Type | Details |
|---|---|---|
| `user` | `ForeignKey(User)` | `on_delete=CASCADE`, `related_name='likes'` |
| `post` | `ForeignKey(Post)` | `on_delete=CASCADE`, `related_name='likes'` |
| `created_at` | `DateTimeField(auto_now_add=True)` | Auto-set on creation |

- **Meta:** `unique_together = ('user', 'post')` — prevents duplicate likes

#### `Comment` model
| Field | Type | Details |
|---|---|---|
| `author` | `ForeignKey(User)` | `on_delete=CASCADE`, `related_name='comments'` |
| `post` | `ForeignKey(Post)` | `on_delete=CASCADE`, `related_name='comments'` |
| `text` | `TextField` | The comment text |
| `created_at` | `DateTimeField(auto_now_add=True)` | Auto-set on creation |

- **Meta:** `ordering = ['created_at']` (oldest first, chronological)

---

### 3. `accounts/api_views.py` (Backend — API Views)

**What changed:**
- **Line 21:** Updated import to include `Post`, `Like`, `Comment` from `.models`
- **Lines 410–523:** Added helper function + three new view functions

#### `_post_to_dict(post, request_user)` — Helper (line 413)
Serializes a `Post` object into a JSON-friendly dict matching the Svelte frontend's expectations. Includes:
- Post fields: `id`, `tree_name`, `body`, `health`, `borough`, `image`, `created_at`
- Nested `author`: `{ id, username }`
- `likes_count`: total likes on the post
- `liked`: boolean — whether the current `request_user` has liked it
- `comments`: array of `{ id, text, author: { id, username }, created_at }`

#### `api_posts(request)` — GET `/api/posts/` (line 447)
- Returns all posts, newest first
- Uses `select_related('author')` and `prefetch_related('likes', 'comments', 'comments__author')` for query optimization
- Response: `{ success: true, posts: [...] }`

#### `api_toggle_like(request, post_id)` — POST `/api/posts/<id>/like/` (line 462)
- Requires authentication (returns 401 if not logged in)
- Returns 404 if post doesn't exist
- Uses `get_or_create` to toggle: creates a like if none exists, deletes it if it already does
- Updates the post author's `total_likes_received` cached count
- Response: `{ success: true, liked: bool, likes_count: int }`

#### `api_add_comment(request, post_id)` — POST `/api/posts/<id>/comment/` (line 490)
- Requires authentication (returns 401 if not logged in)
- Parses `{ text }` from JSON body; returns 400 if empty
- Returns 404 if post doesn't exist
- Creates a `Comment` record
- Response: `{ success: true, comment: { id, text, author, created_at } }`

---

### 4. `accounts/api_urls.py` (Backend — URL Routing)

**What changed:** Added three new URL patterns at lines 20–23:

```
path('posts/',                       api_views.api_posts,        name='api-posts'),
path('posts/<int:post_id>/like/',    api_views.api_toggle_like,  name='api-toggle-like'),
path('posts/<int:post_id>/comment/', api_views.api_add_comment,  name='api-add-comment'),
```

All routes are under the `/api/` prefix (configured in `treestagram/urls.py` line 33).

---

### 5. Migration Created & Applied

**File:** `accounts/migrations/0002_post_comment_like.py` (auto-generated)

```
python manage.py makemigrations accounts
python manage.py migrate
```

Creates the three new database tables: `accounts_post`, `accounts_like`, `accounts_comment`.

---

## API Endpoint Summary

| Method | URL | Auth Required | Description |
|---|---|---|---|
| `GET` | `/api/posts/` | No | Fetch all posts (feed) |
| `POST` | `/api/posts/<id>/like/` | Yes | Toggle like on a post |
| `POST` | `/api/posts/<id>/comment/` | Yes | Add a comment to a post |

---

## Verification

```bash
$ curl -s http://127.0.0.1:8000/api/posts/
{"success": true, "posts": []}
```

The endpoint returns an empty posts array (no posts in DB yet). The Home feed now loads correctly and shows "No posts yet — be the first to share a tree observation! 🌱" instead of being stuck on "Loading posts…".

---
---

# Changelog — Profile Page Feature

**Date:** March 15, 2026  
**Author:** AI-assisted development  
**Summary:** `Profile.svelte` was not running because it imported four API functions (`apiFetchMyPosts`, `apiFetchMyTaggedPosts`, `apiCreatePost`, `apiDeletePost`) that did not exist in `api.js`. The corresponding Django backend endpoints and a `tagged_users` field on the `Post` model were also missing. Five files were modified and one migration was created to fix this.

---

## Problem

`Profile.svelte` imports `apiFetchMyPosts`, `apiFetchMyTaggedPosts`, `apiCreatePost`, and `apiDeletePost` from `src/lib/api.js`, but none of these functions were defined. This caused runtime errors on mount — `loadMyPosts()` and `loadTaggedPosts()` both called undefined functions, crashing the page. The profile's "Plant a Post" create flow and post deletion also had no backend support. Additionally, the `Post` model had no `tagged_users` field, so the tagging feature shown in the UI had no data layer.

---

## Files Changed

### 1. `accounts/models.py` (Backend — Django Models)

**What changed:** Added a `tagged_users` ManyToManyField to the existing `Post` model.

| Field | Type | Details |
|---|---|---|
| `tagged_users` | `ManyToManyField(User)` | `blank=True`, `related_name='tagged_posts'` |

This allows posts to tag other users. The relationship is stored in an auto-generated join table `accounts_post_tagged_users`.

---

### 2. `accounts/api_views.py` (Backend — API Views)

**What changed:**
- Updated `_post_to_dict()` helper to include `tagged_users` and `author.profile_picture` in serialized output
- Added four new view functions for profile-specific endpoints

#### `_post_to_dict` — Updated Helper
Now includes two additional fields in the serialized response:
- `author.profile_picture`: URL of the post author's profile picture (or `null`)
- `tagged_users`: array of `{ id, username }` for each tagged user

#### `api_my_posts(request)` — GET `/api/my-posts/`
- Requires authentication (returns 401 if not logged in)
- Returns all posts authored by the logged-in user, newest first
- Uses `select_related('author')` and `prefetch_related('likes', 'comments', 'comments__author', 'tagged_users')` for query optimization
- Response: `{ success: true, posts: [...] }`

#### `api_my_tagged_posts(request)` — GET `/api/my-tagged-posts/`
- Requires authentication (returns 401 if not logged in)
- Returns all posts where the logged-in user is tagged via the `tagged_users` M2M field
- Response: `{ success: true, posts: [...] }`

#### `api_create_post(request)` — POST `/api/create-post/`
- Requires authentication (returns 401 if not logged in)
- Supports both JSON and `multipart/form-data` (for image uploads)
- Accepts fields: `tree_name` (required), `body`, `health`, `borough`, `image` (file), `tagged_users` (comma-separated usernames)
- Resolves tagged usernames to `User` objects and sets the M2M relationship
- Updates the author's cached `post_count` field
- Response: `{ success: true, post: {...}, user: {...} }`

#### `api_delete_post(request, post_id)` — POST `/api/posts/<id>/delete/`
- Requires authentication (returns 401 if not logged in)
- Only the post author or an admin can delete (returns 403 otherwise)
- Returns 404 if post doesn't exist
- Updates the author's cached `post_count` after deletion
- Response: `{ success: true }`

---

### 3. `accounts/api_urls.py` (Backend — URL Routing)

**What changed:** Added four new URL patterns:

```
path('my-posts/',                      api_views.api_my_posts,         name='api-my-posts'),
path('my-tagged-posts/',               api_views.api_my_tagged_posts,  name='api-my-tagged-posts'),
path('create-post/',                   api_views.api_create_post,      name='api-create-post'),
path('posts/<int:post_id>/delete/',    api_views.api_delete_post,      name='api-delete-post'),
```

All routes are under the `/api/` prefix.

---

### 4. `treestagram-svelte/src/lib/api.js` (Frontend)

**What changed:** Added four missing exported functions used by `Profile.svelte`.

| Function | HTTP Method | Endpoint | Purpose |
|---|---|---|---|
| `apiFetchMyPosts()` | `GET` | `/api/my-posts/` | Fetch posts by the logged-in user. Returns `{ success, posts }`. Falls back to `{ success: false, posts: [] }` on error. |
| `apiFetchMyTaggedPosts()` | `GET` | `/api/my-tagged-posts/` | Fetch posts where the logged-in user is tagged. Returns `{ success, posts }`. Falls back to `{ success: false, posts: [] }` on error. |
| `apiCreatePost({ tree_name, borough, health, body, image, tagged_users })` | `POST` | `/api/create-post/` | Create a new post. Sends `FormData` (multipart) to support image upload. Returns `{ success, post, user }`. |
| `apiDeletePost(postId)` | `POST` | `/api/posts/<postId>/delete/` | Delete a post by ID. Returns `{ success }`. |

---

### 5. Migration Created & Applied

**File:** `accounts/migrations/0003_post_tagged_users.py` (auto-generated)

```
python manage.py makemigrations accounts
python manage.py migrate
```

Creates the join table `accounts_post_tagged_users` for the new ManyToManyField.

---

## New API Endpoint Summary

| Method | URL | Auth Required | Description |
|---|---|---|---|
| `GET` | `/api/my-posts/` | Yes | Fetch logged-in user's posts |
| `GET` | `/api/my-tagged-posts/` | Yes | Fetch posts where user is tagged |
| `POST` | `/api/create-post/` | Yes | Create a new post (multipart supported) |
| `POST` | `/api/posts/<id>/delete/` | Yes | Delete a post (author or admin only) |

---

## Verification

After the fix, navigating to `/profile` while logged in correctly loads the user's posts grid, supports creating new posts via the "Plant a Post" carousel, shows tagged posts under the Tagged tab, and allows post deletion through the 3-dot menu.

---
---

# Changelog — Disable Theme Toggle in Left Nav

**Date:** March 15, 2026  
**Author:** AI-assisted development  
**Summary:** The theme cycle button in the left navigation sidebar was commented out so the app uses the default theme only.

---

## Problem

The left navigation included a Theme button that allowed users to cycle between dark, light, and retro themes via `cycleTheme()`. This was disabled to keep the app on the default theme.

---

## Files Changed

### 1. `treestagram-svelte/src/components/LeftNav.svelte` (Frontend)

**What changed:** The theme toggle button (lines 65–74) was wrapped in an HTML comment (`<!-- ... -->`), effectively removing it from the rendered UI while preserving the code for potential future re-enablement.

**Before:**
```html
<button class="left-nav-btn" on:click={cycleTheme}>
    <span class="left-nav-icon">...</span>
    <span class="left-nav-label">Theme</span>
</button>
```

**After:**
```html
<!-- <button class="left-nav-btn" on:click={cycleTheme}>
    <span class="left-nav-icon">...</span>
    <span class="left-nav-label">Theme</span>
</button> -->
```

No other files were changed. The `cycleTheme` import in the `<script>` block remains intact so the feature can be easily re-enabled later by uncommenting the button.

---
---

# Changelog — Fix Post Images Not Displaying

**Date:** March 15, 2026  
**Author:** AI-assisted development  
**Summary:** Uploaded post images were not displaying in the Profile posts grid (or anywhere else) because Django was not serving media files. The `DEBUG` setting defaults to `False`, which causes `django.conf.urls.static.static()` to return an empty list — meaning no URL route was registered for `/media/...` paths. A single file was modified to fix this.

---

## Problem

When a user created a post with an image via the "Plant a Post" carousel on `Profile.svelte`, the image was successfully uploaded to Django and saved to the `media/post_images/` directory. The backend correctly returned the image URL (e.g., `/media/post_images/filename.jpg`) in the `_post_to_dict()` response. However, when the Svelte frontend rendered `<img src="/media/post_images/filename.jpg">`, the request returned a **404 Not Found**.

**Root cause:** In `treestagram/settings.py`, the `DEBUG` setting defaults to `False`:

```python
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
```

The old `urls.py` relied on `static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)` to serve media files, but this Django helper **returns an empty list when `DEBUG = False`**. As a result, no URL pattern was registered for `/media/...`, and Django had no way to serve uploaded images.

The Vite dev server proxy (`/media` → `http://127.0.0.1:8000`) was correctly configured, but Django itself was returning 404 for all media requests.

---

## Files Changed

### 1. `treestagram/urls.py` (Backend — URL Routing)

**What changed:**
- Added import: `from django.views.static import serve as static_serve`
- Replaced the conditional `static()` helper with an explicit `re_path` that always serves media files regardless of the `DEBUG` setting
- Removed the now-unnecessary `+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)` at the end of `urlpatterns`

**Before:**
```python
from django.conf.urls.static import static

urlpatterns = [
    ...
    re_path(r'^(?!api/|admin/|accounts/|media/).*$', TemplateView.as_view(template_name='index.html')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

**After:**
```python
from django.conf.urls.static import static
from django.views.static import serve as static_serve

urlpatterns = [
    ...
    # Serve uploaded media files (images etc.) — works regardless of DEBUG setting
    re_path(r'^media/(?P<path>.*)$', static_serve, {'document_root': settings.MEDIA_ROOT}),
    # Catch-all — serve Svelte SPA (must be last!)
    re_path(r'^(?!api/|admin/|accounts/|media/).*$', TemplateView.as_view(template_name='index.html')),
]
```

The new `re_path` uses Django's built-in `django.views.static.serve` view directly, which serves files from `MEDIA_ROOT` for any request matching `/media/<path>`. This works in both development (`DEBUG=False` default) and production (when S3 is not configured).

---

## Verification

After the fix, restarting the Django server and creating a post with an image via "Plant a Post" now correctly displays the uploaded image in the Profile posts grid, the post detail modal, and the Home feed.
