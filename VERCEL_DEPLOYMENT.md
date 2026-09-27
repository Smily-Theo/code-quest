# CodeQuest Vercel Deployment

1. Upload this `codequest` folder to GitHub.
2. Open https://vercel.com/ and sign in with GitHub.
3. **Add New → Project → Import** the CodeQuest repository.
4. Let Vercel detect the Flask/Python application.
5. Deploy.
6. In **Project → Settings → Environment Variables**, add:
   - `SECRET_KEY` — a long random production secret
   - `OPENAI_API_KEY` — optional, for the real AI Tutor
   - `OPENAI_MODEL` — optional, e.g. `gpt-4.1-mini`
   - `DATABASE_URL` — recommended PostgreSQL connection string for persistent data
7. Redeploy after adding variables.
8. Test `/` and `/health`.

Important: do not rely on SQLite for persistent production data on Vercel. Use an external PostgreSQL database for accounts, XP, badges and leaderboard data.

The browser Python editor uses a curated evaluator and does not execute arbitrary Python on the server.
