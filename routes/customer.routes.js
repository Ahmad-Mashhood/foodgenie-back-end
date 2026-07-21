const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const customerController = require('../controllers/customer.controller');

router.get('/:id', auth(['customer', 'admin']), customerController.getCustomerById);
router.put('/:id', auth(['customer', 'admin']), customerController.updateCustomer);
router.patch('/:id/preferences', auth(['customer', 'admin']), customerController.updatePreferences);
router.get('/:id/orders', auth(['customer', 'admin']), customerController.getCustomerOrders);
router.get('/:id/favorites', auth(['customer', 'admin']), customerController.getCustomerFavorites);

module.exports = router;
