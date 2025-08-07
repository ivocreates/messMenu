# MessMenu Rater - Complete Mess Management System

A comprehensive web application for mess management that allows students to rate menu items, place orders, and track bills, while providing administrators with powerful tools to manage menus, orders, and analytics.

## Features

### For Students
- **Menu Rating & Reviews**: Rate and review mess items with 5-star rating system
- **Order Management**: Browse daily menu and place orders
- **Order Tracking**: Real-time order status tracking
- **Bill Management**: View weekly and monthly billing summaries
- **User Dashboard**: Personalized dashboard with recent activities

### For Administrators
- **Menu Management**: Complete CRUD operations for menu items
- **Daily Menu Setup**: Set and manage daily menu offerings
- **Order Management**: View and update order statuses
- **Analytics Dashboard**: Comprehensive statistics and insights
- **Student Bill Management**: Monitor and manage student expenses

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Bootstrap 5
- **Icons**: Font Awesome
- **Color Theme**: Custom color palette (#113F67, #34699A, #58A0C8, #FDF5AA)

## Project Structure

```
messmenu/
│
├── app.py                 # Main Flask application
├── init_db.py            # Database initialization script
├── requirements.txt       # Python dependencies
│
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Landing page
│   ├── login.html        # Login page
│   ├── register.html     # Student registration
│   │
│   ├── admin/            # Admin templates
│   │   ├── dashboard.html
│   │   ├── menu.html
│   │   ├── add_menu_item.html
│   │   ├── edit_menu_item.html
│   │   ├── daily_menu.html
│   │   └── orders.html
│   │
│   └── student/          # Student templates
│       ├── dashboard.html
│       ├── menu.html
│       ├── reviews.html
│       ├── review.html
│       ├── orders.html
│       └── bills.html
│
├── static/              # Static files
│   └── css/
│       └── custom.css   # Custom styles
│
├── setup.bat           # Windows setup script
├── start.bat           # Windows start script
├── setup.sh            # Linux/Mac setup script
├── start.sh            # Linux/Mac start script
└── README.md           # This file
```

## Installation & Setup

### Windows

1. **Clone or download** the project to your desired location
2. **Run setup script**:
   ```cmd
   setup.bat
   ```
3. **Start the application**:
   ```cmd
   start.bat
   ```

### Linux/Mac

1. **Clone or download** the project to your desired location
2. **Make scripts executable**:
   ```bash
   chmod +x setup.sh start.sh
   ```
3. **Run setup script**:
   ```bash
   ./setup.sh
   ```
4. **Start the application**:
   ```bash
   ./start.sh
   ```

### Manual Setup

If the automated scripts don't work, follow these manual steps:

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment**:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database**:
   ```bash
   python init_db.py
   ```

5. **Start application**:
   ```bash
   python app.py
   ```

## Default Login Credentials

### Administrator
- **Username**: admin
- **Password**: admin123

### Student
- **Username**: student
- **Password**: student123

## Usage Guide

### First Time Setup

1. Run the setup script for your operating system
2. Access the application at `http://localhost:5000`
3. Login with the default credentials
4. Change default passwords (recommended)

### For Students

1. **Registration**: Create a new account using the registration form
2. **Menu Browsing**: View daily menu items with ratings and prices
3. **Rating Items**: Click on any menu item to rate and review
4. **Placing Orders**: Select items from daily menu and place orders
5. **Tracking Orders**: Monitor order status in real-time
6. **Viewing Bills**: Check weekly and monthly expenses

### For Administrators

1. **Menu Management**: Add, edit, or remove menu items
2. **Daily Menu**: Set which items are available each day
3. **Order Processing**: Update order statuses (pending → preparing → ready → completed)
4. **Analytics**: Monitor sales, popular items, and revenue
5. **Student Management**: View student bills and order history

## Database Schema

### Tables
- **students**: Student user accounts
- **admins**: Administrator accounts
- **menu_items**: Available menu items
- **daily_menu**: Daily menu configurations
- **reviews**: Student ratings and reviews
- **orders**: Order records
- **order_items**: Individual items in orders

## API Endpoints

### Authentication
- `GET/POST /login` - User login
- `GET/POST /register` - Student registration
- `GET /logout` - User logout

### Student Routes
- `GET /student/dashboard` - Student dashboard
- `GET /student/menu` - Full menu view
- `GET /student/reviews` - User's reviews
- `GET/POST /student/review/<id>` - Add/edit review
- `GET /student/orders` - Order history
- `POST /student/order` - Place new order (JSON API)
- `GET /student/bills` - Billing information

### Admin Routes
- `GET /admin/dashboard` - Admin dashboard with analytics
- `GET /admin/menu` - Menu management
- `GET/POST /admin/menu/add` - Add menu item
- `GET/POST /admin/menu/edit/<id>` - Edit menu item
- `GET /admin/menu/delete/<id>` - Delete menu item
- `GET /admin/daily-menu` - Daily menu management
- `POST /admin/daily-menu/add` - Add item to daily menu
- `GET /admin/orders` - Order management
- `POST /admin/orders/update/<id>` - Update order status

## Customization

### Color Theme
The application uses a custom color palette defined in CSS variables:
- Primary: #113F67 (Dark Blue)
- Secondary: #34699A (Medium Blue)
- Accent: #58A0C8 (Light Blue)
- Light: #FDF5AA (Light Yellow)

To customize colors, edit the `:root` section in `static/css/custom.css`.

### Adding New Features

1. **Database Changes**: Modify `init_db.py` to add new tables
2. **Backend Logic**: Add new routes in `app.py`
3. **Frontend**: Create new templates in the appropriate directory
4. **Styling**: Add custom CSS in `static/css/custom.css`

## Security Features

- Password hashing using SHA-256
- Session management
- CSRF protection
- SQL injection prevention with parameterized queries
- Role-based access control

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in `app.py` (last line)
2. **Database errors**: Delete `messmenu.db` and run `python init_db.py`
3. **Permission errors**: Make sure scripts are executable (`chmod +x`)
4. **Python not found**: Ensure Python 3.7+ is installed and in PATH

### Logs
Flask development server provides detailed error logs in the console.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the code comments
3. Create an issue in the repository

## Future Enhancements

Potential features for future versions:
- Email notifications
- Payment integration
- Mobile app
- Advanced analytics
- Inventory management
- Multi-language support
- Social features (sharing reviews)
- Meal planning
- Nutritional information

---

**MessMenu Rater** - Making mess management delicious and efficient! 🍽️⭐
