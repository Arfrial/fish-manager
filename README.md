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
