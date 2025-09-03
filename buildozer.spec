[app]
title = Tap Ball Game
package.name = tapballgame
package.domain = com.tapballgame
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt
version = 1.0
requirements = python3==3.11,kivy
orientation = portrait
fullscreen = 1
android.permissions = VIBRATE
android.archs = arm64-v8a, armeabi-v7a
android.api = 33
android.minapi = 21
android.ndk = 25b
android.private_storage = True

[buildozer]
log_level = 2
warn_on_root = 1
