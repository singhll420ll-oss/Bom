# BMB - Bite Me Buddy

A complete production-ready food ordering platform with admin panel, customer interface, and team member management.

## Features

### 🍽️ Customer Features
- User registration and authentication
- Browse food services and menu items
- Add items to cart and place orders
- Real-time order tracking
- Order history and favorites
- Profile management

### 👨‍🍳 Team Member Features
- View assigned orders
- Accept/reject orders
- OTP-based delivery verification
- View daily plans and tasks
- Performance tracking
- Break management

### 👨‍💼 Admin Features
- Complete admin dashboard
- Service and menu management
- User management (customers, team members)
- Order assignment and management
- Plan creation for team members
- Reports and analytics
- System health monitoring

### 🔒 Security Features
- JWT token authentication
- OTP verification via SMS
- Password hashing with bcrypt
- Input validation and sanitization
- Rate limiting
- CSRF protection
- Role-based access control

### 📱 Technical Features
- Real-time digital clock (IST)
- Secret admin access (15s long press + 5 taps on clock)
- Mobile-responsive design
- HTMX for dynamic updates
- Async database operations
- Comprehensive logging
- Docker support

## Technology Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: Jinja2 templates, HTMX, Bootstrap 5, Font Awesome
- **Authentication**: JWT tokens, OTP via Twilio
- **Database**: PostgreSQL with async support
- **Deployment**: Docker, Docker Compose

## Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis (optional, for caching)
- Twilio account (for SMS OTP)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bite-me-buddy
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**
   ```bash
   alembic upgrade head
   ```

6. **Seed initial data (optional)**
   ```bash
   python seed_data.py
   ```

7. **Run the application**
   ```bash
   # Development mode
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   
   # Production mode
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

## Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Access the application**
   - Main application: http://localhost:8000
   - API documentation: http://localhost:8000/docs

## Admin Panel Access

The admin panel has a secret access method:

1. Go to the home page (http://localhost:8000)
2. Long press (15 seconds) on the digital clock
3. Tap 5 times on the clock
4. Set the time to **3:43** (AM or PM)
5. You will be redirected to the admin login page

**Note**: There are no visual hints for this feature as per security requirements.

## API Documentation

Once the application is running, you can access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
.
├── main.py                 # FastAPI application entry point
├── database.py            # Database configuration
├── core/                  # Core functionality
│   ├── config.py          # Configuration management
│   ├── security.py        # Security utilities
│   ├── exceptions.py      # Custom exceptions
│   └── logging.py         # Logging configuration
├── models/                # Database models
├── schemas/               # Pydantic schemas
├── routers/               # API routes
├── crud/                  # CRUD operations
├── templates/             # HTML templates
├── static/                # Static files (CSS, JS)
├── alembic/              # Database migrations
├── tests/                 # Test files
└── docker-compose.yml     # Docker configuration
```

## Environment Variables

### Required
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Secret key for JWT tokens
- `TWILIO_ACCOUNT_SID`: Twilio account SID
- `TWILIO_AUTH_TOKEN`: Twilio auth token
- `TWILIO_PHONE_NUMBER`: Twilio phone number

### Optional
- `REDIS_URL`: Redis connection string
- `SENTRY_DSN`: Sentry error tracking DSN
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `ENVIRONMENT`: Environment (development, production)

## Testing

Run tests with pytest:
```bash
pytest tests/ -v
```

Run tests with coverage:
```bash
pytest tests/ --cov=.
```

## Deployment

### Using Docker
```bash
docker-compose up -d
```

### Using systemd (Linux)
1. Create service file: `/etc/systemd/system/bmb.service`
2. Enable and start service:
   ```bash
   sudo systemctl enable bmb
   sudo systemctl start bmb
   ```

### Using PM2 (Node.js process manager)
```bash
pm2 start main.py --name bmb --interpreter python3
pm2 save
pm2 startup
```

## Security Considerations

1. **Change default secret keys** before production deployment
2. **Use HTTPS** in production
3. **Configure firewall** to restrict access
4. **Regular security updates** for dependencies
5. **Monitor logs** for suspicious activity
6. **Backup database** regularly

## Performance Optimization

1. **Database indexing** is already configured
2. **Connection pooling** for database connections
3. **Async operations** throughout the application
4. **Caching** support with Redis (optional)
5. **CDN** for static files in production

## Monitoring

- Application logs are in the `logs/` directory
- Health check endpoint: `/health`
- Structured JSON logging for production
- Error tracking with Sentry (optional)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Run tests: `pytest`
6. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support, please contact:
- Email: support@bitemebuddy.com
- Phone: +91 1234567890

## Changelog

### Version 1.0.0
- Initial release
- Complete food ordering platform
- Admin panel with secret access
- Customer and team member interfaces
- OTP authentication
- Real-time features