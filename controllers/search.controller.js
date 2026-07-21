const MenuItem = require('../models/MenuItem');
const Vendor = require('../models/Vendor');

// GET /api/search?q=biryani
exports.search = async (req, res) => {
  try {
    const query = req.query.q;
    if (!query) {
      return res.status(400).json({ message: 'Search query parameter q is required.' });
    }

    const regex = new RegExp(query, 'i');

    // 1. Search Vendors
    const vendors = await Vendor.find({
      isActive: true,
      isApproved: true,
      $or: [{ name: regex }, { cuisine: regex }, { address: regex }]
    });

    // 2. Search Menu Items
    const foods = await MenuItem.find({
      isAvailable: true,
      $or: [{ name: regex }, { description: regex }, { category: regex }, { tags: { $in: [regex] } }]
    }).populate('vendor', 'name cuisine address rating');

    res.json({ vendors, foods });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// GET /api/foods/filter?calories=500&category=healthy&city=Vehari
exports.filterFoods = async (req, res) => {
  try {
    const { calories, category, city } = req.query;
    const foodQuery = { isAvailable: true };

    // 1. Calorie Filter
    if (calories) {
      foodQuery.calories = { $lte: Number(calories) };
    }

    // 2. Category Filter
    if (category) {
      const catRegex = new RegExp(category, 'i');
      foodQuery.$or = [
        { category: catRegex },
        { tags: { $in: [category.toLowerCase()] } }
      ];
    }

    // 3. City/Vendor Filter
    if (city) {
      const cityRegex = new RegExp(city, 'i');
      const vendorsInCity = await Vendor.find({
        isActive: true,
        address: cityRegex
      }).select('_id');

      const vendorIds = vendorsInCity.map(v => v._id);
      foodQuery.vendor = { $in: vendorIds };
    }

    const foods = await MenuItem.find(foodQuery)
      .populate('vendor', 'name cuisine address rating');

    res.json(foods);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};
