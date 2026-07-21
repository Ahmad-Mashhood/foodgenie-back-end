const mongoose = require('mongoose');

const userSchema = new mongoose.Schema(
  {
    name:     { type: String, required: true, trim: true },
    email:    { type: String, required: true, unique: true, lowercase: true },
    password: { type: String, required: true, select: false },
    phone:    { type: String },
    role:     { type: String, enum: ['customer', 'rider', 'admin'], default: 'customer' },
    isActive: { type: Boolean, default: true },
    location: {
      lat: { type: Number },
      lng: { type: Number },
    },
    addresses: [
      {
        label:   String,
        address: String,
        lat:     Number,
        lng:     Number,
      },
    ],
    preferences: {
      diet:        { type: String, default: '' },
      calories:    { type: Number, default: 2000 },
      healthGoals: [{ type: String }],
    },
    favorites: [
      { type: mongoose.Schema.Types.ObjectId, ref: 'MenuItem' },
    ],
    availability: { type: Boolean, default: true },
  },
  { timestamps: true }
);

module.exports = mongoose.model('User', userSchema);
