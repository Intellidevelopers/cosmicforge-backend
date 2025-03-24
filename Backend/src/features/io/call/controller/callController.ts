import mongoose from "mongoose";
import { AuthMiddlewareProps } from "../../../../middleware/userAuthenticationMiddleware";
import { TypedSocket } from "../../../../util/interface/TypedSocket";
import  Socket from 'socket.io';
import UserConnectionsModel from "../../model/UserConnections";

export const Call_USER =  (socketIO:Socket.Server,socket:TypedSocket<AuthMiddlewareProps>) =>{

      socket.on('calling',(d)=>{
        userCalling(socketIO,socket,d)
      })

      socket.on('create_answer', async(data:{ userToCall:string,
        userCalling:string,
        user_receiving_call_answer:RTCSessionDescription})=>{

          const userToCallSocketID = await UserConnectionsModel.findOne({
            userId:data.userCalling
           })
        
           if(!userToCallSocketID){
            socket.emit('call-failed',{
              message:'failed to initialize call.',
              error:'invalid connectionId'
            })
        
            return 
           }
      socketIO.to(userToCallSocketID.connectionId!!).emit('answer_received',data)
     // console.log(data)


      })



      socket.on('create_offer',async(data:{
        userToCall:string,
        userCalling:string,
        user_calling_offer:RTCSessionDescription
           })=>{

            const userToCallSocketID = await UserConnectionsModel.findOne({
              userId:data.userToCall
             })
          
             if(!userToCallSocketID){
              socket.emit('call-failed',{
                message:'failed to initialize call.',
                error:'invalid connectionId'
              })
          
              return 
             }
        socketIO.to(userToCallSocketID.connectionId!!).emit('offer_received',data)
        //console.log(data)
      })

      socket.on('local_ice_candidate',async(data:{
        userToCall:string,
        userCalling:string,
        user_calling_ice_canidate:RTCIceCandidate
           })=>{

        console.log('ice canditate')
        console.log(data)

        const userToCallSocketID = await UserConnectionsModel.findOne({
          userId:data.userToCall
         })
      
         if(!userToCallSocketID){
          socket.emit('call-failed',{
            message:'failed to initialize call.',
            error:'invalid connectionId'
          })
      
          return 
         }
    socketIO.to(userToCallSocketID.connectionId!!).emit('local_ice_candidate',data)

        
      })



      socket.on('remote_ice_candidate',async(data:{
        userToCall:string,
        userCalling:string,
        user_recieving_call_ice_candidate:RTCIceCandidate
           })=>{
        console.log('ice canditate remote')
        console.log(data)

         const userToCallSocketID = await UserConnectionsModel.findOne({
          userId:data.userCalling
         })
      
         if(!userToCallSocketID){
          socket.emit('call-failed',{
            message:'failed to initialize call.',
            error:'invalid connectionId'
          })
      
          return 
         }
    socketIO.to(userToCallSocketID.connectionId!!).emit('remote_ice_candidate',data)
      })


      socket.on('remote_answered_call',async(data:{remoteId:string,
        userCalling:string})=>{
          console.log('call answered..')
      console.log(data)
             const userToCallSocketID = await UserConnectionsModel.findOne({
          userId:data.userCalling
         })
      
         if(!userToCallSocketID){
          socket.emit('call-failed',{
            message:'failed to initialize call.',
            error:'invalid connectionId'
          })
      
          return 
         }
       
    socketIO.to(userToCallSocketID.connectionId!!).emit('remote_answered_call',data)

      })

      socket.on('failed_to_connect',async(data:{userId:string})=>{
             const userToCallSocketID = await UserConnectionsModel.findOne({
          userId:data.userId
         })
      
         if(!userToCallSocketID){
          socket.emit('call-failed',{
            message:'failed to initialize call.',
            error:'invalid connectionId'
          })
      
          return 
         }
        
    socketIO.to(userToCallSocketID.connectionId!!).emit('failed_to_connect',data)

      })


}


const userCalling = async (socketIO:Socket.Server,socket:TypedSocket<AuthMiddlewareProps>,data:{userToCall:string, userCallingDetails:{
  name:string,
  profilePicture:string
}}) =>{

   console.log('calling') 
console.log(data.userToCall)
   if(!data.userToCall){
    socket.emit('call-failed',{
      message:'failed to initialize call.',
      error:'invalid userToCall id'
    })
    return
   }
   const userToCallValidId = mongoose.Types.ObjectId.isValid(data.userToCall)

  

   if(!userToCallValidId){
    socket.emit('call-failed',{
      message:'failed to initialize call.',
      error:'invalid userToCall id'
    })
    return
   }



   const userToCallSocketID = await UserConnectionsModel.findOne({
    userId:data.userToCall,
    
   
   })

   if(!userToCallSocketID){
    socket.emit('call-failed',{
      message:'failed to initialize call.',
      error:'invalid connectionId'
    })

    return 
   }

   socketIO.to(userToCallSocketID?.connectionId!!).emit('incoming-call',{
    caller:socket.user,
    userCallingDetails:data.userCallingDetails
   })



}