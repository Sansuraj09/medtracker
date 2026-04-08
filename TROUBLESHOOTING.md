# MySQL Troubleshooting Guide

## Access Denied Error

If you get "Access denied for user 'root'@'localhost'", it means the password is wrong.

### Option 1: Verify Password
```bash
mysql -u root -p
# Enter your MySQL password when prompted
```

If this works, copy that password into `.env`:
```env
MYSQL_PASSWORD=your-actual-password
```

### Option 2: Reset MySQL Root Password (Windows)

1. Stop MySQL Service:
```bash
# Open PowerShell as Administrator
net stop MySQL80  # or "MySQL57" depending on your version
```

2. Start MySQL without password:
```bash
mysqld --skip-grant-tables
```

3. In another PowerShell window:
```bash
mysql -u root
```

4. Run these commands in MySQL:
```sql
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY 'your-new-password';
EXIT;
```

5. Restart MySQL normally:
```bash
net start MySQL80
```

### Option 3: Check MySQL Service Status
```bash
# PowerShell as Administrator
Get-Service MySQL*  # List all MySQL services
```

If the service isn't running, start it:
```bash
Start-Service MySQL80
```

### Option 4: Find MySQL Installation
```bash
mysql --version
where mysql
```

---

**After fixing the password**, update `.env` and run:
```bash
python init_db.py
```
