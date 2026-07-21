const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const authController = require('../controllers/auth.controller');

// Public routes
router.post('/register', authController.register);
router.post('/login', authController.login);

// Protected routes (available to any authenticated user/vendor/rider/admin)
router.get('/me', auth(['customer', 'vendor', 'rider', 'admin']), authController.me);
router.post('/logout', auth(['customer', 'vendor', 'rider', 'admin']), authController.logout);

module.exports = router;
