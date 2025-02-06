 import express  from 'express'
 import dotenv from "dotenv"
 import swaggerUI from 'swagger-ui-express'
 
import file from 'fs'

import path from 'path'
import uploadImage  from './src/config/cloudinary/cloudinary'
import swaggersetup from './src/config/api-docummentation/swaggersetup'
import { connectDB } from './src/config/database/databaseConfig'

import cors from 'cors'
import mainRouter from './src/routes/routes'

 dotenv.config()


 const app = express()

 app.use('/api-docs',swaggerUI.serve,swaggerUI.setup(swaggersetup))

app.set("view engine",'ejs')
app.set('views','./src/views')
app.use(cors())
app.use(express.json({limit:'50mb'}));
app.use(express.urlencoded({ extended: true,limit:'50mb' }));

app.use('/api/v1/cosmicforge/',mainRouter)





app.get('/',(req,res)=>{
  res.render(path.join(__dirname,'src','views','reset-password.ejs'),{
    data:{
      fullName:"Agwu Emmanuel",
      token:129099
    }
  })
})

 import jwt  from 'jsonwebtoken'
const PORT = process.env.PORT || 3010
connectDB().then(res=>{
  app.listen(PORT,()=>{
    console.log('on port 3010 h gg dgdg gg hhh')

    interface  AuthMiddlewareProps{
      _id:string
      fullName: string,
      lastName: string,
      password: string,
      role:string
  }

  const d = jwt.verify('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2N2ExZjliZDlkZDI4ODNiMWQ4NjRhZjYiLCJmdWxsTmFtZSI6IiBFbW1hbnVlbCIsImxhc3ROYW1lIjoiQWd3dSIsImVtYWlsIjoiYmVuYWd1NDc3QGdtYWlsLmNvbSIsInBhc3N3b3JkIjoiJDJhJDEwJEtma2xmWnJnVjB0T1B3RDM0ZUIuRHVFL2FzZzh3ZEV3cXI3SnFzZlZabDhkUWoxL2VNekdpIiwicm9sZSI6ImNsaWVudCIsIl9fdiI6MCwiaWF0IjoxNzM4ODYwNTE2LCJleHAiOjE3NDE0NTI1MTZ9.UzuBVoY2i62HMwB1lHBtJUT5awC86YqTxTdgAgDAFPg',process.env?.JWT_SECRET!! ) as AuthMiddlewareProps
console.log(
  d._id
  )
  /*  const stream = file.createReadStream(path.join(__dirname,"src",'images.jpeg'))
    
    let buffer:any = null
  stream.on('data',(data)=>{
    console.log(data.toLocaleString())
    
    buffer = data
  }).on('end',(d:any)=>{
    console.log(d)
    console.log('ended')

      
  })

  const t =uploadImage.upload_stream({public_id:"myimag",resource_type:"image"},(err:any,res:any)=>{
    
       console.log(res)
       console.log(err)
       stream.pipe(t).on('finish',(e:any)=>{
        console.log('dobe')
        console.log(e)
       }).on('error',()=>{
        console.log('reeror')
       })
  })
  

 /*sendMail({receiver:"benagu477@gmail.com",subject:"Cosmic Tech Email verification.",message:"your otp is:3020"}).then(res=>{
   console.log(res.response.split(' ')[1] ==="2.0.0")
 }).catch(err=>{
   console.log(err)
 })*/
 })
}).catch(err=>{
  console.log(err)
  process.exit()
})






 