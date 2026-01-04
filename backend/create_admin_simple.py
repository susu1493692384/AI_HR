"""Direct SQL script to create admin"""
import asyncio
import uuid
from datetime import datetime
from asyncpg import connect

async def create_admin():
    conn = await connect(
        "postgresql://postgres:password@localhost:5432/ai_hr"
    )

    try:
        # Check if admin exists
        row = await conn.fetchrow(
            "SELECT id, username FROM users WHERE username = $1", "admin"
        )

        if row:
            print(f"[OK] Admin already exists: {row['username']}")
            print("Password: admin123456 (default)")
            return

        # Create admin with UUID
        admin_id = uuid.uuid4()
        hashed_pw = "ac0e7d037817094e9e0b4441f9bae3209d67b02fa484917065f71b16109a1a78"  # admin123456
        now = datetime.utcnow()

        await conn.execute("""
            INSERT INTO users (id, username, email, password_hash, role, is_active, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """, admin_id, "admin", "admin@ai-hr.com", hashed_pw, "admin", True, now, now)

        print("[OK] Admin created successfully!")
        print("=" * 40)
        print("Username: admin")
        print("Email: admin@ai-hr.com")
        print("Password: admin123456")
        print("=" * 40)

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(create_admin())
