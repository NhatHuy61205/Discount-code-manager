import hashlib
import re

from app import app, db
from app.models import User

# Regex nhận diện chuỗi MD5 32 ký tự hex
MD5_PATTERN = re.compile(r"^[a-fA-F0-9]{32}$")


def is_md5_hash(value: str) -> bool:
    return bool(value and MD5_PATTERN.fullmatch(value))


def md5_hash(password: str) -> str:
    return hashlib.md5(password.encode("utf-8")).hexdigest()


def migrate_all_passwords():
    with app.app_context():
        users = User.query.all()

        if not users:
            print("Không có user nào trong database.")
            return

        updated_count = 0
        skipped_count = 0

        for user in users:
            current_password = user.password or ""

            # Nếu đã là MD5 rồi thì bỏ qua để tránh băm 2 lần
            if is_md5_hash(current_password):
                skipped_count += 1
                print(f"[BỎ QUA] User: {user.username} đã có mật khẩu dạng MD5")
                continue

            old_password = current_password
            new_password = md5_hash(old_password)

            user.password = new_password
            updated_count += 1
            print(f"[CẬP NHẬT] User: {user.username} | '{old_password}' -> '{new_password}'")

        db.session.commit()

        print("\n=== HOÀN TẤT ===")
        print(f"Số user đã cập nhật: {updated_count}")
        print(f"Số user bỏ qua: {skipped_count}")


if __name__ == "__main__":
    migrate_all_passwords()