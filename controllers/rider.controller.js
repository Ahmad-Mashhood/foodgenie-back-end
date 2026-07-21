const User = require('../models/User');
const Order = require('../models/Order');

// GET /api/riders/:id
exports.getRiderById = async (req, res) => {
  try {
    const rider = await User.findOne({ _id: req.params.id, role: 'rider' });
    if (!rider) return res.status(404).json({ message: 'Rider not found.' });
    res.json(rider);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// PUT /api/riders/:id
exports.updateRider = async (req, res) => {
  try {
    if (req.user.role !== 'admin' && req.user.id !== req.params.id) {
      return res.status(403).json({ message: 'Access denied.' });
    }

    const rider = await User.findOneAndUpdate(
      { _id: req.params.id, role: 'rider' },
      req.body,
      { new: true }
    );
    if (!rider) return res.status(404).json({ message: 'Rider not found.' });
    res.json(rider);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// PATCH /api/riders/:id/location
// Body contains { lat, lng, orderId }
exports.updateRiderLocation = async (req, res) => {
  try {
    if (req.user.role !== 'admin' && req.user.id !== req.params.id) {
      return res.status(403).json({ message: 'Access denied.' });
    }

    const { lat, lng, orderId } = req.body;
    if (lat === undefined || lng === undefined) {
      return res.status(400).json({ message: 'Latitude and longitude are required.' });
    }

    // Save location to rider's profile
    const rider = await User.findOneAndUpdate(
      { _id: req.params.id, role: 'rider' },
      { 'location.lat': lat, 'location.lng': lng },
      { new: true }
    );

    if (!rider) return res.status(404).json({ message: 'Rider not found.' });

    // Emit live location updates via Socket.io
    const io = req.app.get('io');
    if (io) {
      // 1. Broadcast to the order room
      if (orderId) {
        io.to(`order_${orderId}`).emit('rider:locationUpdate', { riderId: req.params.id, lat, lng });
      }
      // 2. Also broadcast to customer room directly if we have the order
      if (orderId) {
        const order = await Order.findById(orderId);
        if (order) {
          io.to(`user_${order.customer}`).emit('rider:locationUpdate', { orderId, lat, lng });
        }
      }
    }

    res.json({ message: 'Location updated successfully.', location: { lat, lng } });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// GET /api/riders/:id/deliveries
exports.getRiderDeliveries = async (req, res) => {
  try {
    if (req.user.role !== 'admin' && req.user.id !== req.params.id) {
      return res.status(403).json({ message: 'Access denied.' });
    }

    const deliveries = await Order.find({ rider: req.params.id })
      .populate('customer', 'name email phone location')
      .populate('vendor', 'name address phone location')
      .sort('-createdAt');

    res.json(deliveries);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// PATCH /api/riders/:id/availability
// Body contains { availability: true | false }
exports.updateRiderAvailability = async (req, res) => {
  try {
    if (req.user.role !== 'admin' && req.user.id !== req.params.id) {
      return res.status(403).json({ message: 'Access denied.' });
    }

    const { availability } = req.body;
    if (availability === undefined) {
      return res.status(400).json({ message: 'Availability boolean value is required.' });
    }

    const rider = await User.findOneAndUpdate(
      { _id: req.params.id, role: 'rider' },
      { availability },
      { new: true }
    );

    if (!rider) return res.status(404).json({ message: 'Rider not found.' });
    res.json(rider);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};
