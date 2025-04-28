
import  service  from 'node-cron'
import BookAppointmentModel from '../features/appointment/model/bookAppointmentModel'
import { TypedSocket } from '../util/interface/TypedSocket'
import { AuthMiddlewareProps } from '../middleware/userAuthenticationMiddleware'
import  Socket from 'socket.io';
import UserConnectionsModel from '../features/io/model/UserConnections';


let appoinmentBackgroundService  =  async (socket:TypedSocket<AuthMiddlewareProps>,socketIO:Socket.Server) =>{

    service.schedule('* * * * *',async ()=>{

        console.log('calling every minute')
       
        const date = new Date()
         
         const monthNumber = date.getDate()
       
         const dayInWeek =  date.toLocaleString('en-Us',{
           weekday:'long'
         })
       
         const monthName = date.toLocaleString('en-Us',{
           month:'long'
         })
         const year = date.getFullYear()
       
       
         const customDateString = dayInWeek.concat(' ').concat(monthNumber.toString().concat(getDaySuffice(monthNumber))).concat(' ').concat(monthName).concat('  ').concat(year.toString())
       
         //console.log(customDateString)
       
        const appointmentForToday = await BookAppointmentModel.find({
           $and:[
            {
                appointmentDate:{$eq:customDateString}
            },
            {
              $or:[
                {
                    medicalPersonelID:socket.user?._id
                },
                {
                    patientID:socket.user?._id
                }
              ]
            }

           ]
        })
       

        const appointmentFor = await BookAppointmentModel.updateMany({
          $and:[
           {
               appointmentDate:{$eq:customDateString},
               createdAt:{$lt:Date.now()},
               appointmentStatus:{$ne:'cancelled'}
           },
           {
             $or:[
               {
                   medicalPersonelID:socket.user?._id
               },
               {
                   patientID:socket.user?._id
               }
             ]
           }

          ]
       },{
        appointmentStatus:'cancelled'
       })
      
      console.log('hdhhdh')
       console.log(appointmentFor)
        

        const socConnection = await UserConnectionsModel.findOne({userId:socket.user?._id})

        if(appointmentForToday && appointmentForToday.length>0 && socConnection){

          console.log(appointmentForToday)

              appointmentForToday.map(async(data)=>{
               const  time =  data.appointmentTime?.split('-')[0].charAt(0)
               const  secondTime =  data.appointmentTime?.split('-')[1].charAt(0)

               const currentHour = date.toLocaleTimeString('en-Us',{
                hour12:true
               }).split(':')[0]

               const currentMins = date.toLocaleTimeString('en-Us',{
                hour12:true
               }).split(':')[1]

               console.log( date.toLocaleTimeString('en-Us',{
                hour12:true
               }).split(':')[0])

                

                if(time ===  currentHour || secondTime === currentHour){
                    socket.emit('appointmentReminder',{
                        totalAppointmentsForToday:appointmentForToday.length
                    })



                   

                  /*  socketIO.to(socConnection.connectionId!!).emit('appointmentReminder',{
                        totalAppointmentsForToday:appointmentForToday.length
                    })*/


                }

              })
            
         /*socket.emit('appointmentReminder',{
                totalAppointmentsForToday:appointmentForToday.length
            })*/
        }


     
      

       
       // console.log(appointmentForToday)
       
       
       }).start()



       service.schedule('0 0 * * *',async ()=>{

        console.log('running by 12am')
        const date = new Date()
         
        const monthNumber = date.getDate()-1
      
        const dayInWeek =  date.toLocaleString('en-Us',{
          weekday:'long'
        })
      
        const monthName = date.toLocaleString('en-Us',{
          month:'long'
        })
        const year = date.getFullYear()
      
      
        const customDateString = dayInWeek.concat(' ').concat(monthNumber.toString().concat(getDaySuffice(monthNumber))).concat(' ').concat(monthName).concat('  ').concat(year.toString())
      
        //console.log(customDateString)
      
       const appointmentForYesterday = await BookAppointmentModel.find({
          $and:[
           {
               appointmentDate:{$eq:customDateString}
           },
           {
             $or:[
               {
                   medicalPersonelID:socket.user?._id
               },
               {
                   patientID:socket.user?._id
               }
             ]
           }

          ]
       })

       if(appointmentForYesterday){

        appointmentForYesterday.forEach(async appointment=>{

            if(appointment.appointmentStatus !== 'completed')
           await  appointment.updateOne({
                appointmentStatus:'cancelled'
           })
        })
       }
      
       }).start()

}





const getDaySuffice = (day: number) => {
    if (day >= 11 && day <= 13) {
        return 'th';
    }

    switch (day % 10) {
        case 1:
            return 'st';
        case 2:
            return 'nd';
        case 3:
            return 'rd';
        default:
            return 'th';
    }
};




export default appoinmentBackgroundService

