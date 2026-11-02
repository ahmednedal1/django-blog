# Django Blog

See [Task 2 completion and verification note](TASK_2.md) for what was
implemented, what was tested, and the intended scope of this assignment.

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
