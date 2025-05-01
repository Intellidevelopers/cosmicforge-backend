import SERVER_STATUS from '../../../util/interface/CODE';
import { ResponseBodyProps } from '../../../util/interface/ResponseBodyProps';
import TypedRequest from '../../../util/interface/TypedRequest';
import TypedResponse from '../../../util/interface/TypedResponse';
import AdminModel from '../model/adminModel';
import OTPModel from '../model/adminOtpModel';
import generateOTP from '../../../util/otpGenerator';
import sendMail from '../../../config/mail/nodeMailer';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';

// Request payload interfaces
export interface AdminRegistrationRequest {
  email: string;
  password: string;
}

export interface ValidateAdminOTPRequest {
  email: string;
  otp: number;
}

export interface AdminLoginRequest {
  email: string;
  password: string;
}

export interface RequestBodyProps {} // Empty body expected for GET


/**
 * Registers a new admin by sending an OTP for verification.
 */
export const registerNewAdmin = async (
    req: TypedRequest<AdminRegistrationRequest>,
    res: TypedResponse<ResponseBodyProps>
  ) => {
    try {
      const { email, password } = req.body;
  
      if (!email || !password) {
        return res.status(SERVER_STATUS.BAD_REQUEST).json({
          title: 'Register Admin',
          status: SERVER_STATUS.BAD_REQUEST,
          successful: false,
          message: 'Email and password fields are required.',
        });
      }
  
      const existingAdmin = await AdminModel.findOne({ email });
  
      if (existingAdmin) {
        return res.status(SERVER_STATUS.BAD_REQUEST).json({
          title: 'Register Admin',
          status: SERVER_STATUS.BAD_REQUEST,
          successful: false,
          message: 'This email is already registered as admin.',
        });
      }
  
      const existingOTP = await OTPModel.findOne({
        'adminDetails.email': email,
      });
  
      if (existingOTP) {
        return res.status(SERVER_STATUS.BAD_REQUEST).json({
          title: 'Register Admin',
          status: SERVER_STATUS.BAD_REQUEST,
          successful: false,
          message: 'OTP already sent. Please verify or wait for expiration.',
        });
      }
  
      // Generate OTP and save it
      const otp = await generateOTP();
      const hashedPassword = await bcrypt.hash(password, 10);
      const otpEntry = new OTPModel({
        adminDetails: { email },
        otpCode: otp,
        hashedPassword,
        expiringTime: new Date(Date.now() + 5 * 60 * 1000), // 5 min expiry
      });
  
      await otpEntry.save();
  
      // Send OTP to admin email
      await sendMail({
        receiver: email,
        subject: 'Admin Registration OTP',
        emailData: { email, otp },
        template: 'send-admin-otp.ejs',
      });
  
      return res.status(SERVER_STATUS.SUCCESS).json({
        title: 'Register Admin',
        successful: true,
        status: SERVER_STATUS.SUCCESS,
        message: 'OTP sent to admin email.',
      });
    } catch (error: any) {
      return res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
        title: 'Register Admin',
        successful: false,
        status: SERVER_STATUS.INTERNAL_SERVER_ERROR,
        message: 'An error occurred during admin registration.',
        error: error.message,
      });
    }
  };

/**
 * Verifies OTP sent to admin email for registration.
 */
/**
 * Verifies OTP sent to admin email for registration.
 */
export const verifyAdminOTP = async (
    req: TypedRequest<ValidateAdminOTPRequest>,
    res: TypedResponse<ResponseBodyProps>
  ) => {
    try {
      const { email, otp } = req.body;
  
      if (!email || !otp) {
        return res.status(SERVER_STATUS.BAD_REQUEST).json({
          title: 'Verify Admin OTP',
          status: SERVER_STATUS.BAD_REQUEST,
          successful: false,
          message: 'Email and OTP are required.',
        });
      }
  
      const existingOTP = await OTPModel.findOne({ 'adminDetails.email': email });
  
      if (!existingOTP) {
        return res.status(SERVER_STATUS.BAD_REQUEST).json({
          title: 'Verify Admin OTP',
          status: SERVER_STATUS.BAD_REQUEST,
          successful: false,
          message: 'No OTP found for this email. Please register again.',
        });
      }
  
      if (existingOTP.otpCode !== otp) {
        return res.status(SERVER_STATUS.UNAUTHORIZED).json({
          title: 'Verify Admin OTP',
          status: SERVER_STATUS.UNAUTHORIZED,
          successful: false,
          message: 'Invalid OTP code.',
        });
      }
  
      if (new Date(existingOTP.expiringTime).getTime() < Date.now()) {
        await OTPModel.deleteOne({ _id: existingOTP._id }); // Clean up expired OTP
        return res.status(SERVER_STATUS.UNAUTHORIZED).json({
          title: 'Verify Admin OTP',
          status: SERVER_STATUS.UNAUTHORIZED,
          successful: false,
          message: 'OTP has expired. Please request a new one.',
        });
      }
  
      // Create new admin
      const newAdmin = new AdminModel({
        email,
        password: existingOTP.hashedPassword,
        role: 'admin',
      });
  
      await newAdmin.save();
      await OTPModel.deleteOne({ _id: existingOTP._id });
  
      return res.status(SERVER_STATUS.SUCCESS).json({
        title: 'Verify Admin OTP',
        status: SERVER_STATUS.SUCCESS,
        successful: true,
        message: 'OTP verified successfully. Admin registration complete.',
      });
    } catch (error: any) {
      return res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
        title: 'Verify Admin OTP',
        status: SERVER_STATUS.INTERNAL_SERVER_ERROR,
        successful: false,
        message: 'An error occurred during OTP verification.',
        error: error.message,
      });
    }
  };
  

