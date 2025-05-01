import express from "express";
import SERVER_STATUS from "../../../util/interface/CODE";
import { Request, Response, NextFunction } from "express";
import jwt, { JwtPayload, TokenExpiredError, JsonWebTokenError } from "jsonwebtoken";
import adminModel from "../model/adminModel";
import { ResponseBodyProps } from "../../../util/interface/ResponseBodyProps";
import TypedRequest from "../../../util/interface/TypedRequest";
import TypedResponse from "../../../util/interface/TypedResponse";

// Define the payload structure expected in the admin JWT
interface AdminTokenPayload extends JwtPayload {
  _id: string;
  email: string;
  role: string;
}

export const adminAuthMiddleware = async (
  req: TypedRequest<{}>,
  res: TypedResponse<ResponseBodyProps>,
  next: NextFunction
) => {
  try {
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return res.status(SERVER_STATUS.UNAUTHORIZED).json({
        title: "Authentication Error",
        status: SERVER_STATUS.UNAUTHORIZED,
        successful: false,
        message: "Missing or malformed authorization header.",
      });
    }

    const token = authHeader.split(" ")[1];

    if (!token) {
      return res.status(SERVER_STATUS.BAD_REQUEST).json({
        title: "Authentication Error",
        status: SERVER_STATUS.BAD_REQUEST,
        successful: false,
        message: "Access token not provided.",
      });
    }

    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as AdminTokenPayload;

    if (!decoded || !decoded._id || decoded.role !== "admin") {
      return res.status(SERVER_STATUS.Forbidden).json({
        title: "Authorization Error",
        status: SERVER_STATUS.Forbidden,
        successful: false,
        message: "Admin access required. Access denied.",
      });
    }

    const admin = await adminModel.findById(decoded._id);

    if (!admin || admin.role !== "admin") {
      return res.status(SERVER_STATUS.Forbidden).json({
        title: "Authorization Error",
        status: SERVER_STATUS.Forbidden,
        successful: false,
        message: "Admin account not found or unauthorized.",
      });
    }

    // Attach admin user info to res.locals instead of req.user
    // Use res.local.user in any controller that belongs to the admin to gain access
    res.locals.user = {
      _id: admin._id.toString(),
      email: admin.email,
      role: admin.role,
    };

    next();
  } catch (error: any) {
    let status = SERVER_STATUS.INTERNAL_SERVER_ERROR;
    let message = "Failed to authenticate admin access.";

    if (error instanceof TokenExpiredError) {
      status = SERVER_STATUS.UNAUTHORIZED;
      message = "Session expired. Please log in again.";
    } else if (error instanceof JsonWebTokenError) {
      status = SERVER_STATUS.UNAUTHORIZED;
      message = "Invalid token. Please log in again.";
    }

    return res.status(status).json({
      title: "Authentication Error",
      status,
      successful: false,
      message,
      error: process.env.NODE_ENV === "development" ? error.message : undefined,
    });
  }
};

// export default adminAuthMiddleware;
