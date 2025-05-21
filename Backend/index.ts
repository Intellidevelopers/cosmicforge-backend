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


  


  

  


     










  /*sendMail({receiver:'benagu477@gmail.com',subject:"Successfull Sign up.",emailData:{
            fullName:`Agwu Emmanuel Chijekwu`
        },template:"sign-up-success.ejs"}).then((e)=>{
          console.log(e)
        }).catch(err=>console.log(err))*/



 

 
   
 

   
 })
}).catch(err=>{
  console.log(err)
  process.exit()
})






 
