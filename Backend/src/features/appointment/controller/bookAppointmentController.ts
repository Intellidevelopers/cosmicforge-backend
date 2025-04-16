import mongoose from "mongoose";
import SERVER_STATUS from "../../../util/interface/CODE";
import { ResponseBodyProps } from "../../../util/interface/ResponseBodyProps";
import TypedRequest from "../../../util/interface/TypedRequest";
import TypedResponse from "../../../util/interface/TypedResponse";
import { USER_ROLES } from "../../../util/interface/UserRole";
import newUserModel from "../../newUser/model/newUserModel";
import BookAppointmentModel from "../model/bookAppointmentModel";
import PatientProfileModel from "../../patient/profile/model/patientProfileModel";
import MedicalPersonnelProfileModel from "../../medicalPersonnel/profile/model/profileModel";


 interface paymentProps {
     consultationFee:string,
     cardType:string
     cardFee:string
     vat:string
     total:string,
     paymentReference:string
 
 }

interface bookAppointmentProps {

    doctorId:string,
   date:string,
   time:string,
    appointmentType: string
    payment:paymentProps,
    appointmentStatus:string
}

export const bookAppointment = async (req:TypedRequest<bookAppointmentProps>,res:TypedResponse<ResponseBodyProps>) => {

  try {

    const user = req.user

    if(!user){
        res.status(SERVER_STATUS.Forbidden).json({
            title:"Book Appointment Message.",
            status:SERVER_STATUS.Forbidden,
            successful:false,
            message:"You are not authorized"
        })
        return
    }

    if(user.role !== USER_ROLES.CLIENT.toString()){

        res.status(SERVER_STATUS.UNAUTHORIZED).json({
            title:"Book Appointment Message.",
            status:SERVER_STATUS.UNAUTHORIZED,
            successful:false,
            message:"you are not authorized"
        })
        return
    }


    const {doctorId,date,time,appointmentType,payment,appointmentStatus} = req.body
     
      if(!doctorId || !date || !time||  !appointmentType){

        res.status(SERVER_STATUS.BAD_REQUEST).json({
            title:"Book Appointment Message.",
            status:SERVER_STATUS.BAD_REQUEST,
            successful:false,
            message:"doctorId,date,time and appointmentType fields are needed to continue."
        })
        return
      }


       const appointmentAlreadyBooked = await BookAppointmentModel.findOne({
         $and:[
            {
                medicalPersonelID:doctorId
            },
            {
                patientID:user._id
            },
            {
                appointmentDate:date
            },
            {
                appointmentTime:time
            }
        

         ]
       })

       if(appointmentAlreadyBooked){
       
         await  appointmentAlreadyBooked.updateOne({
            medicalPersonelID:doctorId,
            patientID:user._id,
            appointmentType:appointmentType,
            payment,
            appointmentDate:date,
            appointmentTime:time,
            appointmentStatus:appointmentStatus
         })

         const appointment = await BookAppointmentModel.findOne({
            $and:[
               {
                   medicalPersonelID:doctorId
               },
               {
                   patientID:user._id
               },
               {
                   appointmentStatus
               },
               {
                   appointmentDate:date
               },
               {
                   appointmentTime:time
               }
           
   
            ]
          })

         res.status(SERVER_STATUS.SUCCESS).json({
            title:"Book Appointment Message.",
            status:SERVER_STATUS.SUCCESS,
            successful:true,
            message:"Successfully".concat(" ").concat(appointmentStatus ?? 'booked').concat(" ").concat("appoinment."),
            data:appointment
        
        }) 

        return
       }

       const isPaymentObjectEmpty = Object.entries(payment).every(([key,value])=>{
            if(payment['consultationFee']=== ''){
                return true
            }

            if(payment['total']=== ''){
                return true
            }


       })

       if(isPaymentObjectEmpty){
        res.status(SERVER_STATUS.BAD_REQUEST).json({
            title:"Book Appointment Message.",
            status:SERVER_STATUS.BAD_REQUEST,
            successful:false,
            message:"Atleast consultationFee and total is needed to continue."
        })
        return


       }

      const isDoctorIdValid = mongoose.Types.ObjectId.isValid(doctorId)

      if(!isDoctorIdValid){
        res.status(SERVER_STATUS.BAD_REQUEST).json({
            title:"Book Appointment Message.",
            status:SERVER_STATUS.BAD_REQUEST,
            successful:false,
            message:"Invalid id provided."
        })
        return
      }

      const isDoctorRegistered = await newUserModel.findOne({_id:user._id})

      const patientProfileID =  await PatientProfileModel.findOne({
        userId:user._id
      })
      const doctorProfileID = await MedicalPersonnelProfileModel.findOne({
        userId:doctorId
      })

      if(!isDoctorRegistered){
        res.status(SERVER_STATUS.BAD_REQUEST).json({
            title:"Book Appointment Message.",
            status:SERVER_STATUS.BAD_REQUEST,
            successful:false,
            message:"Invalid id provided."
        })
        return
      }


      

      const newAppointment = new  BookAppointmentModel({
        medicalPersonelID:doctorId,
        patientID:user._id,
        appointmentType:appointmentType,
        payment,
        appointmentDate:date,
        appointmentTime:time,
        appointmentStatus:appointmentStatus ?? 'booked',
        patientDetails:patientProfileID,
        medicalPersonelDetails:doctorProfileID

      })

      await newAppointment.save()

     
      
      res.status(SERVER_STATUS.SUCCESS).json({
        title:"Book Appointment Message.",
        status:SERVER_STATUS.SUCCESS,
        successful:true,
        message:"Successfully booked appointment.",
        data:newAppointment.toObject()
    
    }) 
    
  } catch (error:any) {
    res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
        title:"Book Appointment Message.",
        status:SERVER_STATUS.INTERNAL_SERVER_ERROR,
        successful:false,
        message:"Internal Server Error.",
        error:error.message
    }) 
  }

         



}


export const getSpecificDoctorAppointments = async (req:TypedRequest<any>,res:TypedResponse<ResponseBodyProps>) =>{

   try {

    const user = req.user

    if(!user){
        res.status(SERVER_STATUS.Forbidden).json({
            title:"Book Appointment Message.",
            status:SERVER_STATUS.Forbidden,
            successful:false,
            message:"You are not authorized"
        })
        return
    }

    if(user.role === USER_ROLES.DOCTOR.toString()){

        const appointments = await BookAppointmentModel.find({medicalPersonelID:user._id}).sort('createdAt').populate([{path:'patientDetails',select:""},{path:'patientID',select:'fullName lastName'}])


        res.status(SERVER_STATUS.SUCCESS).json({
            title:"Book Appointment Message.",
            status:SERVER_STATUS.SUCCESS,
            successful:true,
            message:"Successfully fetched.",
            data:{
                totalAppointments:appointments.length,
                appointments
            }
        })
        return
    }

    const appointments = await BookAppointmentModel.find({patientID:user._id}).sort('-1').populate([{path:'medicalPersonelDetails',select:""},{path:'medicalPersonelID',select:'fullName lastName'}])


    res.status(SERVER_STATUS.SUCCESS).json({
        title:"Book Appointment Message.",
        status:SERVER_STATUS.SUCCESS,
        successful:true,
        message:"Successfully fetched.",
        data:{
            totalAppointments:appointments.length,
            appointments
        }
    })

   

    
   



    
   } catch (error:any) {

    res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
        title:"Book Appointment Message.",
        status:SERVER_STATUS.INTERNAL_SERVER_ERROR,
        successful:false,
        message:"Internal Server Error.",
        error:error.message
    }) 

   } 

}

