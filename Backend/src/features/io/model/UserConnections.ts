import mongoose from "mongoose";



const UserConnectionsSchema =  new   mongoose.Schema({

    userId:{
        type:mongoose.SchemaTypes.String
    },
    
    connectionId:{
        type:mongoose.SchemaTypes.String
    }


})


const UserConnectionsModel = mongoose.model('user-connections',UserConnectionsSchema)

export default UserConnectionsModel