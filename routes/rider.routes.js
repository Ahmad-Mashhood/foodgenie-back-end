const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const riderController = require('../controllers/rider.controller');

router.get('/:id', auth(['rider', 'admin']), riderController.getRiderById);
router.put('/:id', auth(['rider', 'admin']), riderController.updateRider);
router.patch('/:id/location', auth(['rider', 'admin']), riderController.updateRiderLocation);
router.get('/:id/deliveries', auth(['rider', 'admin']), riderController.getRiderDeliveries);
router.patch('/:id/availability', auth(['rider', 'admin']), riderController.updateRiderAvailability);

module.exports = router;
