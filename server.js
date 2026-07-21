const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const mongoose = require('mongoose');
const cors = require('cors');
require('dotenv').config();

// Route imports
const authRoutes = require('./routes/auth.routes');
const customerRoutes = require('./routes/customer.routes');
const foodRoutes = require('./routes/food.routes');
const vendorRoutes = require('./routes/vendor.routes');
const recommendationRoutes = require('./routes/recommendation.routes');
const orderRoutes = require('./routes/order.routes');
const riderRoutes = require('./routes/rider.routes');
const searchRoutes = require('./routes/search.routes');
const adminRoutes = require('./routes/admin.routes');

const app    = express();
const server = http.createServer(app);
const io     = new Server(server, {
  cors: { origin: '*', methods: ['GET', 'POST'] },
});

// Set Socket.io instance on app for controllers access
app.set('io', io);

// ── Middleware ────────────────────────────────────────────────────────────────
app.use(cors());
app.use(express.json());

// ── Routes ────────────────────────────────────────────────────────────────────
app.use('/api/auth', authRoutes);
app.use('/api/customers', customerRoutes);
app.use('/api/foods', foodRoutes);
app.use('/api/vendors', vendorRoutes);
app.use('/api/recommendations', recommendationRoutes);
app.use('/api/orders', orderRoutes);
app.use('/api/riders', riderRoutes);
app.use('/api/search', searchRoutes);
app.use('/api/admin', adminRoutes);

// ── Socket.io ─────────────────────────────────────────────────────────────────
io.on('connection', (socket) => {
  console.log(`Socket connected: ${socket.id}`);

  socket.on('join_room', (room) => {
    socket.join(room);
    console.log(`Socket ${socket.id} joined room ${room}`);
  });

  socket.on('order_update', (data) => {
    io.to(data.room).emit('order_update', data);
  });

  socket.on('rider:locationUpdate', (data) => {
    // data: { orderId, lat, lng, riderId }
    io.to(`order_${data.orderId}`).emit('rider:locationUpdate', data);
    io.to(`user_${data.customerId}`).emit('rider:locationUpdate', data);
  });

  socket.on('disconnect', () => {
    console.log(`Socket disconnected: ${socket.id}`);
  });
});

// ── Database + start ──────────────────────────────────────────────────────────
const PORT    = process.env.PORT || 5000;
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/food-genie';

mongoose
  .connect(MONGO_URI)
  .then(() => {
    console.log('✅  MongoDB connected');
    server.listen(PORT, () => console.log(`🚀  Server running on port ${PORT}`));
  })
  .catch((err) => {
    console.error('❌  MongoDB connection error:', err);
    process.exit(1);
  });

module.exports = { io };
