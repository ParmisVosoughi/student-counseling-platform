STUDENT COUNSELING PLATFORM - EASY VERSION
==========================================

You do NOT need to create a .env file.
You do NOT need to run migrations manually.
You do NOT need to run seed_demo manually.
You do NOT need port 8000 to be free.

FIRST RUN
---------
1) Install Docker Desktop for Windows.
2) Open Docker Desktop and wait until it is running.
3) Double-click START.bat.
4) Wait. The first build can take several minutes.
5) Your browser opens automatically.

LOGIN
-----
Admin:
  username: admin
  password: Admin123!

Supervisor:
  username: supervisor1
  password: Supervisor123!

Advisor:
  username: advisor1
  password: Advisor123!

STOP
----
Double-click STOP.bat.
Your database is preserved.

RESET EVERYTHING
----------------
Double-click RESET-ALL-DATA.bat and type DELETE.
Then run START.bat again.

NOTES
-----
- The app uses a free local port starting from 18088 automatically.
- Backend is not exposed on port 8000, so an existing program on port 8000 will not conflict.
- API, Swagger and Django Admin are reached through the same application address.
