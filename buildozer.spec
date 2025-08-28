[app]

# (str) Title of your application
title = Kasir App

# (str) Package name
package.name = kasirapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.kasir

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,ttf

# (str) Application versioning
version = 1.0

# (list) Application requirements
requirements = python3,kivy==2.0.0,requests,pillow,urllib3,certifi,android

# (str) Orientation
orientation = portrait

# (bool) Fullscreen
fullscreen = 0

# Android specific
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 29
android.minapi = 21
android.sdk = 29
android.ndk = 21.3.6528147
android.arch = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
