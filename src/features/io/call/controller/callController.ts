import mongoose from "mongoose";
import { AuthMiddlewareProps } from "../../../../middleware/userAuthenticationMiddleware";
import { TypedSocket } from "../../../../util/interface/TypedSocket";
import  Socket from 'socket.io';
import UserConnectionsModel from "../../model/UserConnections";
import CallModel from "../model/callModel";
import BookAppointmentModel from "../../../appointment/model/bookAppointmentModel";

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


         
        socket.on('call_ended',async(data:{remoteId:string})=>{
             const userToCallSocketID = await UserConnectionsModel.findOne({
          userId:data.remoteId
         })
      
         if(!userToCallSocketID){
          socket.emit('call-failed',{
            message:'failed to initialize call.',
            error:'invalid connectionId'
          })
      
          return 
         }
        
    socketIO.to(userToCallSocketID.connectionId!!).emit('on_call_ended',data)

      })

      


      socket.on('ringing',async(data:{remoteId:string})=>{
        const userToCallSocketID = await UserConnectionsModel.findOne({
     userId:data.remoteId
    })
 
    console.log('ring.........')
    if(!userToCallSocketID){
     socket.emit('call-failed',{
       message:'failed to initialize call.',
       error:'invalid connectionId'
     })
 
     return 
    }
   
socketIO.to(userToCallSocketID.connectionId!!).emit('ringing',data)

 })


      socket.on('connected',async(data:{remoteId:string})=>{
        const userToCallSocketID = await UserConnectionsModel.findOne({
     userId:data.remoteId
    })
 
    if(!userToCallSocketID){
     socket.emit('call-failed',{
       message:'failed to initialize call.',
       error:'invalid connectionId'
     })
 
     return 
    }
   
socketIO.to(userToCallSocketID.connectionId!!).emit('on_connected',data)

 })


 socket.on('request_to_switch_call_mode',async(data:{remoteId:string,callMode:string})=>{
 console.log('requesting call mode')
  const userToCallSocketID = await UserConnectionsModel.findOne({
userId:data.remoteId
})






if(!userToCallSocketID){
socket.emit('call-failed',{
 message:'failed to initialize call.',
 error:'invalid connectionId'
})

return 
}



socketIO.to(userToCallSocketID.connectionId!!).emit('request_to_switch_call_mode',data)




})




socket.on('accept_request_to_switch_call_mode',async(data:{remoteId:string,userAccepted:boolean,callMode:string})=>{
  const userToCallSocketID = await UserConnectionsModel.findOne({
userId:data.remoteId
})

console.log('accepting request')

if(!userToCallSocketID){
socket.emit('call-failed',{
 message:'failed to initialize call.',
 error:'invalid connectionId'
})

return 
}

socketIO.to(userToCallSocketID.connectionId!!).emit('accept_request_to_switch_call_mode',data)

})



socket.on('appointmentSessionStarted',async(data:{doctorID:string,patientID:string,startTime:string,caller:'patient'|'doctor'})=>{


  /* const appointmentID = await  BookAppointmentModel.findOne({
      patientID:data.patientID,
      medicalPersonelID:data.doctorID
     })*/

  const newAppointmentSession =  new CallModel({
   // appointmentId:appointmentID?._id,
    peers:[data.doctorID,data.patientID],
    session:{
      start:data.startTime,
      
    }
  })

 await newAppointmentSession.save()



 if(data.caller === 'doctor'){

 const userToCallSocketID = await UserConnectionsModel.findOne({
userId:data.patientID
})



if(!userToCallSocketID){
socket.emit('call-failed',{
 message:'failed to initialize call.',
 error:'invalid connectionId'
})

return 
}
socketIO.to(userToCallSocketID.connectionId!!).emit('sessionID',{
  sessionID:newAppointmentSession._id
 })

 socket.emit('sessionID',{
  sessionID:newAppointmentSession._id
 })


 }else{



  const userToCallSocketID = await UserConnectionsModel.findOne({
userId:data.doctorID
})



if(!userToCallSocketID){
socket.emit('call-failed',{
 message:'failed to initialize call.',
 error:'invalid connectionId'
})

return 
}
socketIO.to(userToCallSocketID.connectionId!!).emit('sessionID',{
  sessionID:newAppointmentSession._id
 })

 socket.emit('sessionID',{
  sessionID:newAppointmentSession._id
 })
  
 }
  

 





})


socket.on('appointmentSessionEnded',async(data:{doctorID:string,patientID:string,endTime:string,caller:'patient'|'doctor',sessionID:string,duration:string})=>{


  const appointmentID = await  BookAppointmentModel.findOne({
     patientID:data.patientID,
     medicalPersonelID:data.doctorID
    })

    await appointmentID?.updateOne({appointmentStatus:'completed'})

     
 const sessionData =await CallModel.findOne({
  _id:data.sessionID
 })

 if(sessionData){
  await sessionData.updateOne({
    session:{
      start:sessionData.session?.start,
      end:data.endTime,
      durationOfCall:data.duration
    }
   })
 }

})


}


const userCalling = async (socketIO:Socket.Server,socket:TypedSocket<AuthMiddlewareProps>,data:{userToCall:string, userCallingDetails:{
  name:string,
  profilePicture:string
},callMode:'audio' | 'video'}) =>{

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
    userCallingDetails:data.userCallingDetails,
  callMode:data.callMode
   })



}