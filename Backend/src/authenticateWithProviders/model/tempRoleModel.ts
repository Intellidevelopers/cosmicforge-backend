
import mongoose from "mongoose";


const userTempRoleModelSchema = new mongoose.Schema({
    userRole:{
        type:mongoose.SchemaTypes.String
    }
})


 export const  userTempRoleModel =  mongoose.model('user-role-temp',userTempRoleModelSchema)