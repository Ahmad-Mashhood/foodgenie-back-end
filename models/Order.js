const mongoose = require('mongoose');

const orderItemSchema = new mongoose.Schema({
  menuItem: { type: mongoose.Schema.Types.ObjectId, ref: 'MenuItem' },
  name:     { type: String },
  price:    { type: Number },
  quantity: { type: Number, default: 1 },
});

const orderSchema = new mongoose.Schema(
  {
    customer:    { type: mongoose.Schema.Types.ObjectId, ref: 'User',   required: true },
    vendor:      { type: mongoose.Schema.Types.ObjectId, ref: 'Vendor', required: true },
    rider:       { type: mongoose.Schema.Types.ObjectId, ref: 'User',   default: null },
    items:       [orderItemSchema],
    totalAmount: { type: Number, required: true },
    status: {
      type: String,
      enum: ['pending', 'confirmed', 'preparing', 'ready_for_pickup', 'out_for_delivery', 'delivered', 'cancelled'],
      default: 'pending',
    },
    deliveryAddress: {
      address: String,
      lat:     Number,
      lng:     Number,
    },
    paymentMethod: { type: String, enum: ['cash', 'card', 'wallet'], default: 'cash' },
    isPaid:        { type: Boolean, default: false },
    specialInstructions: { type: String },
  },
  { timestamps: true }
);

module.exports = mongoose.model('Order', orderSchema);
