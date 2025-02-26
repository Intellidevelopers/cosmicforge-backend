"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
const mongoose_1 = __importStar(require("mongoose"));
var UserRoleProps;
(function (UserRoleProps) {
    UserRoleProps[UserRoleProps["client"] = 0] = "client";
    UserRoleProps[UserRoleProps["doctor"] = 1] = "doctor";
    UserRoleProps[UserRoleProps["admin"] = 2] = "admin";
})(UserRoleProps || (UserRoleProps = {}));
const UserSchema = new mongoose_1.default.Schema({
    fullName: {
        type: mongoose_1.default.SchemaTypes.String,
        required: [true, 'fullName is needed to continue.'],
    },
    lastName: {
        type: mongoose_1.default.SchemaTypes.String,
        required: [true, 'firstName is needed to continue.'],
    },
    email: {
        type: mongoose_1.default.SchemaTypes.String,
        required: [true, 'email is needed to continue.'],
        unique: [true, 'email must be unique'],
        validate: {
            validator: (value) => {
                const re = /^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@((([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})|(\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b))$/i;
                return value.match(re);
            },
            message: "Please enter a valid email"
        }
    },
    password: {
        type: mongoose_1.default.SchemaTypes.String,
        required: [true, 'password is required.'],
    },
    role: {
        type: mongoose_1.default.SchemaTypes.String,
        required: [true, 'user must have a role.'],
        enum: [UserRoleProps, 'not a valid role assigned']
    }
});
exports.default = (0, mongoose_1.model)('users', UserSchema);
