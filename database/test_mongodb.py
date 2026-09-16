from database.mongodb import test_connection


print("=" * 50)
print("Testing MongoDB Atlas connection...")
print("=" * 50)


if test_connection():
    print("✅ MongoDB Atlas connection successful!")
else:
    print("❌ MongoDB Atlas connection failed.")