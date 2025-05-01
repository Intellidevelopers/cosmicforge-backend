import mongoose, { Schema, model } from "mongoose";

const AdminSchema = new Schema({
  email: {
    type: String,
    required: [true, 'Email is required.'],
    unique: [true, 'Email must be unique.'],
    validate: {
      validator: function (value: string) {
        const re = /^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@((([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})|(\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b))$/i;
        return re.test(value);
      },
      message: "Please enter a valid email."
    }
  },
  password: {
    type: String,
    required: [true, 'Password is required.'],
  },
  role: {
    type: String,
    default: 'admin',
    enum: ['admin'],
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

export default model('Admin', AdminSchema);
