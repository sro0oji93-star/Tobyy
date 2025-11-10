[app]

title = Toby
package.name = toby
package.domain = org.toby

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

requirements = python3,kivy,yt_dlp

orientation = portrait

fullscreen = 0

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

[buildozer]

log_level = 2
warn_on_root = 1
