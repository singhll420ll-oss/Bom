# BMB - Bite Me Buddy Setup Instructions

## Quick Start Guide

This guide will help you set up and run the complete BMB food ordering platform.

## Prerequisites

1. **Python 3.11+** installed
2. **PostgreSQL 14+** installed and running
3. **Redis** (optional, for caching)
4. **Git** for version control

## Step-by-Step Setup

### 1. Environment Setup

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd bite-me-buddy

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Configuration

```bash
# Create PostgreSQL database
createdb bite_me_buddy

# Copy environment template
cp .env.example .env

# Edit .env file with your database credentials
nano .env  # or use your preferred editor
```

**Required .env settings:**
```env
DATABASE_URL=postgresql+asyncpg://username:password@localhost/bite_me_buddy
SECRET_KEY=your-super-secret-key-here-change-in-production
```

### 3. Database Migration

```bash
# Initialize database tables
alembic upgrade head
```

### 4. Create Admin User (Optional)

```bash
# You can create an admin user directly in the database
# Or use the secret clock method described below
```

### 5. Run the Application

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 6. Access the Application

- **Main Website**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

## Admin Panel Access

The admin panel has a **secret access method** for security:

### Method 1: Secret Clock (Recommended)

1. Go to http://localhost:8000
2. **Long press (15 seconds)** on the digital clock
3. **Tap 5 times** on the clock
4. Set the time to **3:43** (AM or PM)
5. You'll be redirected to admin login

**Important**: There are **no visual hints** for this feature by design.

### Method 2: Direct Access

Go to: http://localhost:8000/admin-login

## User Roles

### 👤 Customer
- Register and login
- Browse services and menu
- Place orders
- Track orders
- View order history

### 👨‍🍳 Team Member
- Login with team credentials
- View assigned orders
- Accept/reject orders
- Verify delivery with OTP
- View daily plans

### 👨‍💼 Admin
- Full system access
- Manage users, services, menu items
- Create plans for team members
- View reports and analytics
- System health monitoring

## Testing the Application

### 1. Register as Customer
1. Click "New Registration"
2. Fill in customer details
3. Verify phone number with OTP
4. Start ordering food

### 2. Create Team Member Account
1. Admin needs to create team member account
2. Team member can login and manage deliveries

### 3. Place an Order
1. Login as customer
2. Browse services and menu items
3. Add items to cart
4. Checkout and place order
5. Track order status

### 4. Manage Order as Team Member
1. Login as team member
2. View assigned orders
3. Accept order and start delivery
4. Verify delivery with OTP

## Docker Setup (Alternative)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop containers
docker-compose down
```

## Environment Variables

### Required
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Secret key for JWT tokens (change in production!)

### Optional but Recommended
- `TWILIO_ACCOUNT_SID`: For SMS OTP
- `TWILIO_AUTH_TOKEN`: For SMS OTP
- `TWILIO_PHONE_NUMBER`: For SMS OTP
- `REDIS_URL`: For caching
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Troubleshooting

### Database Connection Error
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Create database if not exists
createdb bite_me_buddy

# Check database connection
psql -U postgres -d bite_me_buddy -c "SELECT 1;"
```

### Migration Issues
```bash
# Reset database completely
alembic downgrade base
alembic upgrade head

# Or drop and recreate database
dropdb bite_me_buddy
createdb bite_me_buddy
alembic upgrade head
```

### Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process or use different port
uvicorn main:app --reload --port 8001
```

### Missing Dependencies
```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

## Production Deployment

### 1. Security Checklist
- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS
- [ ] Configure firewall
- [ ] Set up monitoring
- [ ] Configure backups

### 2. Performance Optimization
- Use PostgreSQL connection pooling
- Enable Redis caching
- Use CDN for static files
- Configure proper logging
- Set up monitoring

### 3. Monitoring
- Application logs: `logs/app.log`
- Error logs: `logs/error.log`
- Database logs: `logs/database.log`
- Performance logs: `logs/performance.log`

## API Usage

### Authentication
```python
# Login
POST /api/auth/login
{
    "login_field": "email@example.com",
    "password": "password123"
}

# Register
POST /api/auth/register/customer
{
    "name": "John Doe",
    "username": "johndoe",
    "email": "john@example.com",
    "phone": "9123456789",
    "password": "SecurePass123!",
    "address": "123 Main Street"
}
```

### Orders
```python
# Create order
POST /api/orders/create
{
    "service_id": 1,
    "order_items": [
        {
            "menu_item_id": 1,
            "quantity": 2
        }
    ],
    "address": "Delivery Address",
    "phone": "9123456789"
}
```

## Common Issues and Solutions

### Issue: "Database connection failed"
**Solution**: 
1. Check PostgreSQL is running: `sudo systemctl start postgresql`
2. Verify database exists: `psql -l | grep bite_me_buddy`
3. Check connection string in .env

### Issue: "Module not found"
**Solution**: 
1. Activate virtual environment
2. Install dependencies: `pip install -r requirements.txt`

### Issue: "Port already in use"
**Solution**: 
1. Use different port: `uvicorn main:app --port 8001`
2. Kill process using port: `kill -9 <pid>`

### Issue: "Admin access not working"
**Solution**: 
1. Make sure to long press for exactly 15 seconds
2. Tap 5 times quickly after long press
3. Set time to exactly 3:43 (not 15:43 or other)
4. Check browser console for errors

## Support

If you encounter issues:
1. Check the logs in the `logs/` directory
2. Review the troubleshooting section above
3. Check API documentation at `/docs`
4. Contact support with error logs

## Next Steps

1. **Customize the application** for your needs
2. **Add more menu items** and services
3. **Set up team members** for order management
4. **Configure SMS service** for OTP
5. **Set up monitoring** and alerts
6. **Configure backups** for data safety

## License

This project is licensed under the MIT License.

---

**Enjoy using BMB - Bite Me Buddy!** 🍽️