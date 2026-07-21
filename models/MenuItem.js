const mongoose = require('mongoose');

const menuItemSchema = new mongoose.Schema(
  {
    vendor:      { type: mongoose.Schema.Types.ObjectId, ref: 'Vendor', required: true },
    name:        { type: String, required: true, trim: true },
    description: { type: String },
    price:       { type: Number, required: true },
    category:    { type: String },
    image:       { type: String },        // URL
    isAvailable: { type: Boolean, default: true },
    calories:    { type: Number, default: 0 },
    tags:        [{ type: String }],      // e.g. ['vegan', 'spicy']
  },
  { timestamps: true }
);

module.exports = mongoose.model('MenuItem', menuItemSchema);
