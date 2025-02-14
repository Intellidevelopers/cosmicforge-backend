import mongoose from "mongoose";
import SERVER_STATUS from "../../../util/interface/CODE";
import { ResponseBodyProps } from "../../../util/interface/ResponseBodyProps";
import TypedRequest from "../../../util/interface/TypedRequest";
import TypedResponse from "../../../util/interface/TypedResponse";
import { USER_ROLES } from "../../../util/interface/UserRole";
import newUserModel from "../../newUser/model/newUserModel";
import BookAppointmentModel from "../model/bookAppointmentModel";


 interface paymentProps {
     consultationFee:string,
     cardType:string
     cardFee:string
     vat:string
     total:string
 
 }

interface bookAppointmentProps {

    doctorId:string,
    day:string,
    month:string,
    year:string,
    meridianType: 'am' | 'pm'
    hour:string,
    minutes:string,
    appointmentType: string
    payment:paymentProps
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


    const {doctorId,day,month,year,meridianType,hour,minutes,appointmentType,payment} = req.body
     
      if(!doctorId || !day || !month || !month || !year || !meridianType || !hour || !minutes || !appointmentType){

        res.status(SERVER_STATUS.BAD_REQUEST).json({
            title:"Book Appointment Message.",
            status:SERVER_STATUS.BAD_REQUEST,
            successful:false,
            message:"doctorId,day,month,year,meridianType,hour,minutes and appointmentType fields are needed to continue."
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

      if(!isDoctorRegistered){
        res.status(SERVER_STATUS.BAD_REQUEST).json({
            title:"Book Appointment Message.",
            status:SERVER_STATUS.BAD_REQUEST,
            successful:false,
            message:"Invalid id provided."
        })
        return
      }


      let createCustomDate:Date | null = null

      if(meridianType === 'pm'){
      createCustomDate=  new Date(Number(year),Number(Number(month)-1),Number(day),Number(Number(hour)+12),Number(minutes),0,0)

      }else{
        createCustomDate=  new Date(Number(year),Number(Number(month)-1),Number(day),Number(hour),Number(minutes),0,0)

      }

      const newAppointment = new  BookAppointmentModel({
        medicalPersonelID:doctorId,
        patientID:user._id,
        appointmentType:appointmentType,
        appointmentDate:createCustomDate.getTime(),
        payment

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

    if(user.role !== USER_ROLES.DOCTOR.toString()){

        res.status(SERVER_STATUS.UNAUTHORIZED).json({
            title:"Book Appointment Message.",
            status:SERVER_STATUS.UNAUTHORIZED,
            successful:false,
            message:"you are not authorized"
        })
        return
    }

    
    const appointments = await BookAppointmentModel.find({medicalPersonelID:user._id}).sort('-1')


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

