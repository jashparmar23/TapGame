[app]
title = Tap Ball Game
package.name = tapballgame
package.domain = com.tapballgame
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt
version = 1.0
requirements = python3==3.10.12,kivy
orientation = portrait
fullscreen = 1
android.permissions = VIBRATE
android.archs = arm64-v8a, armeabi-v7a
android.api = 33
android.minapi = 21
android.ndk_path = /home/parmar/.buildozer/android/platform/android-ndk-r25b
android.ndk = 25b
android.private_storage = True

# Force SDK path so Buildozer knows where sdkmanager is
android.sdk_path = /home/parmar/.buildozer/android/platform/android-sdk

# Force Java 17 (needed for sdkmanager + API 33+)
android.javac_path = /usr/lib/jvm/java-17-openjdk-amd64/bin/javac
android.java_path = /usr/lib/jvm/java-17-openjdk-amd64/bin/java


[buildozer]
log_level = 2
warn_on_root = 1
