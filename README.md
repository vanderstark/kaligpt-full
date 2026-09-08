# KaliGPT Source Code — HackerX v1.3

Repo ini berisi **source code resmi KaliGPT** (codename: HackerX v1.3), sebuah _Agentic AI Assistant_ untuk Linux CLI yang dirancang untuk membantu proses **Ethical Hacking & Cybersecurity**.

Repo ini adalah **salinan (mirror)** dari repo resmi `SudoHopeX/KaliGPT` namun dikelola di bawah akun GitHub `vanderstark` untuk dokumentasi dan tujuan deploy internal.

---

## 📦 Isi Repo

Repo ini berisi seluruh source code KaliGPT, meliputi:

- **Script installer** (`install.sh`, `kaligptinstaller.sh`)
- **Modul AI Agent** — logika utama interaksi dengan backend model
- **Tool integration** — pencarian online, tool calling, OpenSearchAPI
- **CLI interface** — antarmuka baris perintah `kaligpt`
- **Konfigurasi API key** — management backend Gemini, Ollama, OpenRouter, ChatGPT, LiteLLM
- **Model management** — perubahan model, list provider, reset default
- **Documentation files** — README, LICENSE, DISCLAIMER

### Struktur Direktori Utama

```
kaligpt-source/
├── hackerx/              # Branch aktif (fitur terbaru)
│   ├── installer.sh
│   ├── kaligptinstaller.sh
│   ├── cli.py            # Interface baris perintah
│   ├── agents/           # Agentic AI logic
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── tools/            # Tool calling implementations
│   │   ├── search.py
│   │   └── opensearch.py
│   ├── backends/         # AI backend integrations
│   │   ├── gemini.py
│   │   ├── ollama.py
│   │   ├── openrouter.py
│   │   ├── chatgpt.py
│   │   └── litellm.py
│   ├── models.py         # Model management
│   └── utils.py          # Utilitas umum
├── main/                 # Branch main (stabil)
│   └── ...
├── requirements/         # File persyaratan
│   └── globals.md
├── LICENSE               # Lisensi proyek
├── README.md             # Dokumentasi proyek (asal)
├── DISCLAIMER            # Disclaimer penggunaan
└── pyproject.toml        # Konfigurasi Python project
```

---

## 🛠 Cara Menggunakan Source Code Ini

### 1. Clone Repo

```bash
git clone https://github.com/vanderstark/kaligpt-source.git
cd kaligpt-source
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
# atau
pip3 install -r requirements.txt
```

### 3. Setup API Keys

```bash
# Jalankan interaktif
bash installer.sh

# Atau manual edit file konfigurasi
nano ~/.config/kaligpt/keys.env
```

### 3. Jalankan KaliGPT

```bash
# Cek versi
kaligpt -v

# Cek bantuan
kaligpt -h

# Prompt interaktif
kaligpt

# Direct prompt
kaligpt "Help me find XSS on target.com"
```

---

## 🌿 Branch Management

Repo ini memiliki 2 branch utama:

| Branch | Deskripsi |
|--------|-----------|
| `hackerx` | Branch aktif dengan fitur terbaru (Tool calling, OpenSearchAPI, LiteLLM, dll.) |
| `main` | Branch utama stabil (versi terbit publik) |

Untuk melihat fitur terbaru, aktifkan branch `hackerx`:
```bash
git checkout hackerx
```

---

## 📄 Lisensi

Lihat file [`LICENSE`](LICENSE) untuk detail lengkap.

> **Kesimpulan:** Source code ini tunduh lisensi [`MIT License`](https://opensource.org/licenses/MIT) sebagai dokumentasi lokal. Lisensi asli di repo `SudoHopeX/KaliGPT` mungkin berbeda — silakan lihat di repo resmi.

---

## ⚖️ Disclaimer

> [!WARNING]
> **KaliGPT masih dalam tahap aktif dikembangkan.** Jangan berharap bekerja sempurna.

Penggunaan source code ini harus sesuai dengan:

1. **HANYA untuk Ethical Hacking** dengan izin tertulis dari pemilik target.
2. **Pentest for good** — digunakan untuk meningkatkan keamanan, bukan merusak.
3. **Bukan untuk cybercrime** — penyalahgunaan dapat melanggar hukum.
4. **Patuhi hukum lokal** — akses tanpa izin adalah tindak pidana.

> *Pentest for good instead.* Dengan unduh atau memodifikasi source code ini, Anda setuju bertanggung jawab atas segala konsekuensinya.

---

## 🔗 Referensi

- **Repo Resmi**: https://github.com/SudoHopeX/KaliGPT
- **Branch HackerX**: https://github.com/SudoHopeX/KaliGPT/tree/hackerx
- **Dokumentasi Lengkap**: https://hope.is-a.dev/?path=kaligpt
- **Issues**: https://github.com/SudoHopeX/KaliGPT/issues
- **Author**: SudoHopeX | Krishna Dwivedi

---

<div align="center">

**[⬆ Kembali ke Atas](#-kaligpt-source-code--hackerx-v13)**

Made with ❤️ for the Ethical Hacking Community

</div>