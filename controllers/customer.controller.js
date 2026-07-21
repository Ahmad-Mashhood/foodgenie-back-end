const User = require('../models/User');
const Order = require('../models/Order');

// GET /api/customers/:id
exports.getCustomerById = async (req, res) => {
  try {
    const customer = await User.findOne({ _id: req.params.id, role: 'customer' });
    if (!customer) return res.status(404).json({ message: 'Customer not found.' });
    res.json(customer);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// PUT /api/customers/:id
exports.updateCustomer = async (req, res) => {
  try {
    // Restrict updates to the logged-in customer or admin
    if (req.user.role !== 'admin' && req.user.id !== req.params.id) {
      return res.status(403).json({ message: 'Access denied.' });
    }

    const customer = await User.findOneAndUpdate(
      { _id: req.params.id, role: 'customer' },
      req.body,
      { new: true }
    );
    if (!customer) return res.status(404).json({ message: 'Customer not found.' });
    res.json(customer);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// PATCH /api/customers/:id/preferences
// Body can contain { diet, calories, healthGoals }
exports.updatePreferences = async (req, res) => {
  try {
    if (req.user.role !== 'admin' && req.user.id !== req.params.id) {
      return res.status(403).json({ message: 'Access denied.' });
    }

    const { diet, calories, healthGoals } = req.body;
    const updateData = {};
    if (diet !== undefined) updateData['preferences.diet'] = diet;
    if (calories !== undefined) updateData['preferences.calories'] = calories;
    if (healthGoals !== undefined) updateData['preferences.healthGoals'] = healthGoals;

    const customer = await User.findOneAndUpdate(
      { _id: req.params.id, role: 'customer' },
      { $set: updateData },
      { new: true }
    );
    if (!customer) return res.status(404).json({ message: 'Customer not found.' });
    res.json(customer);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// GET /api/customers/:id/orders
exports.getCustomerOrders = async (req, res) => {
  try {
    if (req.user.role !== 'admin' && req.user.id !== req.params.id) {
      return res.status(403).json({ message: 'Access denied.' });
    }

    const orders = await Order.find({ customer: req.params.id })
      .populate('vendor', 'name cuisine address')
      .populate('rider', 'name phone')
      .sort('-createdAt');
    res.json(orders);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// GET /api/customers/:id/favorites
exports.getCustomerFavorites = async (req, res) => {
  try {
    if (req.user.role !== 'admin' && req.user.id !== req.params.id) {
      return res.status(403).json({ message: 'Access denied.' });
    }

    const customer = await User.findOne({ _id: req.params.id, role: 'customer' })
      .populate({
        path: 'favorites',
        populate: { path: 'vendor', select: 'name address' }
      });
    if (!customer) return res.status(404).json({ message: 'Customer not found.' });
    res.json(customer.favorites || []);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};
