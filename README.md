# Django Blog

Assignment milestones are documented here; application files are organized by
entity and purpose, with comments marking Task 2 additions.

## Task 2 — REST POST APIs

This update is **Task 2**: creating blog users, categories, posts, and comments
through Django REST Framework. The earlier models, admin, HTML blog page, and
`/blog/api/` examples remain available.

Task 2 uses create-only ViewSets, ModelSerializers, and database transactions.
The four endpoints accept JSON without authentication for this assignment.
This public creation policy is intended for the exercise; the older CRUD APIs
still require a Django login for writes.

| Endpoint | Required request fields |
| --- | --- |
| `POST /api/users/` | `username`, `email`, `first_name`, `last_name` |
| `POST /api/categories/` | `name`, `description` |
| `POST /api/posts/` | `title`, `content`, `author`, `category` |
| `POST /api/comments/` | `content`, `author`, `post` |

### Request examples

Create a user:

```json
{"username":"john_doe","email":"john@example.com","first_name":"john","last_name":"doe"}
```

Create a category:

```json
{"name":"Technology","description":"Articles related to technology."}
```

Create a post using IDs returned by the user and category endpoints:

```json
{"title":"Introduction to Django REST Framework","content":"Django REST Framework makes it easy to build APIs.","author":1,"category":1}
```

Create a comment using the returned user and post IDs:

```json
{"content":"Great article!","author":1,"post":1}
```

Success returns `201` with the new record and its generated ID. Invalid data
returns `400` with field-specific errors. Duplicate usernames, emails, and
category names are rejected. Relationship IDs must exist, and required fields
cannot be missing, null, or blank. Unexpected server failures return `500`;
creation transactions roll back rather than leave partial records.

The Task 2 post API accepts and returns singular `category`, as specified in the
assignment. It stores that category in the existing many-to-many `categories`
relationship. Earlier APIs continue using the plural `categories` array.

Blog users are author profiles, separate from Django authentication accounts.
The assignment's user payload contains no password: this API does not create a
login, accept a password field, or return passwords. Use `createsuperuser` for
Django admin login accounts; Django handles their password hashing.

### Run locally (PowerShell)

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` with your own secret key and PostgreSQL connection settings.
Use an existing database and schema (`public` is the example default).
Do not overwrite an existing configured `.env` when following these steps.

```powershell
python manage.py migrate
$env:DEBUG = 'True'
python manage.py runserver 127.0.0.1:8001
```

Send JSON with `Content-Type: application/json` to the endpoints above using
Postman or another HTTP client. These endpoints only implement POST; opening
them directly in a browser sends GET and returns `405 Method Not Allowed`.

### Verification

```powershell
python manage.py makemigrations --check --dry-run
$env:DATABASE_SCHEMA = 'public'
python manage.py test blog --keepdb
Remove-Item Env:DATABASE_SCHEMA
```

The test database needs a schema that exists in a newly created database and
the database role needs permission to create a test database. The `public`
override is for tests only. Tests do not insert sample data into the application
database. Task 2 adds no model changes or migrations.

`.env`, virtual environments, caches, and local SQLite files are excluded by
`.gitignore`. `.env.example`, source code, tests, and migrations belong in Git.

## Task 2 verification and scope note

## Verification completed

- All 29 automated tests passed when Task 2 was implemented. These cover the
  four exact endpoints, required fields, duplicates, email validation,
  relationship IDs, saved records, and rollback on a simulated server error.
- Manual browser tests returned HTTP 201 for all four creation endpoints.
- Manual duplicate-user tests returned HTTP 400 for username and email.
- Manual duplicate-category testing returned HTTP 400 for the category name.
- A manual comment request referencing post ID 999999 returned HTTP 400.

Required-field checks are covered by automated tests; a separate manual
required-field test was suggested but has not been confirmed in the session.

## Intended behavior and scope

- Repeated post or comment content is allowed. Duplicate authors or category
  assignments across different posts are also allowed. Each record gets its own ID.
- User first/last names and category descriptions may repeat; only usernames,
  emails, and category names have uniqueness constraints.
- These endpoints create blog author profiles, not Django authentication accounts.
  Passwords are not accepted or returned by these APIs. Django authentication
  accounts remain separate and use Django's password hashing.
- Task 2 provides POST creation, not GET lists or update/delete routes at `/api/`.
  GET on a Task 2 endpoint correctly returns HTTP 405. Earlier `/blog/api/` CRUD
  endpoints remain available with their existing permissions.
- Creation is public for this assignment; account ownership and production
  authentication policies are outside this task's scope.
- No model schema changes or new migrations were needed for Task 2.
- PostgreSQL stores API-created records locally. GitHub contains source code,
  tests, documentation, migrations, and `.env.example`; it does not contain the
  application database, real `.env` credentials, or virtual environments.


### Code organization

Serializers and views live in entity-named modules (`user.py`, `post.py`,
`category.py`, `comment.py`). Shared creation behavior is in `views/base.py`.
All blog routes are defined in `blog/urls.py`; `config/urls.py` mounts them.
Creation tests are in `blog/test_api.py`. Comments mark the Task 2 additions.
