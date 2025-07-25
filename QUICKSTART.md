# 🚀 Quick Start Guide - Mess Menu Rater

## ⚡ Instant Setup (Windows)

### Option 1: Automated Setup
```batch
# Run the setup script
setup.bat

# Start the application
start_app.bat
```

### Option 2: Manual Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup database
python setup.py

# 3. Start application
python app.py
```

## 🌐 Access the Application

Open your browser and go to: **http://localhost:5000**

## 🔑 Default Login Credentials

### Admin Access
- **Username**: `admin`
- **Password**: `admin123`

### Student Access
- Create new account by clicking "Register"
- Use your new credentials to login

## 📱 Quick User Guide

### For Students:
1. **Register** → Create your account
2. **Browse Menu** → View today's items with ratings
3. **Rate Items** → Click stars (1-5) and add comments
4. **Place Orders** → Add items to cart (basic KOT system)

### For Admins:
1. **Login** → Use admin credentials
2. **Add Menu** → Add items for specific dates
3. **View Analytics** → Check ratings and statistics
4. **Manage** → Monitor student feedback

## 🎯 Key Features

- ⭐ **5-Star Rating System** - Students rate meals
- 👨‍💼 **Admin Dashboard** - Menu management interface
- 📊 **Analytics** - Rating statistics and charts
- 🛒 **Order System** - Basic KOT functionality
- 📱 **Responsive Design** - Works on all devices
- 🔐 **Secure Authentication** - Password hashing

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Charts**: Chart.js

## 📁 Project Structure

```
MessMenuRater/
├── app.py              # Main application
├── setup.py            # Database setup
├── requirements.txt    # Dependencies
├── setup.bat          # Windows setup script
├── start_app.bat      # Windows start script
├── database/          # Database files
├── static/            # CSS & JavaScript
├── templates/         # HTML templates
└── Readme.md          # Full documentation
```

## 🔧 Troubleshooting

### Common Issues:

**App won't start?**
- Run `python setup.py` first
- Check Python version (3.7+)
- Install requirements: `pip install -r requirements.txt`

**Database errors?**
- Delete `database/mess_menu.db`
- Run `python setup.py` again

**Static files not loading?**
- Check `static/` folder exists
- Clear browser cache

## 📞 Support

1. Check **Readme.md** for detailed documentation
2. Run `python test_installation.py` to verify setup
3. Ensure all files are present in project directory

---

**🎉 Happy Rating! Enjoy your mess menu management system!**
