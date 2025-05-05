const adminRegistrationTemplate = (otp) => {
    return `
        <html>
        <head>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f9;
                    margin: 0;
                    padding: 0;
                }
                .email-container {
                    max-width: 600px;
                    margin: 20px auto;
                    padding: 20px;
                    background: #ffffff;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }
                .header {
                    text-align: center;
                    color: #FF5722;
                }
                .content {
                    padding: 10px 20px;
                    line-height: 1.6;
                    color: #333;
                }
                .otp {
                    font-size: 20px;
                    font-weight: bold;
                    text-align: center;
                    margin: 20px 0;
                    color: #FF5722;
                }
                .footer {
                    text-align: center;
                    font-size: 12px;
                    color: #aaa;
                }
            </style>
        </head>
        <body>
            <div class="email-container">
                <h3 class="header">Welcome to the Cosmicforge's Admin Team!</h3>
                <div class="content">
                    <p>Hi Admin</p>
                    <p>We’re excited to have you onboard as an administrator for Cosmicforge. Your account has been successfully created, granting you access to manage and oversee operations.</p>
                    <p>To finalize your account setup, please use the OTP below to verify your admin account. This OTP is valid for 10 minutes:</p>
                    <div class="otp">${otp}</div>
                    <p>If you encounter any issues during setup, feel free to contact our support team for assistance.</p>
                    <p>Thank you for joining us!</p>
                    <p>Best Regards,<br/>Cosmicforge Health Team</p>
                </div>
                <div class="footer">
                    <p>&copy; ${new Date().getFullYear()} Cosmicforge . All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
    `;
};


module.exports = {
    adminRegistrationTemplate
};








