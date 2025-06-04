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
        type:mongoose.SchemaTypes.Number,
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


      paymentReference:{
        type:mongoose.SchemaTypes.String,
        required:[true,'needed to continue.']
      }
     
      
      






    





})




const BookAppointmentSchema = new mongoose.Schema({
    
    medicalPersonelID:{
        type:mongoose.SchemaTypes.ObjectId,
        ref:'users',
        required:[true,' medicalPersonelID is needed to continue.']
    },
    medicalPersonelDetails:{
        type:mongoose.SchemaTypes.ObjectId,
        ref:'medicalPersonnelProfile',
    },
    patientID:{
         type:mongoose.SchemaTypes.ObjectId,
        ref:'users',
        required:[true,' patientId is needed to continue.']
    },
    patientDetails:{
        type:mongoose.SchemaTypes.ObjectId,
        ref:'patientProfile',
    },

    appointmentDate:{
        type:mongoose.SchemaTypes.String
    },

    appointmentTime:{
        type:mongoose.SchemaTypes.String
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
    paymentStatus:{
      type:mongoose.SchemaTypes.String,
        enum:['pending','success','failed'],
        default:'pending'

      },
      sessionDuration:{
       type:mongoose.SchemaTypes.Number
      },
    createdAt:{
        type:mongoose.SchemaTypes.Date,
        default:Date.now()
    }
})


const BookAppointmentModel =  mongoose.model('bookAppointment',BookAppointmentSchema)

export default BookAppointmentModel