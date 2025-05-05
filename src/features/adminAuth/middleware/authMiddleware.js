const JWT = require('jsonwebtoken');
const Admin = require('../model/AdminModel');

const protectAdmin = async (req, res, next) => {

    let token = req.headers.authorization;
    
    if (!token || !token.startsWith('Bearer ')) {
        return res.status(401).json({ message: 'Unauthorized access. No token provided.' });
    }

    token = token.split(' ')[1]; 
    
    try {

        const decoded = JWT.verify(token, process.env.JWT_SECRET);
        
        const admin = await Admin.findById(decoded.adminId).select('-password');

        if (!admin) {
            return res.status(404).json({ message: 'Admin not found.' });
        }
       
        if (admin.role !== 'admin' && admin.role !== 'superadmin') {
            return res.status(403).json({ message: 'You are not authorized to access this resource.' });
        }

        req.admin = admin;

        next();
    } catch (error) {
        console.error(error);
        return res.status(401).json({ message: 'Invalid or expired token.' });
    }
};


module.exports = { protectAdmin };