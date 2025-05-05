const mongoose = require('mongoose');

const AdminModel = new mongoose.Schema(
    {
        email: {
            type: String,
            required: true,
            unique: true,
            trim: true,
            lowercase: true,
            match: [/^\S+@\S+\.\S+$/, 'Please use a valid email address'],
        },
        password: {
            type: String,
            required: true,
            minlength: 8,
            select: false, 
        },
        loginAttempts: {
            type: Number,
            default: 0,
            select: false,
        },
        lockUntil: {
            type: Date,
            select: false,
        },
        otp: {
            type: String,
            select: false, 
        },
        otpExpiry: {
            type: Date,
            select: false, 
        },
        role: {
            type: String,
            enum: ['admin', 'superadmin'],
            default: 'admin',
        },
        isActive: {
            type: Boolean,
            default: true, 
        },
    },
    { 
        timestamps: true 
    }
);

const Admin = mongoose.model('Admin', AdminModel);

module.exports = Admin;
