const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const Vendor = require('../models/Vendor');
const MenuItem = require('../models/MenuItem');
const Order = require('../models/Order');

const signToken = (vendor) =>
  jwt.sign(
    { id: vendor._id, role: 'vendor' },
    process.env.JWT_SECRET || 'food_genie_secret',
    { expiresIn: '7d' }
  );

// GET /api/vendors
exports.getAllVendors = async (req, res) => {
  try {
    const vendors = await Vendor.find({ isActive: true, isApproved: true });
    res.json(vendors);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// GET /api/vendors/:id
exports.getVendorById = async (req, res) => {
  try {
    const vendor = await Vendor.findById(req.params.id);
    if (!vendor) return res.status(404).json({ message: 'Vendor not found.' });
    res.json(vendor);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// POST /api/vendors/register
exports.registerVendor = async (req, res) => {
  try {
    const { name, email, password, phone, address, cuisine } = req.body;
    const exists = await Vendor.findOne({ email });
    if (exists) return res.status(400).json({ message: 'Email already in use.' });

    const hashed = await bcrypt.hash(password, 12);
    const vendor = await Vendor.create({
      name,
      email,
      password: hashed,
      phone,
      address,
      cuisine,
      isApproved: false // Requires admin approval
    });

    const vendorResponse = vendor.toObject();
    delete vendorResponse.password;

    res.status(201).json({
      token: signToken(vendor),
      vendor: vendorResponse
    });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// PUT /api/vendors/:id
exports.updateVendor = async (req, res) => {
  try {
    if (req.user.role !== 'admin' && req.user.id !== req.params.id) {
      return res.status(403).json({ message: 'Access denied.' });
    }

    const vendor = await Vendor.findByIdAndUpdate(req.params.id, req.body, { new: true });
    if (!vendor) return res.status(404).json({ message: 'Vendor not found.' });
    res.json(vendor);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// GET /api/vendors/:id/menu
exports.getVendorMenu = async (req, res) => {
  try {
    const menu = await MenuItem.find({ vendor: req.params.id });
    res.json(menu);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// GET /api/vendors/:id/orders
exports.getVendorOrders = async (req, res) => {
  try {
    if (req.user.role !== 'admin' && req.user.id !== req.params.id) {
      return res.status(403).json({ message: 'Access denied.' });
    }

    const orders = await Order.find({ vendor: req.params.id })
      .populate('customer', 'name email phone')
      .populate('rider', 'name phone')
      .sort('-createdAt');
    res.json(orders);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// PATCH /api/vendors/:id/status
// Body contains { status: 'open' | 'closed' }
exports.updateVendorStatus = async (req, res) => {
  try {
    if (req.user.role !== 'admin' && req.user.id !== req.params.id) {
      return res.status(403).json({ message: 'Access denied.' });
    }

    const { status } = req.body;
    if (!['open', 'closed'].includes(status)) {
      return res.status(400).json({ message: 'Invalid status. Must be open or closed.' });
    }

    const vendor = await Vendor.findByIdAndUpdate(
      req.params.id,
      { status },
      { new: true }
    );
    if (!vendor) return res.status(404).json({ message: 'Vendor not found.' });
    res.json(vendor);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};
