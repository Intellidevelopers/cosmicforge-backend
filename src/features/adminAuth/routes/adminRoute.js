const express = require('express');
const { registerAdmin, verifyOTP, loginAdmin, getAdminDashboard } = require('../controller/adminController');
const { protectAdmin } = require('../middleware/authMiddleware');
const router = express.Router();


router.post("/admin/register", registerAdmin);
router.post("/admin/verify-otp", verifyOTP);
router.post("/admin/login", loginAdmin);
router.get("/admin/dashboard", protectAdmin, getAdminDashboard);

module.exports = router;


