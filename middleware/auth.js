const jwt  = require('jsonwebtoken');
require('dotenv').config();

/**
 * Role-based JWT authentication middleware.
 *
 * Usage:
 *   router.get('/protected', auth(['admin']), handler);
 *   router.get('/multi',     auth(['vendor', 'admin']), handler);
 *
 * @param {string[]} allowedRoles - Roles permitted to access the route.
 */
const auth = (allowedRoles = []) => {
  return (req, res, next) => {
    // 1. Extract token from Authorization header
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ message: 'No token provided.' });
    }

    const token = authHeader.split(' ')[1];

    // 2. Verify token
    let decoded;
    try {
      decoded = jwt.verify(token, process.env.JWT_SECRET || 'food_genie_secret');
    } catch (err) {
      return res.status(401).json({ message: 'Invalid or expired token.' });
    }

    // 3. Role check
    if (allowedRoles.length && !allowedRoles.includes(decoded.role)) {
      return res.status(403).json({ message: 'Access denied: insufficient permissions.' });
    }

    // 4. Attach user info and continue
    req.user = decoded;
    next();
  };
};

module.exports = auth;
