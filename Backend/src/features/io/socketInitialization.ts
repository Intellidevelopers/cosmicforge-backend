

import jwt from 'jsonwebtoken'
import { AuthMiddlewareProps } from "../../middleware/userAuthenticationMiddleware";
import  Socket from 'socket.io';
import { TypedSocket } from '../../util/interface/TypedSocket';
import newUserModel from '../newUser/model/newUserModel';
import UserConnectionsModel from './model/UserConnections';

export default  (socketIO:Socket.Server) =>{

    socketIO.use(async(socket:TypedSocket<AuthMiddlewareProps>,next)=>{
          const authorization:string =  socket.handshake.headers.authorization || socket.handshake.auth.token

          if(!authorization){
            next(Error('you are not authorized to continue.'))
            return
          }

        

          try {

            const token = authorization.split(" ")[1] ?? authorization
         
              const  validatedToken = jwt.verify(token,process.env?.JWT_SECRET!) as AuthMiddlewareProps
             
               const user = await newUserModel.findOne({_id:validatedToken._id})

               if(!user){
                next(Error('you are not authorized to continue.'))
                return
               }

               socket.user = validatedToken
               next()


          } catch (error:any) {
        
                next(Error(error.message))
               
          }



    }).on('connection',async(socket:TypedSocket<AuthMiddlewareProps>)=>{

      
    

       let userConnection =  await UserConnectionsModel.findOne({userId:socket.user?._id})

       if(!userConnection){
         
           userConnection =  new UserConnectionsModel({
            userId:socket.user?._id,
            connectionId:socket.id
           })

           await userConnection.save()

           socket.emit('message',JSON.stringify(userConnection))


           return

       }

      await userConnection.updateOne({
        connectionId:socket.id,


       },{
        new:true,
        returnDocument:'after'
       })

       userConnection = await UserConnectionsModel.findOne({userId:socket.user?._id})
      console.log('updating....')
      console.log(socket.id)
       socket.emit('message',JSON.stringify(userConnection))


    })

}