import mongoose from 'mongoose'


const  paymentSchema =  new  mongoose.Schema({

     
     
    consultationFee:{
       type:mongoose.SchemaTypes.String,
    },

    cardType:{
       type:mongoose.SchemaTypes.String,
       enum:['individual','family']
    },

    cardFee:{
        type:mongoose.SchemaTypes.BigInt,
        default:0,
        min:[0,'can not be less than 0']
     },

     vat: {
      type:mongoose.SchemaTypes.Number,  
       default:0,
       min:[0,'can not be less than 0']
     },

     total:{
        type:mongoose.SchemaTypes.Number,  
        default:0,
       min:[0,'can not be less than 0']

     },

      paymentStatus:{

        type:mongoose.SchemaTypes.String,
        enum:['pending','success','failed'],
        default:'pending'

      }






    





})




const BookAppointmentSchema = new mongoose.Schema({
    
    medicalPersonelID:{
        type:mongoose.SchemaTypes.ObjectId,
        ref:'medicalPersonnelProfile',
        required:[true,' medicalPersonelID is needed to continue.']
    },
    patientID:{
         type:mongoose.SchemaTypes.ObjectId,
        ref:'patientProfile',
        required:[true,' medicalPersonelID is needed to continue.']
    },

    appointmentDate:{
        type:mongoose.SchemaTypes.Date
    },

    appointmentType:{
        type:mongoose.SchemaTypes.String,
        enum:['Virtual','In-Person']
    },

    payment:paymentSchema,

    appointmentStatus:{
        type:mongoose.SchemaTypes.String,
        enum:['booked','cancelled','resheduled','completed'],
        default:'booked'
    },

    createdAt:{
        type:mongoose.SchemaTypes.Date,
    }
})


const BookAppointmentModel =  mongoose.model('bookAppointment',BookAppointmentSchema)

export default BookAppointmentModel