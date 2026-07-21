const MenuItem = require('../models/MenuItem');

// GET /api/foods
exports.getAllFoods = async (req, res) => {
  try {
    const foods = await MenuItem.find({ isAvailable: true }).populate('vendor', 'name cuisine address rating');
    res.json(foods);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// GET /api/foods/:id
exports.getFoodById = async (req, res) => {
  try {
    const food = await MenuItem.findById(req.params.id).populate('vendor', 'name cuisine address rating');
    if (!food) return res.status(404).json({ message: 'Food item not found.' });
    res.json(food);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// GET /api/foods/category/:category
exports.getFoodsByCategory = async (req, res) => {
  try {
    const foods = await MenuItem.find({ category: req.params.category, isAvailable: true }).populate('vendor', 'name cuisine address rating');
    res.json(foods);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// POST /api/foods
exports.addFood = async (req, res) => {
  try {
    // Only vendors can add food
    if (req.user.role !== 'vendor') {
      return res.status(403).json({ message: 'Access denied. Vendor role required.' });
    }

    const food = await MenuItem.create({
      ...req.body,
      vendor: req.user.id
    });
    res.status(201).json(food);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// PUT /api/foods/:id
exports.updateFood = async (req, res) => {
  try {
    if (req.user.role !== 'vendor') {
      return res.status(403).json({ message: 'Access denied. Vendor role required.' });
    }

    // Ensure vendor owns the menu item
    const food = await MenuItem.findOneAndUpdate(
      { _id: req.params.id, vendor: req.user.id },
      req.body,
      { new: true }
    );

    if (!food) return res.status(404).json({ message: 'Food item not found or unauthorized.' });
    res.json(food);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// DELETE /api/foods/:id
exports.deleteFood = async (req, res) => {
  try {
    if (req.user.role !== 'vendor') {
      return res.status(403).json({ message: 'Access denied. Vendor role required.' });
    }

    const food = await MenuItem.findOneAndDelete({ _id: req.params.id, vendor: req.user.id });
    if (!food) return res.status(404).json({ message: 'Food item not found or unauthorized.' });

    res.json({ message: 'Food item deleted successfully.' });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};
