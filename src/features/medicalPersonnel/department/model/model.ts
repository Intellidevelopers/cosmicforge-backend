import mongoose from "mongoose";


 const departmentSchema = new  mongoose.Schema({
    
    name:{
        type:mongoose.SchemaTypes.String
    },
    image:{
        type:mongoose.SchemaTypes.String
    },
    backgroundImage:{
        type:mongoose.SchemaTypes.String
    },
    bodyText:{
        type:mongoose.SchemaTypes.String
    },

    
 },{timestamps:true})


 const DoctorDepartmentModel =  mongoose.model('doctor-department',departmentSchema)

 export default DoctorDepartmentModel