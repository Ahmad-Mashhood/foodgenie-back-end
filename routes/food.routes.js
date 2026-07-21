const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const foodController = require('../controllers/food.controller');
const searchController = require('../controllers/search.controller');

// Public routes for food discovery
router.get('/', foodController.getAllFoods);
router.get('/filter', searchController.filterFoods);
router.get('/:id', foodController.getFoodById);
router.get('/category/:category', foodController.getFoodsByCategory);

// Vendor-only routes for menu management
router.post('/', auth(['vendor']), foodController.addFood);
router.put('/:id', auth(['vendor']), foodController.updateFood);
router.delete('/:id', auth(['vendor']), foodController.deleteFood);

module.exports = router;
