[app]

# Title of your application
title = Universal File Converter

# Package name
package.name = fileconverter

# Package domain (needed for android/ios packaging)
package.domain = org.example

# Source code where the main.py lives
source.dir = .

# Source files to include
source.include_exts = py,png,jpg,kv,atlas

# Application version
version = 0.1

# Application requirements
requirements = python3,kivy,pillow,python-docx,pypdf2,pandas,moviepy,pydub

# Presplash of the application
presplash.filename = %(source.dir)s/data/presplash.png

# Icon of the application
icon.filename = %(source.dir)s/data/icon.png

# Supported orientation (landscape, portrait or all)
orientation = portrait

# Android specific
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.gradle_dependencies = com.android.support:support-v4:27.1.1
android.arch = arm64-v8a

# iOS specific
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0

[buildozer]
# Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# Whether to use color coding in the logs
color = 1

# Path to buildozer and python-for-android directories
# buildozer_dir = ./.buildozer
# p4a_dir = ./.buildozer/android/platform/python-for-android