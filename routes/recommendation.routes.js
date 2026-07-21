const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const recommendationController = require('../controllers/recommendation.controller');

router.get('/:customerId', auth(['customer', 'admin']), recommendationController.getRecommendations);
router.post('/generate', auth(['customer', 'admin']), recommendationController.generateRecommendations);

module.exports = router;
