const User = require('../models/User');
const Vendor = require('../models/Vendor');
const Order = require('../models/Order');

// GET /api/admin/users
exports.getAllUsers = async (req, res) => {
  try {
    const users = await User.find({ role: { $ne: 'admin' } }).sort('-createdAt');
    res.json(users);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// GET /api/admin/vendors
exports.getAllVendors = async (req, res) => {
  try {
    const vendors = await Vendor.find().sort('-createdAt');
    res.json(vendors);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// PATCH /api/admin/vendors/:id/approve
exports.approveVendor = async (req, res) => {
  try {
    const vendor = await Vendor.findByIdAndUpdate(
      req.params.id,
      { isApproved: true },
      { new: true }
    );
    if (!vendor) return res.status(404).json({ message: 'Vendor not found.' });
    res.json(vendor);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// GET /api/admin/orders
exports.getAllOrders = async (req, res) => {
  try {
    const orders = await Order.find()
      .populate('customer', 'name email phone')
      .populate('vendor', 'name cuisine address')
      .populate('rider', 'name phone')
      .sort('-createdAt');
    res.json(orders);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// GET /api/admin/analytics
exports.getPlatformAnalytics = async (req, res) => {
  try {
    const [customersCount, ridersCount, vendorsCount, ordersCount] = await Promise.all([
      User.countDocuments({ role: 'customer' }),
      User.countDocuments({ role: 'rider' }),
      Vendor.countDocuments(),
      Order.countDocuments()
    ]);

    const revenueResult = await Order.aggregate([
      { $match: { status: 'delivered' } },
      { $group: { _id: null, total: { $sum: '$totalAmount' } } }
    ]);
    const totalRevenue = revenueResult[0]?.total || 0;

    const ordersByStatus = await Order.aggregate([
      { $group: { _id: '$status', count: { $sum: 1 } } }
    ]);

    res.json({
      users: { customers: customersCount, riders: ridersCount },
      vendorsCount,
      ordersCount,
      totalRevenue,
      ordersByStatus
    });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};
