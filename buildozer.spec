[app]

# ── የአፑ ስም እና መለያ (App Identity) ──────────────────────
# ስልኩ ላይ የሚታየው ስም
title = Jebena

# የአፑ መጠሪያ (ያለ ክፍተት በትንሽ ፊደል)
package.name = jebenasered

# የአፑ መለያ (Domain)
package.domain = org.jebena

# የአፑ ስሪት
version = 1.0

# ── ፋይሎች እና ፎልደሮች (Source Code & Files) ──────────────
source.dir = .

# በአፑ ውስጥ እንዲካተቱ የምትፈልጋቸው የፋይል አይነቶች
source.include_exts = py, png, jpg, jpeg, kv, db, ttf

# የግድ መካተት ያለባቸው ዋና ዋና ፋይሎች
source.include_patterns = logo.png, background.jpg, jebena.db

# ── የሚያስፈልጉ ላይብረሪዎች (Requirements) ─────────────────
# Kivy እና KivyMD ስለምትጠቀም እነዚህ ወሳኝ ናቸው
requirements = python3, kivy==2.3.0, kivymd==1.2.0, pillow

# ── የአፑ ገጽታ (Display Settings) ─────────────────────────
# አፑ ሁልጊዜ ቀጥ ብሎ እንዲከፈት (Portrait)
orientation = portrait
fullscreen = 0

# ── ምስሎች (Icons & Presplash) ────────────────────────────
# የአፑ አይኮን (logo.png መሆኑን አረጋግጥ)
icon.filename = logo.png

# አፑ ሲከፈት መጀመሪያ የሚመጣው ምስል (Loading screen)
presplash.filename = background.jpg

# ── የአንድሮይድ ቅንብሮች (Android Configuration) ────────────
android.minapi = 21
android.api = 33
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True
android.arch = arm64-v8a
android.allow_backup = True

# ── ፍቃዶች (Permissions) ──────────────────────────────────
# ዳታቤዝ ለመጠቀምና ፋይል ለማንበብ የሚያስፈልጉ ፍቃዶች
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

[buildozer]
# ስህተቶችን በዝርዝር ለማየት
log_level = 2
warn_on_root = 1
