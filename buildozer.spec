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

# (str) Application versioning (method 1)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py
#
# (str) Application versioning (method 2)
version = 1.0

# (list) Application requirements
requirements = python3,kivy==2.2.1,requests,pillow,urllib3,certifi,firebase-admin,android,plyer

# (str) Custom source folders for requirements
# requirements.source.kivy = ../../kivy

# (str) Presplash of the application
presplash.filename = %(source.dir)s/presplash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# Android specific
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.ndk_path = 
android.sdk_path = 
android.arch = arm64-v8a
android.debug_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 1
