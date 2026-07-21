const User = require('../models/User');
const MenuItem = require('../models/MenuItem');

// GET /api/recommendations/:customerId
exports.getRecommendations = async (req, res) => {
  try {
    const customer = await User.findOne({ _id: req.params.customerId, role: 'customer' });
    if (!customer) return res.status(404).json({ message: 'Customer not found.' });

    const prefs = customer.preferences || {};
    const query = { isAvailable: true };

    // Filter by calories if specified
    if (prefs.calories) {
      query.calories = { $lte: prefs.calories };
    }

    // Filter by diet and health goals matching tags
    const targetTags = [];
    if (prefs.diet) targetTags.push(prefs.diet.toLowerCase());
    if (prefs.healthGoals && prefs.healthGoals.length > 0) {
      prefs.healthGoals.forEach(g => targetTags.push(g.toLowerCase()));
    }

    if (targetTags.length > 0) {
      query.tags = { $in: targetTags };
    }

    let recommendations = await MenuItem.find(query)
      .populate('vendor', 'name rating cuisine address')
      .limit(10);

    // Fallback: If no recommendations matching preferences, return any available items
    if (recommendations.length === 0) {
      recommendations = await MenuItem.find({ isAvailable: true })
        .populate('vendor', 'name rating cuisine address')
        .limit(10);
    }

    res.json(recommendations);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// POST /api/recommendations/generate
// Body can contain { diet, calories, healthGoals }
exports.generateRecommendations = async (req, res) => {
  try {
    const { diet, calories, healthGoals } = req.body;
    const query = { isAvailable: true };

    if (calories) {
      query.calories = { $lte: Number(calories) };
    }

    const targetTags = [];
    if (diet) targetTags.push(diet.toLowerCase());
    if (healthGoals && Array.isArray(healthGoals)) {
      healthGoals.forEach(g => targetTags.push(g.toLowerCase()));
    }

    if (targetTags.length > 0) {
      query.tags = { $in: targetTags };
    }

    const recommendations = await MenuItem.find(query)
      .populate('vendor', 'name rating cuisine address')
      .limit(10);

    res.json(recommendations);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};
