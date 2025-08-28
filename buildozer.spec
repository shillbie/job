[app]
title = Kasir App
package.name = kasirapp
package.domain = org.kasir
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf
version = 1.0
requirements = python3,kivy,requests,pillow,urllib3,certifi,firebase-admin
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,VIBRATE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.archs = arm64-v8a
android.allow_backup = True
android.accept_sdk_license = True
android.private_storage = True
android.wakelock = True
android.orientation = portrait
android.icon = icon.png
android.presplash = presplash.png
android.gradle_dependencies = 
android.add_src = 
android.add_jars = 
android.add_compile_options = 
android.manifest_placeholders = 
android.release_artifact = aab
android.debug_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 1
