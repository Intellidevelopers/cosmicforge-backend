import express from 'express';
import { registerNewAdmin, verifyAdminOTP, adminLogin, getAdmin } from '../controller/adminAuthController';
import { adminAuthMiddleware } from '../middleware/adminAuthMiddleware'; // Assuming you have an auth middleware
import { ResponseBodyProps } from '../../../util/interface/ResponseBodyProps';

const router = express.Router();

/**
 * Route for registering a new admin by sending an OTP.
 * - Body: { email, password }
 */
router.post('/register', registerNewAdmin);

/**
 * Route to verify the OTP sent to admin email for registration.
 * - Body: { email, otp }
 */
router.post('/verify-otp', verifyAdminOTP);

/**
 * Route for admin login.
 * - Body: { email, password }
 */
router.post('/login', adminLogin);


/**
 * Route to get the admin data 
 * 
 */

router.get('/adminDashboard',  adminAuthMiddleware, getAdmin);


export default router;
