from passlib.context import CryptContext

# Use a safe, pure-python hashing algorithm for local development to avoid
# native bcrypt compatibility issues on some Windows environments. For
# production, consider switching back to bcrypt.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
