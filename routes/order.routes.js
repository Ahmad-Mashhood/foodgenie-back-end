const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const orderController = require('../controllers/order.controller');

router.get('/:id', auth(['customer', 'vendor', 'rider', 'admin']), orderController.getOrderById);
router.post('/', auth(['customer', 'admin']), orderController.placeOrder);
router.patch('/:id/status', auth(['vendor', 'rider', 'admin']), orderController.updateOrderStatus);
router.delete('/:id', auth(['customer', 'admin']), orderController.cancelOrder);

module.exports = router;
