const bcrypt = require('bcryptjs');
const Admin = require('../model/AdminModel');
const jwt = require('jsonwebtoken');
const  generateOtp  = require('../util/otpGenerator');
const {
    sendAdminRegistrationEmail
} = require('../mailerConfig/nodemailerConfig');
const generateJWT = (adminId, role) => {
    return jwt.sign({ adminId, role }, process.env.JWT_SECRET, { expiresIn: '1d' });
};

// function to handle otp verification 
const isAccountLocked = (admin) => {
    if (admin.lockUntil && admin.lockUntil > Date.now()) {
        return true;
    }
    return false;
}


const registerAdmin = async (req, res) => {

    const { email, password} = req.body;

    try {

        const existingAdmin = await Admin.findOne({ email });

        if (existingAdmin) {
            return res.status(400).json({
                message: "Admin already exists",
                success: false
            });
        }

        const hashedPassword = await bcrypt.hash(password, 10);
        const otp = generateOtp();
        const otpExpiry = Date.now() + 10 * 60 * 1000;

        const newAdmin = new Admin({
            email,
            password: hashedPassword,
            otp,
            otpExpiry,
            verified: false
        });

        await newAdmin.save();

        await sendAdminRegistrationEmail(email, otp);

        res.status(200).json({
            message: 'Admin registration successful. OTP has been sent to your email for verification.',
        });

    } catch(error) {
        console.error(error);
        res.status(500).json({
            message: "Error during admin registration",
            success: false
        })
    }
}


const verifyOTP = async (req, res) => {
    const { email, otp } = req.body;

    try {
        const admin = await Admin.findOne({ email }).select('+otp +otpExpiry');
        if (!admin) {
            return res.status(400).json({
                message: "Admin not found",
                success: false
            });
        }

        if (admin.otpExpiry < Date.now()) {
            return res.status(400).json({
                message: "Invalid or expired OTP provided",
                success: false
            });
        }
        if (admin.otp !== otp) {
            return res.status(400).json({
                message: "Invalid OTP provided",
                success: false
            });
        }

        admin.isActive = true;
        admin.otp = undefined;
        admin.otpExpiry = undefined;
        await admin.save();

        res.status(200).json({
            message: "Admin Activated successfully. Pls proceed to login",
            success: true
        });

    } catch(error) {
        console.error(error);
        res.status(500).json({
            message: "Error verifying OTP! pls try again"
        })
    }
}

const loginAdmin = async (req, res) => {
    const { email, password } = req.body;

    try {

        const admin = await Admin.findOne({ email }).select("+password +loginAttempts +lockUntil");
        if (!admin) return res.status(400).json({
            message: "Invalid credentials",
            success: false
        });

        if (isAccountLocked (admin)) {
            return res.status(403).json({
                message: "Account is locked due to multiple failed login attempts! Pls try again later"
            });
        }

        const isMatch = await bcrypt.compare(password, admin.password);
        
        if (!isMatch) {
            admin.loginAttempts += 1;
            if (admin.loginAttempts >= 5) {
                admin.lockUntil = Date.now() + 15 * 60 * 1000;
            }

            await admin.save();
            return res.status(400).json({
                message: "Invalid credentials provided",
                success: false
            });
        }

        admin.loginAttempts = 0;
        admin.lockUntil = undefined;
        await admin.save();

        const token = generateJWT(admin._id, admin.role);

        res.status(200).json({
            message: "Login successful",
            success: true,
            data: token
        });

    } catch (error) {
        console.error(error);
        res.status(500).json({
            message: "Error during Admin login! pls try again",
            success: false
        });
    }
}

const getAdminDashboard = async (req, res) => {
    res.status(200).json({
        message: "Welcome to the Admin dashboard",
        admin: req.admin
    });
};

module.exports = {
    registerAdmin,
    verifyOTP,
    loginAdmin,
    getAdminDashboard
}

