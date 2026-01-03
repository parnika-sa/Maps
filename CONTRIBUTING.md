# 🤝 Contributing Guide

Thanks for your interest in improving this project! 🎉

## How to Contribute

### **1. Fork the Repository**
Click the "Fork" button at the top right on GitHub

### **2. Clone Your Fork**
```bash
git clone https://github.com/YOUR_USERNAME/Maps.git
cd Maps
```

### **3. Create a New Branch**
```bash
git checkout -b feature/your-feature-name
```

**Branch naming:**
- `feature/` for new features
- `fix/` for bug fixes
- `docs/` for documentation

### **4. Make Your Changes**

```bash
# Install dev dependencies
pip install -r requirements.txt

# Make changes
# Test your code
python test_setup.py

# Commit changes
git add .
git commit -m "Clear description of what you changed"
```

### **5. Push to Your Fork**
```bash
git push origin feature/your-feature-name
```

### **6. Create Pull Request**
- Go to GitHub
- Click "Compare & pull request"
- Write clear description
- Submit! ✅

---

## 💡 Contribution Ideas

- **Bug Fixes** - Find and fix bugs
- **Performance** - Make it faster
- **Features** - Add new capabilities
- **Documentation** - Improve guides
- **Tests** - Add more test coverage

---

## 📝 Commit Message Guide

**Good:**
```
Add email validation for false positives
Fix: handle timeout errors gracefully
Improve: reduce API latency by 30%
```

**Bad:**
```
fixed stuff
update
changes
```

---

## 🧪 Before Submitting

1. Run tests:
```bash
python test_setup.py
```

2. Check code:
```bash
# Make sure no syntax errors
python -m py_compile *.py
```

3. Update README if needed

---

## 📋 Code Style

- Follow PEP 8 Python guidelines
- Use meaningful variable names
- Add comments for complex logic
- Keep functions small and focused

---

## ❓ Questions?

Create an Issue on GitHub for discussion.

---

**Thank you for contributing!** 🙏
