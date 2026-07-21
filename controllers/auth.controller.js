const bcrypt = require('bcryptjs');
const jwt    = require('jsonwebtoken');
const User   = require('../models/User');
const Vendor = require('../models/Vendor');

const signToken = (id, role) =>
  jwt.sign(
    { id, role },
    process.env.JWT_SECRET || 'food_genie_secret',
    { expiresIn: '7d' }
  );

// POST /api/auth/register
exports.register = async (req, res) => {
  try {
    const { name, email, password, phone, role } = req.body;
    const targetRole = role || 'customer';

    if (!['customer', 'rider', 'admin'].includes(targetRole)) {
      return res.status(400).json({ message: 'Invalid role.' });
    }

    const exists = await User.findOne({ email });
    if (exists) return res.status(400).json({ message: 'Email already in use.' });

    const hashed = await bcrypt.hash(password, 12);
    const user   = await User.create({
      name,
      email,
      password: hashed,
      phone,
      role: targetRole
    });

    // Strip password
    const userResponse = user.toObject();
    delete userResponse.password;

    res.status(201).json({
      token: signToken(user._id, user.role),
      user: userResponse
    });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// POST /api/auth/login
exports.login = async (req, res) => {
  try {
    const { email, password } = req.body;

    // 1. Try checking the User collection
    let account = await User.findOne({ email }).select('+password');
    let role = account ? account.role : null;
    let type = 'user';

    // 2. If not found, try Vendor collection
    if (!account) {
      account = await Vendor.findOne({ email }).select('+password');
      if (account) {
        role = 'vendor';
        type = 'vendor';
      }
    }

    if (!account || !(await bcrypt.compare(password, account.password))) {
      return res.status(401).json({ message: 'Invalid credentials.' });
    }

    const token = signToken(account._id, role);
    const accountObj = account.toObject();
    delete accountObj.password;

    res.json({
      token,
      [type]: accountObj,
      role
    });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// GET /api/auth/me
exports.me = async (req, res) => {
  try {
    if (!req.user) {
      return res.status(401).json({ message: 'Not authenticated.' });
    }

    let account;
    if (req.user.role === 'vendor') {
      account = await Vendor.findById(req.user.id);
    } else {
      account = await User.findById(req.user.id);
    }

    if (!account) {
      return res.status(404).json({ message: 'Account not found.' });
    }

    res.json(account);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// POST /api/auth/logout
exports.logout = async (req, res) => {
  res.json({ message: 'Logged out successfully.' });
};
