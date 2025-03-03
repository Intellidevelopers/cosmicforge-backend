
import mongoose from "mongoose";


const userTempRoleModelSchema = new mongoose.Schema({
    userRole:{
        type:mongoose.SchemaTypes.String
    },
    token:{
        type:mongoose.SchemaTypes.String
    },
    authType:{
        type:mongoose.SchemaTypes.String
    },

    userData:{
        type:{} 
    }
    
})


 export const  userTempRoleModel =  mongoose.model('user-role-temp',userTempRoleModelSchema)