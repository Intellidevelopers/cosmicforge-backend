
import  service  from 'node-cron'
import BookAppointmentModel from '../features/appointment/model/bookAppointmentModel'
import { TypedSocket } from '../util/interface/TypedSocket'
import { AuthMiddlewareProps } from '../middleware/userAuthenticationMiddleware'
import  Socket from 'socket.io';
import UserConnectionsModel from '../features/io/model/UserConnections';
import { USER_ROLES } from '../util/interface/UserRole';


 const timeUtc = new Map<number, number>()

    timeUtc.set(1, 13)
    timeUtc.set(2, 14)
    timeUtc.set(3, 15)
    timeUtc.set(4, 16)
    timeUtc.set(5, 17)
    timeUtc.set(6, 18)
    timeUtc.set(7, 19)
    timeUtc.set(8, 20)
    timeUtc.set(9, 21)
    timeUtc.set(10, 22)
    timeUtc.set(11, 23)
    timeUtc.set(12, 24)



let appoinmentBackgroundService  =  async (socket:TypedSocket<AuthMiddlewareProps>,socketIO:Socket.Server) =>{

    service.schedule('* * * * *',async ()=>{

        
       
        const date = new Date()
         
         const monthNumber = date.getDate()
       
         const dayInWeek =  date.toLocaleString('en-Us',{
           weekday:'long'
         })
       
         const monthName = date.toLocaleString('en-Us',{
           month:'long'
         })
         const year = date.getFullYear()
       
       const  time = date.toLocaleTimeString('en-Us',{
        timeStyle:'short'
       })

       console.log(time.toLowerCase().replace(' ',''))

         const customDateString = dayInWeek.concat(' ').concat(monthNumber.toString().concat(getDaySuffice(monthNumber))).concat(' ').concat(monthName).concat('  ').concat(year.toString())
       
         console.log(customDateString)
       
        const appointmentForToday = await BookAppointmentModel.find({
           $and:[

            {
              appointmentDate: customDateString,
             
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


        console.log(appointmentForToday)


        if(appointmentForToday.length>0){
             if(socket.user?.role=== USER_ROLES.DOCTOR){
               
                socket.emit('appointmentReminder',{
                totalAppointmentsForToday:appointmentForToday.length,
                appointments:appointmentForToday
              
            })

              }
        }
       

        /*const appointmentFor = await BookAppointmentModel.updateMany({
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
       })*/
      
  
    //console.log(appointmentFor)
        

        /*const socConnection = await UserConnectionsModel.findOne({userId:socket.user?._id})

        if(appointmentForToday && appointmentForToday.length>0 && socConnection){

         

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
                    })


                }

              })
            
         /*socket.emit('appointmentReminder',{
                totalAppointmentsForToday:appointmentForToday.length
            })
        }*/


     
      

       
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


 const date = new Date();

  let validateDate = (appointmentmentTime: string, appointmentDate: string) => {

    const appoinmentStartTime = appointmentmentTime?.split("-")[0];

    const appoinmentEndTime = appointmentmentTime?.split("-")[1];

    const appoinmentDay = appointmentDate?.split(" ")[1].replace(/[a-z]/g, "");

    const appoinmentMonth = appointmentDate.split(" ")[2];

    const currentMonth = date.toLocaleDateString("en-Us", {
      month: "long",
    });


    const dayInWeek = date.toLocaleString("en-Us", {
      day: "numeric",
    });


     const startTimeMeridian =appoinmentStartTime.split(":")[1].replace(/[0-9]/g, '').toLowerCase()

      const endTimeMeridian =appoinmentEndTime.split(":")[1].replace(/[0-9]/g, '').toLowerCase()

      const startT = new Date()

startT.setHours(startTimeMeridian==='pm'?timeUtc.get(Number(appoinmentStartTime.split(':')[0]))!!:Number(appoinmentStartTime.split(':')[0]),Number(appoinmentStartTime.split(':')[1].replace(/[a-z A-Z]/g,'')),0,0)




const startE= new Date()



startE.setHours(endTimeMeridian==='pm'?timeUtc.get(Number(appoinmentStartTime.split(':')[0]))!!:Number(appoinmentEndTime.split(':')[0]),Number(appoinmentEndTime.split(':')[1].replace(/[a-z A-Z]/g,'')))
date.setSeconds(0)

console.log(startE.toISOString())
console.log(date.getTime()<=startE.getTime())
         
    return  dayInWeek === appoinmentDay   && currentMonth === appoinmentMonth &&  (date.getTime() >= startT.getTime() && date.getTime()<=startE.getTime()) 

     
  };


export default appoinmentBackgroundService

