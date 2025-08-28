# Aplikasi Kasir

Aplikasi kasir berbasis Kivy untuk Android.

## Fitur
- Interface kasir yang user-friendly
- Manajemen produk dan transaksi
- Export data ke JSON
- Support pembayaran multiple

## Build APK

### Otomatis dengan GitHub Actions
1. Push kode ke GitHub repository
2. GitHub Actions akan otomatis build APK
3. Download APK dari tab "Actions" > "Artifacts"

### Manual dengan Buildozer
```bash
buildozer android debug
```

## Requirements
- Python 3.9+
- Kivy 2.1.0+
- Buildozer

## Struktur File
- `main.py` - Aplikasi utama
- `buildozer.spec` - Konfigurasi build Android
- `requirements.txt` - Dependencies Python
- `.github/workflows/build-apk.yml` - GitHub Actions untuk auto-build
