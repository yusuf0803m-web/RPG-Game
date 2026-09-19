"""Antarmuka web (Flask + HTML/JS) di atas mesin permainan yang sama dengan terminal.

Arsitektur: satu ``WebSession`` per permainan menjalankan ``Game.run()`` di thread
sendiri dengan ``WebIO``: setiap ``ask()`` memblokir sampai klien mengirim jawaban
lewat ``POST /api/session/<id>/input``; setiap ``line()``/``emit()`` ditumpuk sebagai
event yang diambil klien lewat ``GET /api/session/<id>/state?since=N`` (long-poll).
"""
