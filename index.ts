 import express  from 'express'
 import dotenv from "dotenv"
 import swaggerUI from 'swagger-ui-express'
 import http  from 'http'
 import socketIo from 'socket.io'
 import jwt  from 'jsonwebtoken'
 import socketInitialization from './src/features/io/socketInitialization'
import file from 'fs'

import path from 'path'
import uploadImage  from './src/config/cloudinary/cloudinary'
import swaggersetup from './src/config/api-docummentation/swaggersetup'
import { connectDB } from './src/config/database/databaseConfig'

import cors from 'cors'
import mainRouter from './src/routes/routes'
import { errorHandler } from './src/middleware/errorHandlerMiddleware'
import { withdrawBallance } from './src/features/wallet/controller/walletController'
import SubscriptionDtailsModel from './src/features/subscription/model/SubscriptionDtailsModel'
// import adminRoute from './src/features/adminAuth/routes/adminRoute'
// const adminRoute = require('./src/features/adminAuth/routes/adminRoute');


 dotenv.config()


 const app = express()

 const server = http.createServer(app)

 

 const io = new socketIo.Server(server,{
  cors:{
    origin:'*',
    methods:['GET','POST']
  }

 })

 socketInitialization(io)

 app.use('/api-docs',swaggerUI.serve,swaggerUI.setup(swaggersetup))

app.set("view engine",'ejs')
app.set('views','./src/views')
 app.use(cors())
const allowedOrigins = [
    "http://127.0.0.1:5500",
    "https://www.cfhealthnet.com",
    "http://localhost:5173",
    "https://api.paystack.co"
  ];
  
  /*app.use(
    cors({
      credentials: true,
      methods: ["GET", "POST", "PUT", "DELETE", "PATCH"],
      origin: allowedOrigins,
    })
);*/

app.use(express.json({limit:'50mb'}));
app.use(express.urlencoded({ extended: true,limit:'50mb' }));

app.use('/api/v1/cosmicforge/',mainRouter)
// app.use('/api/v1/cosmicforge/admin',adminRoute)

// https://cosmicforge-backend.onrender.com/api/v1/cosmicforge/




app.get('/',(req,res)=>{
  res.render(path.join(__dirname,'src','views','reset-password.ejs'),{
    data:{
      fullName:"Agwu Emmanuel",
      token:129099
    }
  })
})

app.use(errorHandler)

const PORT = process.env.PORT || 3010
connectDB().then( res=>{
  server.listen(PORT,async()=>{
    console.log(`Server connected successfully on http://localhost:${PORT}`);

    interface  AuthMiddlewareProps{
      _id:string
      fullName: string,
      lastName: string,
      password: string,
      role:string
  }




   const doctorPlans = [
   
    {
        name:'Free',
        message:'Suitable to all Subscribers',
        price:'0.00',
        duration:'month',
        commission:30,
        offers:[
            'Access to 20 Patients per month',
            'Regular Profile Listing',
            'Access to 50 AI Responses.',
            'Access to chat only',
            'Access to Support'
        ]
    },
    {
        name:'Basic',
        message:'Suitable to all Basic Plan Subscribers',
        price:'16,000',
        duration:'month',
        commission:25,
        offers:[
            'Access to 50 Patients per month.',
            'Regular Profile Listing.',
            'Access to 200 AI Responses.',
            'Video Consultation and Chat.',
            'Access to Standard support.'
        ]
    },

    {
        name:'Professional',
        message:'Suitable to all Professional Plan Subscribers',
        price:'100,000',
        duration:'month',
        active:false,
        commission:20,
        offers:[
            'Access to 100 Patients per month.',
            'Top Profile Listing.',
            'Access to 400 AI Responses.',
            'Video Consultation and Chat.',
            'Access to Priority Support.'
        ]
    },

    {
        name:'Premium',
        message:'Suitable to all Premium Subscribers',
        price:'200,000',
        duration:'month',
        commission:15,
        offers:[
            'Access to Unlimited Patients per month.',
            'Top Profile Listing.',
            'Access to Unlimited AI Responses.',
            'Video Consultation and Chat.',
            'Access to Priority Support.',
           
        ]
    },
]



const patientPlans = [

  {
      name:'Free',
      message:'Suitable to all  Subscribers',
      price:'0.00',
      duration:'month',
      active:false,
      commission:undefined,
      offers:[
          'Access to Chat only.',
          'Access to 10 AI Chatbot Responses.',
          'Access to General & Emergency Specialist only.',
          'Access to Shop/Purchase',
          'Access to Support'
      ]
  },
  {
      name:'Basic',
      message:'Suitable to all Basic Plan Subscribers',
      price:'16,000',
      duration:'month',
      active:false,
      commission:undefined,
      offers:[
          'Video Consultations and chat.',
          'Access 50 AI Chatbot Responses.',
          'Access 20 AI Diagnostic Requests.',
          'Access to all Department Specialist.',
          'Access to Shop/Purchase.',
          'Suitable for Individual accounts only.',
          'Access to Standard support.'
      ]
  },
  {
      name:'Medium',
      message:'Subscrie to all Medium Subscribers',
      price:'30,000',
      duration:'year',
      active:true,
      commission:undefined,
      offers:[
          'Video Consultation and chat.',
          'Access to 100 AI Chatbot Response.',
          'Access to 50 AI Chatbot Requests.',
          'Access to all Department Specialist.',
          'Access to Shop/Purchase.',
          'Access to First Aid Assistance.',
          'Access to Standard Support.'
      ]
  },
  {
      name:'Premium',
      message:'Subscrie to Premium Subscribers',
      price:'60,000',
      duration:'month',
      active:false,
      commission:undefined,
      offers:[
          'Video Consultation and chat.',
          'Access to unlimited AI Chatbot Response.',
          'Access to unlimited Chatbot Requests.',
          'Access to all Department Specialist.',
          'Access to Shop/Purchase.',
          'Access to First Aid Assistance.',
          'Access to Standard Support.'
      ]
  },

  
]












 

 
   
 

   
 })
}).catch(err=>{
  console.log(err)
  process.exit()
})






 
