const mongoose = require('mongoose');

const vendorSchema = new mongoose.Schema(
  {
    name:        { type: String, required: true, trim: true },
    email:       { type: String, required: true, unique: true, lowercase: true },
    password:    { type: String, required: true, select: false },
    phone:       { type: String },
    cuisine:     { type: String },
    address:     { type: String },
    location: {
      lat: { type: Number },
      lng: { type: Number },
    },
    logo:        { type: String },        // URL
    coverImage:  { type: String },        // URL
    rating:      { type: Number, default: 0 },
    totalReviews:{ type: Number, default: 0 },
    isActive:    { type: Boolean, default: true },
    isApproved:  { type: Boolean, default: false },
    openingTime: { type: String },
    closingTime: { type: String },
    status:      { type: String, enum: ['open', 'closed'], default: 'open' },
  },
  { timestamps: true }
);

module.exports = mongoose.model('Vendor', vendorSchema);
