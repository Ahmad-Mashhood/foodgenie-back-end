const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const vendorController = require('../controllers/vendor.controller');

// Public vendor discovery
router.get('/', vendorController.getAllVendors);
router.get('/:id', vendorController.getVendorById);
router.post('/register', vendorController.registerVendor);
router.get('/:id/menu', vendorController.getVendorMenu);

// Protected vendor actions
router.put('/:id', auth(['vendor', 'admin']), vendorController.updateVendor);
router.get('/:id/orders', auth(['vendor', 'admin']), vendorController.getVendorOrders);
router.patch('/:id/status', auth(['vendor']), vendorController.updateVendorStatus);

module.exports = router;
