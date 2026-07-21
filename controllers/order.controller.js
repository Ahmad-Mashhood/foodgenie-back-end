const Order = require('../models/Order');
const User = require('../models/User');
const Vendor = require('../models/Vendor');

// GET /api/orders/:id
exports.getOrderById = async (req, res) => {
  try {
    const order = await Order.findById(req.params.id)
      .populate('customer', 'name email phone location')
      .populate('vendor', 'name cuisine address phone location')
      .populate('rider', 'name phone location');

    if (!order) return res.status(404).json({ message: 'Order not found.' });

    // Restrict access to order participants or admin
    const userId = req.user.id;
    if (
      req.user.role !== 'admin' &&
      order.customer._id.toString() !== userId &&
      order.vendor._id.toString() !== userId &&
      (!order.rider || order.rider._id.toString() !== userId)
    ) {
      return res.status(403).json({ message: 'Access denied.' });
    }

    res.json(order);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// POST /api/orders
exports.placeOrder = async (req, res) => {
  try {
    const { vendor, items, totalAmount, deliveryAddress, paymentMethod, specialInstructions } = req.body;

    const order = await Order.create({
      customer: req.user.id,
      vendor,
      items,
      totalAmount,
      deliveryAddress,
      paymentMethod,
      specialInstructions,
      status: 'pending'
    });

    const populatedOrder = await Order.findById(order._id)
      .populate('customer', 'name phone location')
      .populate('vendor', 'name cuisine address')
      .populate('items.menuItem');

    // Emit Socket.io event: order:placed to the vendor room
    const io = req.app.get('io');
    if (io) {
      io.to(`vendor_${vendor}`).emit('order:placed', populatedOrder);
    }

    res.status(201).json(populatedOrder);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// PATCH /api/orders/:id/status
exports.updateOrderStatus = async (req, res) => {
  try {
    const { status } = req.body;
    const allowedStatuses = ['pending', 'confirmed', 'preparing', 'ready_for_pickup', 'out_for_delivery', 'delivered', 'cancelled'];
    if (!allowedStatuses.includes(status)) {
      return res.status(400).json({ message: 'Invalid status.' });
    }

    // Optional: assign rider if passed in body
    const updateFields = { status };
    if (req.body.riderId) {
      updateFields.rider = req.body.riderId;
    }

    const order = await Order.findByIdAndUpdate(req.params.id, updateFields, { new: true })
      .populate('customer', 'name email phone')
      .populate('vendor', 'name cuisine address')
      .populate('rider', 'name phone location');

    if (!order) return res.status(404).json({ message: 'Order not found.' });

    const io = req.app.get('io');
    if (io) {
      // Broadcast updates based on status transitions
      if (status === 'confirmed') {
        io.to(`user_${order.customer._id}`).emit('order:confirmed', order);
      } else if (status === 'out_for_delivery' || status === 'ready_for_pickup') {
        // notify customer and broadcast rider assignment
        io.to(`user_${order.customer._id}`).emit('order:picked', { order, rider: order.rider });
      } else if (status === 'delivered') {
        // notify all parties
        io.to(`user_${order.customer._id}`).emit('order:delivered', order);
        io.to(`vendor_${order.vendor._id}`).emit('order:delivered', order);
        if (order.rider) {
          io.to(`rider_${order.rider._id}`).emit('order:delivered', order);
        }
      }

      // Also broadcast general status update to the order's specific room
      io.to(`order_${order._id}`).emit('order_update', order);
    }

    res.json(order);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// DELETE /api/orders/:id
exports.cancelOrder = async (req, res) => {
  try {
    const order = await Order.findById(req.params.id);
    if (!order) return res.status(404).json({ message: 'Order not found.' });

    // Only customer who placed it or admin can cancel it
    if (req.user.role !== 'admin' && order.customer.toString() !== req.user.id) {
      return res.status(403).json({ message: 'Access denied.' });
    }

    if (order.status === 'delivered') {
      return res.status(400).json({ message: 'Delivered orders cannot be cancelled.' });
    }

    order.status = 'cancelled';
    await order.save();

    const populatedOrder = await Order.findById(order._id)
      .populate('customer', 'name phone')
      .populate('vendor', 'name')
      .populate('rider', 'name phone');

    // Notify parties of cancellation
    const io = req.app.get('io');
    if (io) {
      io.to(`user_${order.customer}`).emit('order_update', populatedOrder);
      io.to(`vendor_${order.vendor}`).emit('order_update', populatedOrder);
      if (order.rider) {
        io.to(`rider_${order.rider}`).emit('order_update', populatedOrder);
      }
    }

    res.json({ message: 'Order cancelled successfully.', order: populatedOrder });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};