/**
 * Logs in an admin and returns a JWT token with admin data.
 */
export const adminLogin = async (
  req: TypedRequest<AdminLoginRequest>,
  res: TypedResponse<ResponseBodyProps>
) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(SERVER_STATUS.BAD_REQUEST).json({
        title: 'Validation Error',
        status: SERVER_STATUS.BAD_REQUEST,
        successful: false,
        message: 'Email and password are required.',
      });
    }

    // Check if admin exists
    const admin = await AdminModel.findOne({ email });
    if (!admin || admin.role !== 'admin') {
      return res.status(SERVER_STATUS.UNAUTHORIZED).json({
        title: 'Authentication Error',
        status: SERVER_STATUS.UNAUTHORIZED,
        successful: false,
        message: 'Invalid email or not authorized.',
      });
    }

    // Compare password
    const isPasswordMatch = await bcrypt.compare(password, admin.password);
    if (!isPasswordMatch) {
      return res.status(SERVER_STATUS.UNAUTHORIZED).json({
        title: 'Authentication Error',
        status: SERVER_STATUS.UNAUTHORIZED,
        successful: false,
        message: 'Invalid password.',
      });
    }

    // Generate token for 15 mins
    const token = jwt.sign(
      {
        _id: admin._id,
        email: admin.email,
        role: admin.role,
      },
      process.env.JWT_SECRET!,
      { expiresIn: '15m' }
    );

    return res.status(SERVER_STATUS.SUCCESS).json({
      title: 'Login Successful',
      status: SERVER_STATUS.SUCCESS,
      successful: true,
      message: 'Admin login successful.',
      data: {
        token,
        admin: {
          _id: admin._id,
          email: admin.email,
          role: admin.role,
        },
      },
    });
  } catch (error: any) {
    return res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
      title: 'Login Failed',
      status: SERVER_STATUS.INTERNAL_SERVER_ERROR,
      successful: false,
      message: 'An error occurred during login.',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
};


export const getAdmin = async (req: TypedRequest<RequestBodyProps>, res: TypedResponse<ResponseBodyProps>) => {
    try {
      const user = res.locals.user; // User info attached from the middleware
  
      // Ensure the user exists
      if (!user) {
        return res.status(SERVER_STATUS.BAD_REQUEST).json({
          title: 'Get Admin Message',
          status: SERVER_STATUS.BAD_REQUEST,
          successful: false,
          message: 'No user found in the request.',
        });
      }
  
      // Ensure the user has admin role
      if (user.role !== 'admin') {
        return res.status(SERVER_STATUS.Forbidden).json({
          title: 'Get Admin Message',
          status: SERVER_STATUS.Forbidden,
          successful: false,
          message: 'Access denied: Admins only.',
        });
      }
  
      // Optionally, retrieve additional user data for the admin dashboard
      const adminData = {
        name: user.name,
        email: user.email,
        role: user.role,
        // Add other relevant user data as needed
      };
  
      // Return the admin data
      return res.status(SERVER_STATUS.SUCCESS).json({
        title: 'Get Admin Message',
        status: SERVER_STATUS.SUCCESS,
        successful: true,
        message: 'Admin information fetched successfully.',
        data: adminData, // Attach admin data to the response
      });
    } catch (error: any) {
      // Handle any errors
      return res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
        title: 'Get Admin Message',
        status: SERVER_STATUS.INTERNAL_SERVER_ERROR,
        successful: false,
        message: 'An error occurred while fetching admin data.',
        error: error.message,
      });
    }
  };