# KaliGPT Full — HackerX v1.3

![KaliGPT Banner](https://img.shields.io/badge/KaliGPT-v1.3-0078D4?style=for-the-badge&logo=hackthebox&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-blue.svg?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Termux-4DC20F?style=for-the-badge&logo=linux&logoColor=white)

> **KaliGPT** — Agentic AI Assistant untuk Linux CLI, dirancang untuk membantu proses **Ethical Hacking & Cybersecurity**.

---

## 📖 Tentang KaliGPT

KaliGPT (codename: **HackerX**) adalah asisten AI agentic yang dikonstruksi khusus untuk ekosistem Linux. Ia menyediakan:

- **Multi-provider AI**: Gemini, OpenRouter, OpenAI (ChatGPT), LiteLLM, Ollama
- **Tool Calling**: Pencarian online, OpenSearchAPI, web launcher
- **CLI Interaktif**: Antarmuka baris perintah yang kaya fitur
- **Manajemen Model**: Ganti model, list provider, reset default secara dinamis
- **Automated Installer**: Script `install.sh` & `kaligptinstaller.sh` untuk deploy cepat

Dibangun untuk **Ethical Hacking**, **Pentest**, dan **Cybersecurity** dengan etika yang ketat.

---

## 🛠 Persyaratan Sistem

| Komponen | Minimum | Disarankan |
|----------|---------|------------|
| **OS** | Linux (Ubuntu 20.04+, Debian 10+, Kali Linux) | Kali Linux 2024.x / Ubuntu 22.04 |
| **Python** | 3.10 | 3.11+ |
| **RAM** | 2 GB | 4 GB+ |
| **Disk** | 500 MB kosong | 1 GB+ |
| **Akses Jaringan** | Internet untuk AI backend | Proxy/VPN untuk riset aman |
| **Termux (Opsional)** | Android 7.0+ | Android 10+ |

> ⚠️ **PENTING**: Jangan pernah menjalankan KaliGPT sebagai `root` di Termux atau environment umum. Gunakan user biasa dan aktifkan fitur yang sesuai dengan izin yang Anda miliki.

---

## 🚀 Cara Deploy (Instalasi)

Ada 3 metode instalasi, pilih yang sesuai dengan kebutuhan Anda:

### ⚡ Metode 1: Instalasi Otomatis (Disarankan)

```bash
# 1. Clone repo ini
git clone https://github.com/vanderstark/kaligpt-full.git
cd kaligpt-full

# 2. Jalankan script installer
bash install.sh
# atau
sudo bash kaligptinstaller.sh
```

Script ini akan:
- ✅ Menginstall dependencies (`pip install -r requirements.txt`)
- ✅ Menyiapkan konfigurasi API key (`~/.config/kaligpt/keys.env`)
- ✅ Membuat shortcut CLI `kaligpt` di `/usr/local/bin/`
- ✅ Menyiapkan completion bash/zsh

---

### 🐍 Metode 2: Pip Manual

```bash
# 1. Clone repo
git clone https://github.com/vanderstark/kaligpt-full.git
cd kaligpt-full

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Jalankan installer interaktif
bash installer.sh
# atau edit manual: nano ~/.config/kaligpt/keys.env
```

---

### 📱 Metode 3: Termux (Android)

```bash
# 1. Install dependencies di Termux
pkg update && pkg upgrade -y
pkg install python -y
pip install -r requirements.txt

# 2. Clone repo
git clone https://github.com/vanderstark/kaligpt-full.git ~/.kaligpt
cd ~/.kaligpt

# 3. Jalankan
bash kaligptinstaller.sh
```

> 📝 **Catatan Termux**: Pastikan Anda memiliki akses storage (`termux-setup-storage`) jika butuh baca/tulis file di direktori lokal.

---

## 🔑 Setup API Key

KaliGPT mendukung beberapa provider AI. Setiap provider butuh kunci akses.

### 1. Jalankan Interaktif (Termahal):

```bash
bash installer.sh
```
Akan meminta Anda memasukkan kunci dan menyimpannya ke `~/.config/kaligpt/keys.env`.

### 2. Manual Edit:

```bash
nano ~/.config/kaligpt/keys.env
```

Format file `keys.env`:
```ini
# Gemini API (Gratis dengan daftar Google AI Studio)
GEMINI_API_KEY="AIza..."

# OpenRouter API
OPENROUTER_API_KEY="sk-or-..."

# OpenAI/ChatGPT
OPENAI_API_KEY="sk-..."

# LiteLLM ( wrapper multi-provider )
LITELLM_API_KEY="sk-..."
```

### 3. Daftar Provider & Contoh Kunci:

| Provider | Cara Dapatkan | Catatan |
|----------|---------------|---------|
| **Gemini** | [Google AI Studio](https://aistudio.google.com/) | Gratis, limit harian terbilang |
| **OpenRouter** | [openrouter.ai](https://openrouter.ai/) | Berganti model murah |
| **OpenAI** | [platform.openai.com](https://platform.openai.com/) | Berbayar (berdasarkan usage) |
| **LiteLLM** | Install sendiri atau pakai hosted | Wrapper multi-model |

---

## 💬 Cara Pakai (Usage)

Setelah instalasi dan setup API key selesai, KaliGPT siap digunakan.

### 📦 Cek Versi & Bantuan

```bash
# Cek versi terinstall
kaligpt -v

# Lihat manual pengguna
kaligpt -h
```

### 🤖 Mode Penggunaan

KaliGPT menawarkan beberapa cara berinteraksi:

#### 1. **Prompt Interaktif (Default)**

```bash
kaligpt
```
Akan memulai sesi chat interaktif di terminal. Ketik `/help` di dalam sesi untuk daftar perintah.

#### 2. **Direct Prompt (Satu Klik)**

```bash
# Tanya topik umum
kaligpt "Help me find XSS vulnerabilities on example.com"

# Tanyakan tentang tool tertentu
kaligpt "Scan this URL for security issues: https://example.com"

# Tulis prompt dalam tanda kutip ganda atau satu
```

#### 3. **Mode Spesifik Provider**

Gunakan flag `-g`, `-o`, `-or`, `-c`, `-ll` untuk memaksa provider tertentu:

```bash
# Gunakan Gemini
kaligpt -g "Analisis kode ini untuk bug: ..."

# Gunakan OpenRouter
kaligpt -or "Review kode Python ini..."

# Gunakan OpenAI ChatGPT
kaligpt -c "Tolong debug script ini..."

# Gunakan LiteLLM
kaligpt -ll "Buatkan laporan keamanan dari hasil scan"
```

#### 4. **Command Mode (CLI Utuh)**

```bash
# Lihat semua opsi
kaligpt --help
```

---

## 🧩 Manajemen Model

Di dalam mode interaktif (`kaligpt`), Anda bisa mengontrol model yang digunakan dengan perintah khusus:

| Perintah | Fungsi |
|----------|--------|
| `/set-model gemini-1.5-pro` | Ganti model Gemini |
| `/set-model openrouter/claude-3-opus` | Ganti model via OpenRouter |
| `/list-models` | Daftar model yang tersedia |
| `/reset-default` | Kembalikan ke model default |
| `/exit` / `/quit` | Keluar dari mode interaktif |

Contoh:
```bash
kaligpt
# Di dalam sesi chat:
/set-model gemini-1.5-flash
>>> Mode diganti ke gemini-1.5-flash
```

---

## 🛠 Troubleshooting (Masalah Umum)

### ❌ Masalah: `command not found: kaligpt`

**Solusi:**
```bash
# Pastikan installer jalan dengan benar
sudo bash kaligptinstaller.sh

# Atau tambahkan manually ke PATH
echo 'export PATH="$HOME/.kaligpt:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

### ❌ Masalah: `Invalid API key` / `Authentication Error`

**Solusi:**
```bash
# Hapus kun kunci lama
rm -f ~/.config/kaligpt/keys.env

# Jalankan ulang installer
bash installer.sh

# Pastikan koneksi internet aktif (cek dengan: ping google.com)
```

---

### ❌ Masalah: `ModuleNotFoundError: No module named 'X'`

**Solusi:**
```bash
pip3 install -r requirements.txt --upgrade
# atau
pip install -r requirements.txt --user
```

---

### ❌ Masalah: Kendala di Termux

**Solusi:**
```bash
# Pastikan python dan pip terinstall dengan benar
python --version
pip --version

# Install ulang requirements
pip install -r requirements.txt -r

# Jika error di build tools:
pkg install build-essential -y
```

---

### ❌ Masalah: `Permission denied` saat menjalankan script

**Solusi:**
```bash
chmod +x install.sh kaligptinstaller.sh
bash install.sh
# atau
sudo bash kaligptinstaller.sh
```

---

## ⚖️ Disclaimer & Etika

> **⚠️ PENTING BACA SEBELUM MENGGUNAKAN**

Dengan mengunduh atau menggunakan source code ini, Anda menyetujuh dengan ketentuan di bawah ini:

1. **HANYA untuk Ethical Hacking** — Gunakan hanya pada sistem yang Anda miliki atau memiliki izin tertulis untuk diuji penetrasi.

2. **Pentest for good** — Alat ini dibuat untuk meningkatkan keamanan sistem, bukan untuk merusak atau mencuri data.

3. **Bukan untuk cybercrime** — Penyalahgunaan untuk akses tidak otoritas, pencurian data, atau aktivitas ilegal melanggar hukum dan akan ditanggung jawab pengguna.

4. **Patuhi hukum lokal** — Akses sistem tanpa izin adalah tindak pidana (Criminal Code/IT Law). Penulis tidak bertanggung jawab atas penggunaan salah.

5. **Alat bantu, bukan pengganti profesional** — KaliGPT adalah asisten AI. Selalu verifikasi hasil dan gunakan tools resmi untuk pentest serius.

> *"Pentest for good instead." — Gunakan bijak dan bertanggung jawab.*

---

## 🔗 Referensi & Sumber Daya

| Sumber | Link |
|--------|------|
| **Repo Resmi KaliGPT** | https://github.com/SudoHopeX/KaliGPT |
| **Branch HackerX** | https://github.com/SudoHopeX/KaliGPT/tree/hackerx |
| **Dokumentasi Lengkap** | https://hope.is-a.dev/?path=kaligpt |
| **Issues & Discussions** | https://github.com/SudoHopeX/KaliGPT/issues |
| **Author / Pembuat** | SudoHopeX \| Krishna Dwivedi |
| **License** | MIT (lihat file `LICENSE` di repo ini) |
| **Google AI Studio (Gemini)** | https://aistudio.google.com/ |
| **OpenRouter** | https://openrouter.ai/ |
| **Termux Official** | https://termux.app/ |

---

## 📦 Isi Repo (Ringkas)

```
kaligpt-full/
├── agents/               # Modul AI provider (Gemini, OpenRouter, dll.)
├── install.sh            # Script installer utama
├── kaligptinstaller.sh   # Installer alternatif
├── requirements/         # File persyaratan (pip-requirements.txt, globals.md)
├── installers/           # Script platform (arch, deb, termux)
├── agents/utils/         # Utilitas bantu (tools, configs, prompts)
├── .github/              # Workflow CI/CD (opsional)
├── LICENSE              # MIT License
├── README.md            # Dokumentasi ini (Anda sedang di sini)
├── DISCLAIMER           # Disclaimer etika
├── SECURITY.md          # Pedoman keamanan penggunaan
└── CONTRIBUTING.md      # Panduan kontributor
```

---

## 🛠 Development (Untuk Developer)

Jika ingin berkontribusi atau mengembangkan KaliGPT:

```bash
# 1. Fork repo ini
# 2. Clone ke mesin lokal
git clone https://github.com/<username>/kaligpt-full.git
cd kaligpt-full

# 3. Buat branch baru
git checkout -b fitur-baru

# 4. Lakukan perubahan, commit
git commit -m "Menambahkan: fitur baru"

# 5. Push ke branch Anda
git push origin fitur-baru

# 6. Buat Pull Request ke repo utama
```

Lihat file `CONTRIBUTING.md` dan `DEVELOPER.md` untuk panduan lengkap.

---

<div align="center">

**[⬆ Kembali ke Atas](#-kaligpt-full-hackerx-v13)**

Made with ❤️ for the Ethical Hacking Community

</div>

---