const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const adminController = require('../controllers/admin.controller');

router.get('/users', auth(['admin']), adminController.getAllUsers);
router.get('/vendors', auth(['admin']), adminController.getAllVendors);
router.patch('/vendors/:id/approve', auth(['admin']), adminController.approveVendor);
router.get('/orders', auth(['admin']), adminController.getAllOrders);
router.get('/analytics', auth(['admin']), adminController.getPlatformAnalytics);

module.exports = router;
