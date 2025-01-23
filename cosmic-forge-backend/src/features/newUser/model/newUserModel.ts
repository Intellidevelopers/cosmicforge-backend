import mongoose, { model } from "mongoose";


 const UserSchema = new mongoose.Schema({
    fullName:{
        type:mongoose.SchemaTypes.String,
        required:[true,'fullName is needed to continue.'],
    },
    email:{
        type:mongoose.SchemaTypes.String,
        required:[true,'email is needed to continue.'],
        unique:[true,'email must be unoque'],
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
        validate:{
            validator:(value:string)=>{
                const strongPasswordPattern = /^(?=.*[A-Za-z])(?=.*[A-Z a-z\d ])(?=.*[@$!*#?.&])[A-Za-z\d@$!*.#?&]{10,}$/
               return strongPasswordPattern.test(value)
            }
        }
    }
 })


 export default model('users',UserSchema)