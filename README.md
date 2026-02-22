## Deployment & Infrastructure

### Domain
- **Domain Name:** anthonyfrial.dev
- **Registrar:** NameCheap

The domain is configured to point to the Render web service using DNS A records.

---

### Hosting Provider
- **Platform:** Render
- **Service Type:** Free Tier

Render automatically redeploys the application whenever new commits are pushed to the connected GitHub repository.

---

### Tech Stack
- **Backend:** Flask (Python), HTML, Embedded CSS
- **Frontend:** Jinja2 templates, HTML, Embedded CSS
- **Database:** PostgreSQL, psycopg2
- **Version Control:** Git, GitHub

---

### Database
- **Type:** PostgreSQL
- **Hosting:** Render Managed PostgreSQL Database

The application connects to the database using a secure `DATABASE_URL` environment variable provided by Render.

---

## Deployment Process

### Initial Deployment

1. Push the project to GitHub.
2. Create a new Web Service in Render.
3. Connect the GitHub repository.
4. Set the Start Command:
5. Configure required environment variables.
6. Render builds and deploys automatically.

---

### Updating the Application

1. Make changes locally.
2. Commit changes:
3. Push to GitHub:
4. Render automatically detects the push and redeploys the application.

No manual server access is required.

---

## Configuration & Secrets Management

Sensitive values are managed using environment variables in Render.

### Environment Variables Used

- `DATABASE_URL` – PostgreSQL connection string
- `SECRET_KEY` – Flask session security
- `PORT` – Provided automatically by Render

Environment variables:

- Are configured in the Render dashboard
- Are NOT committed to source control
- Are accessed in code using:

```python
import os
DATABASE_URL = os.environ.get("DATABASE_URL")
