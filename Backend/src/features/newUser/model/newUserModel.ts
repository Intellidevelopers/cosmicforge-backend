import mongoose, { model } from "mongoose";

enum UserRoleProps {
    client,doctor,admin
}


 const UserSchema = new mongoose.Schema({
    fullName:{
        type:mongoose.SchemaTypes.String,
        required:[true,'fullName is needed to continue.'],
    },
    lastName:{
        type:mongoose.SchemaTypes.String,
        required:[true,'firstName is needed to continue.'],
    },
    email:{
        type:mongoose.SchemaTypes.String,
        required:[true,'email is needed to continue.'],
        unique:[true,'email must be unique'],
        validate: {
            validator: (value:string) => {
              const re = /^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@((([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})|(\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b))$/i;
              return value.match(re);
            },
            message: "Please enter a valid email"
          }
      
    },

    password:{
        type:mongoose.SchemaTypes.String,
        required:[true,'password is required.'],
       
        
    },

    role:{
        type:mongoose.SchemaTypes.String,
        required:[true,'user must have a role.'],
        enum:[UserRoleProps,'not a valid role assigned']
    }
 })


 export default model('users',UserSchema)