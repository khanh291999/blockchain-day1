## Thành viên nhóm

| Họ và tên | MSSV |
|-----------|------|
| Đỗ Quốc Khánh | 2591307 |
| Nguyễn Thành Quí | 2591320 |
| Trần Thị Bảo My | 2591314 |

# 🔗 Blockchain Demo - Web Application

## 📖 Giới thiệu

Đây là một ứng dụng web blockchain đầy đủ tính năng, được xây dựng bằng Python Flask với giao diện người dùng hiện đại. Ứng dụng minh họa các khái niệm cốt lõi của blockchain bao gồm:

- **Proof-of-Work (PoW)** - Cơ chế đồng thuận Bitcoin
- **Hash Algorithms** - 5 thuật toán mã hóa khác nhau
- **Chain Validation** - Phát hiện giả mạo tự động
- **Tampering Detection** - Demo bảo mật blockchain

## ✨ Tính năng chính

### 🔗 Tab 1: Blockchain Management

- **Tạo Blockchain** với tùy chọn:
  - 5 thuật toán hash: SHA-256, SHA-512, SHA3-256, SHA3-512, BLAKE2b
  - 4 mức độ khó: 2 (Dễ), 3 (Trung bình), 4 (Khó), 5 (Rất khó)
  
- **Thêm Blocks** với Proof-of-Work mining
  - Hiển thị thời gian mining và nonce
  - Visualize blockchain với từng block
  
- **Validate Chain** - Kiểm tra tính toàn vẹn
  - Verify hash integrity
  - Verify chain links
  - Verify PoW difficulty
  
- **Save/Load History** - Lưu và khôi phục blockchain
  - Lưu blockchain vào file JSON
  - Load lại blockchain đã lưu
  - Quản lý nhiều blockchain khác nhau
  
- **Demo Tampering** - Chứng minh bảo mật
  - Thay đổi dữ liệu block cũ
  - Phát hiện giả mạo tự động
  - Hiển thị chain bị broken

### 📊 Tab 2: Hash Algorithm Comparison

- **So sánh Hiệu suất Mining**
  - Chọn độ khó để test (2, 3, 4, 5)
  - Vẽ bar chart so sánh thời gian mining
  - Hiển thị nonce và hash cho từng thuật toán
  
- **Test Collision Resistance**
  - Demo avalanche effect
  - So sánh hash của "Hello World" vs "Hello World!"
  - Chứng minh tính bảo mật của hash function
  
- **Thông tin Algorithms**
  - Giải thích chi tiết từng thuật toán
  - Ứng dụng thực tế (Bitcoin, Ethereum, ...)
  - So sánh độ dài hash và bảo mật

## 🚀 Hướng dẫn cài đặt và chạy

### Bước 1: Cài đặt Python

Đảm bảo bạn đã cài đặt Python 3.12 hoặc cao hơn.

```bash
python --version
```

### Bước 2: Tạo Virtual Environment

```powershell
# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Hoặc (Windows CMD)
venv\Scripts\activate.bat
```

### Bước 3: Cài đặt Dependencies

```powershell
pip install -r requirements.txt
```

### Bước 4: Chạy ứng dụng

```powershell
python app.py
```

### Bước 5: Truy cập ứng dụng

Mở trình duyệt và truy cập:

```
http://localhost:5000
```

Bạn sẽ thấy giao diện web với 2 tabs:
- **Blockchain** - Quản lý blockchain
- **So sánh Hash Algorithms** - So sánh các thuật toán

---

## 📂 Cấu trúc dự án

```
code/
├── app.py                      # Flask web application (main)
├── blockchain.py               # Core blockchain implementation
├── test_blockchain.py          # Unit tests
├── requirements.txt            # Python dependencies
├── templates/
│   └── index.html             # Web UI với 2 tabs
├── blockchain_history/         # Saved blockchains (JSON)
└── venv/                      # Virtual environment
```

## 🧪 Chạy Unit Tests

```powershell
python -m pytest test_blockchain.py -v
```

Hoặc:

```powershell
python test_blockchain.py
```

## 🎯 Kiến thức được minh họa

### 1. Blockchain Fundamentals

- **Distributed Ledger**: Cấu trúc dữ liệu phân tán, không thể thay đổi
- **Cryptographic Hash**: Sử dụng SHA-256 để bảo mật và định danh blocks
- **Chain Linking**: Mỗi block liên kết với block trước qua `previous_hash`
- **Immutability**: Thay đổi 1 block → phá vỡ toàn bộ chain

### 2. Proof-of-Work (PoW)

- **Mining Process**: Tìm nonce sao cho hash bắt đầu với n số 0
- **Difficulty**: Số lượng số 0 đầu tiên trong hash (2-5)
- **Computational Cost**: Đảm bảo bảo mật qua chi phí tính toán
- **Bitcoin**: Sử dụng PoW với difficulty tự động điều chỉnh

### 3. Hash Algorithms

Ứng dụng hỗ trợ 5 thuật toán mã hóa:

| Algorithm | Bits | Ứng dụng thực tế |
|-----------|------|------------------|
| **SHA-256** | 256 | Bitcoin, SSL certificates |
| **SHA-512** | 512 | High-security applications |
| **SHA3-256** | 256 | Ethereum (Keccak), Modern crypto |
| **SHA3-512** | 512 | Strongest SHA-3 variant |
| **BLAKE2b** | 512 | Performance-critical systems |

### 4. Security Features

- **Tampering Detection**: Phát hiện tự động khi dữ liệu bị thay đổi
- **Hash Integrity**: Mỗi block có hash unique
- **Chain Validation**: Kiểm tra toàn bộ chain trong vài ms
- **Avalanche Effect**: Thay đổi 1 bit → hash hoàn toàn khác

## 🔧 Troubleshooting

### Lỗi: ModuleNotFoundError: No module named 'flask'

```powershell
# Đảm bảo virtual environment được kích hoạt
.\venv\Scripts\Activate.ps1

# Cài lại dependencies
pip install -r requirements.txt
```

### Lỗi: Port 5000 đã được sử dụng

```powershell
# Thay đổi port trong app.py
# Dòng cuối cùng: app.run(debug=True, host='0.0.0.0', port=5001)
```

### Mining quá lâu với difficulty cao

- Giảm difficulty xuống 2 hoặc 3 để test nhanh hơn
- Difficulty 5 có thể mất vài phút tùy máy

## 📚 Tài liệu tham khảo

- [Bitcoin Whitepaper](https://bitcoin.org/bitcoin.pdf) - Satoshi Nakamoto
- [SHA-256 Specification](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf) - NIST
- [Flask Documentation](https://flask.palletsprojects.com/) - Pallets Projects
- [Proof-of-Work Explained](https://www.investopedia.com/terms/p/proof-work.asp) - Investopedia

## 🎯 Tóm tắt nhanh

```bash
# Clone hoặc copy project
cd day1-code

# Tạo và kích hoạt virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy ứng dụng
python app.py

# Truy cập: http://localhost:5000
```

## 🔧 Yêu cầu hệ thống

- Python 3.6 trở lên
- Không cần thư viện bên ngoài (chỉ dùng standard library)

## 📝 Ghi chú
- Difficulty = 4-5 phù hợp cho production
- Difficulty = 2-3 tốt cho testing/demo
