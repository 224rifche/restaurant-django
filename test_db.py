import MySQLdb
from decouple import config

try:
    # Using the same configuration as in settings.py
    db_config = {
        'host': config('DB_HOST', 'localhost'),
        'user': config('DB_USER', 'root'),
        'password': config('DB_PASSWORD', 'che28rif62'),
        'database': config('DB_NAME', 'restaurant_db'),
        'port': int(config('DB_PORT', '3306'))
    }
    
    print("Attempting to connect with these settings:")
    print(f"Host: {db_config['host']}")
    print(f"Database: {db_config['database']}")
    print(f"User: {db_config['user']}")
    
    # Try to connect
    connection = MySQLdb.connect(**db_config)
    print("\n✅ Successfully connected to MySQL!")
    connection.close()
    
    print("\n✅ The database credentials are correct!")
    
except MySQLdb.Error as e:
    print(f"\n❌ Error: {e}")
    print("\nPossible solutions:")
    print("1. Verify that MySQL server is running")
    print("2. Check if the username and password are correct")
    print("3. Make sure the database exists")
    print("4. Check if the user has the necessary permissions")
    print("\nFor a new MySQL installation, the default root password might be empty. Try with an empty password.")
