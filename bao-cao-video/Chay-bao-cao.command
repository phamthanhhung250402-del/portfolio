#!/bin/bash
# =============================================================
#  BẤM ĐÚP FILE NÀY ĐỂ CHẠY BÁO CÁO
#  Lần đầu: tự cài thư viện (cần internet, 1-2 phút).
# =============================================================
cd "$(dirname "$0")" || exit 1

dung_lai() {
  echo
  read -n 1 -s -r -p "Bấm phím bất kỳ để đóng cửa sổ này..."
  echo
  exit "${1:-0}"
}

echo "=================================================="
echo "  BÁO CÁO VIDEO & ĐỀ XUẤT MIX NỘI DUNG"
echo "=================================================="

# 0) File này phải nằm cùng thư mục với các file khác của công cụ
if [ ! -d "baocao" ] || [ ! -f "requirements.txt" ] || [ ! -d "config" ]; then
  echo "Thiếu file của công cụ trong thư mục:"
  echo "  $(pwd)"
  echo
  echo "File .command này chỉ là nút bấm. Nó phải nằm chung thư mục với"
  echo "baocao/, config/, mau/, requirements.txt... (toàn bộ nội dung thư mục bao-cao-video)."
  echo "Hãy chép CẢ thư mục bao-cao-video (không chỉ riêng file .command) rồi bấm đúp"
  echo "file Chay-bao-cao.command nằm bên trong thư mục đó."
  dung_lai 1
fi

# 1) Tìm Python 3 (có sẵn trên Mac)
PY=""
for p in python3 /usr/bin/python3 /opt/homebrew/bin/python3 /usr/local/bin/python3; do
  if command -v "$p" >/dev/null 2>&1 && "$p" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' >/dev/null 2>&1; then
    PY="$p"; break
  fi
done
if [ -z "$PY" ]; then
  echo "Máy chưa có Python 3."
  echo "Một hộp thoại 'Công cụ dòng lệnh' (Command Line Tools) sẽ hiện ra: bấm Cài đặt,"
  echo "đợi cài xong (5-10 phút) rồi bấm đúp lại file này."
  xcode-select --install >/dev/null 2>&1
  dung_lai 1
fi

# 2) Môi trường riêng (.venv) + thư viện, chỉ cài lần đầu hoặc khi requirements.txt đổi
VENV=".venv"
if [ ! -x "$VENV/bin/python" ]; then
  echo "Lần đầu chạy: đang chuẩn bị môi trường..."
  "$PY" -m venv "$VENV" || { echo "Không tạo được môi trường Python."; dung_lai 1; }
fi
REQ=$(shasum requirements.txt | cut -d' ' -f1)
[ -n "$REQ" ] || { echo "Không đọc được requirements.txt."; dung_lai 1; }
if [ "$(cat "$VENV/.da-cai" 2>/dev/null)" != "$REQ" ]; then
  echo "Đang cài thư viện (cần internet)..."
  "$VENV/bin/python" -m pip install -q --disable-pip-version-check --upgrade pip >/dev/null 2>&1
  if ! "$VENV/bin/python" -m pip install -q --disable-pip-version-check -r requirements.txt; then
    echo "Cài thư viện bị lỗi. Kiểm tra kết nối internet rồi bấm đúp lại file này."
    dung_lai 1
  fi
  echo "$REQ" > "$VENV/.da-cai"
fi

# 3) Chạy
"$VENV/bin/python" -m baocao "$@"
dung_lai $?
