[app]

# ── App identity ───────────────────────────────────────────
title           = Jebena Sefed
package.name    = jebenaapp
package.domain  = com.jebena
version         = 1.0

# ── Source ────────────────────────────────────────────────
source.dir           = .
source.include_exts  = py,db,png,jpg,jpeg,kv,atlas,ttf
source.include_patterns = logo.png,background.jpg,jebena.db

# ── Requirements (sqlite3 is built-in — do NOT add it) ────
requirements = python3,kivy==2.2.1,kivymd==1.1.1

# ── Display ───────────────────────────────────────────────
orientation = portrait
fullscreen  = 0

# ── Icons (uses logo.png) ─────────────────────────────────
icon.filename        = %(source.dir)s/logo.png
presplash.filename   = %(source.dir)s/background.jpg

# ── Android ───────────────────────────────────────────────
android.minapi           = 21
android.api              = 33
android.ndk              = 25b
android.sdk              = 33
android.accept_sdk_license = True
android.arch             = arm64-v8a
android.allow_backup     = True

# ── Permissions ───────────────────────────────────────────
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

[buildozer]
log_level    = 2
warn_on_root = 1
