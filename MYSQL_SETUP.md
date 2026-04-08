# MySQL Setup Guide for MedTracker

## Prerequisites
- MySQL Server installed and running
- Python 3.7+

## Installation Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create or update your `.env` file with MySQL credentials:

```env
# MySQL Database Configuration
MYSQL_USER=root
MYSQL_PASSWORD=your-mysql-password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=medtracker

# Alternative: Use DATABASE_URL directly
# DATABASE_URL=mysql+pymysql://root:password@localhost:3306/medtracker
```

### 3. Initialize the Database
Run the initialization script to create the database and tables:

```bash
python init_db.py
```

This script will:
- Create the MySQL database `medtracker` if it doesn't exist
- Create all required tables:
  - `users` - User accounts
  - `patients` - Patient information
  - `medicines` - Medicine details
  - `reminders` - Medication reminders
  - `dose_history` - Dose administration history

### 4. Run the Application
```bash
python app.py
```

The Flask app will be available at `http://localhost:5000`

## Database Schema

### Patients Table
The `patients` table contains the following fields:
- `id` (Integer, Primary Key)
- `first_name` (String, Required)
- `last_name` (String, Required)
- `email` (String, Unique, Optional)
- `phone` (String, Optional)
- `date_of_birth` (Date, Optional)
- `gender` (String, Optional)
- `address` (String, Optional)
- `medical_history` (Text, Optional)
- `allergies` (Text, Optional)
- `emergency_contact` (String, Optional)
- `created_at` (DateTime)
- `updated_at` (DateTime)

## Docker Setup (Optional)

To run MySQL in Docker, add this to your `docker-compose.yaml`:

```yaml
version: '3'
services:
  mysql:
    image: mysql:8.0
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: your-password
      MYSQL_DATABASE: medtracker
    volumes:
      - mysql_data:/var/lib/mysql

  medtracker:
    build: .
    ports:
      - "5000:5000"
    environment:
      - MYSQL_USER=root
      - MYSQL_PASSWORD=your-password
      - MYSQL_HOST=mysql
      - MYSQL_PORT=3306
      - MYSQL_DB=medtracker
    depends_on:
      - mysql

volumes:
  mysql_data:
```

Then run: `docker-compose up`

## Troubleshooting

### Connection Error
If you get a "Connection refused" error:
1. Ensure MySQL server is running
2. Verify credentials in `.env` file
3. Check that `MYSQL_HOST` and `MYSQL_PORT` are correct

### Database Already Exists
The init script safely handles existing databases and won't overwrite data.

### Permission Denied
If you get permission errors:
1. Check MySQL user has required privileges
2. Run: `GRANT ALL PRIVILEGES ON medtracker.* TO 'root'@'localhost';`
3. Then: `FLUSH PRIVILEGES;`
