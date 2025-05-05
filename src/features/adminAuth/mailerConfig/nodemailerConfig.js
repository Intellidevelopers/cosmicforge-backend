const nodemailer = require('nodemailer');
const generateOtp = require('../util/otpGenerator');

const {
    adminRegistrationTemplate
} = require('../util/emailUtility');

// Nodemailer Transporter Setup
const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
        user: "adeagbojosiah1@gmail.com",
        pass: "bvvmpoeglluldhwj",
    },
});

// Helper function to send emails
const sendMail = async (to, subject, htmlContent) => {
    const mailOptions = {
        from: "Cosmicforge",
        to,
        subject,
        html: htmlContent,
    };

    try {
        await transporter.sendMail(mailOptions);
        console.log('Email sent successfully');
    } catch (error) {
        console.error('Error sending email:', error);
    }
};

// Mail Options for Admin Registration Email
const sendAdminRegistrationEmail = async (email, username) => {
    const mailOptions = {
        from: "Cosmicforge",
        to: email,
        subject: 'Admin Registration',
        html: adminRegistrationTemplate(username),
    };

    await sendMail(email, 'Admin Registration', adminRegistrationTemplate(username));
};


// Exporting all functions to be used in the controllers
module.exports = {
    sendAdminRegistrationEmail
};


