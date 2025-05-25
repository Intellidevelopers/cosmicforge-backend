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

import  * as faceApi from 'face-api.js'
import sendMail from './src/config/mail/nodeMailer'
import SubscriptionDtailsModel from './src/features/subscription/model/SubscriptionDtailsModel'

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
  
  app.use(
    cors({
      credentials: true,
      methods: ["GET", "POST", "PUT", "DELETE", "PATCH"],
      origin: allowedOrigins,
    })
);


app.use(express.json({limit:'50mb'}));
app.use(express.urlencoded({ extended: true,limit:'50mb' }));

app.use('/api/v1/cosmicforge/',mainRouter)





app.get('/',(req,res)=>{
  res.render(path.join(__dirname,'src','views','doctor-verification.ejs'),{
    data:{
      fullName:"Agwu Emmanuel",
      token:129099,
     urlForApproval:`${process.env.backend_base_url}/user/medics/certification/verification?token=kks`,
    urlForDisApproval:'kkk'
    }
  })
})

app.get('/hello',(req,res)=>{

  res.render(path.join(__dirname,'src','views','approvedLicenseTemplate.ejs'))
  

})



app.use(errorHandler)

const PORT = process.env.PORT || 3010
  

connectDB().then( res=>{

  server.listen(PORT,async()=>{

    
    console.log('on port 3010 h gg dgdg gg hhh')


  

    const data = [{
       name:"Free",
  
  
      message:" Suitable to all Subscribers",
  
  
      usdPrice:"00.00",
      price:"00.00",
      duration:"month",
      commission:"30",
      offers:["Access to 20 Patients per month.","Regular Profile Listing.","Access to 50 AI Responses.","Access to Chat only.","Access to Support."]



    },{
       name:"Basic",
  
  
      message:" Suitable to all Basic Plan Subscribers.",
  
  
      usdPrice:"50.00",
      price:"60,000.00",
      duration:"month",
      commission:"25",
      offers:["Access to 50 Patients per month.","Regular Profile Listing.","Access to 200 AI Responses.","Video Consultation and Chat.","Access to Standard Support."]



    },{
       name:"Professional",
  
  
      message:" Suitable to all Professional Plan Subscriber.",
  
  
      usdPrice:"80.00",
      price:"100,000.00",
      duration:"month",
      commission:"20",
      offers:["Access to 100 Patients per month.","Top Profile Listing.","Access to 400 AI Responses.","Video Consultation and Chat.","Access to Priority Support."]



    },
  {
       name:"Premium",
  
  
      message:" Suitable to all Premium Plan Subscribers.",
  
  
      usdPrice:"200.00",
      price:"200,000.00",
      duration:"month",
      commission:"15",
      offers:["Access to Unlimited Patients per month.","Top Profile Listing.","Access to  Unlimited AI Responses.","Video Consultation and Chat.","Access to Priority Support."]



    }]

  

 










  /*
sendMail({receiver:'benagu477@gmail.com',subject:"Successfull Sign up.",emailData:{
            fullName:`Agwu Emmanuel Chijekwu`
        },template:"sign-up-success.ejs"}).then((e)=>{
          console.log(e)
        }).catch(err=>console.log(err))*/



 

 
   
 

   
 })
}).catch(err=>{
  console.log(err)
  process.exit()
})






 
