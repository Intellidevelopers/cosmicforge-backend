
import express from 'express'

import jwt  from 'jsonwebtoken'
import { userTempRoleModel } from '../model/tempRoleModel'
import SERVER_STATUS from '../../util/interface/CODE'
import newUserModel from '../../features/newUser/model/newUserModel'
import { USER_ROLES } from '../../util/interface/UserRole'
import PatientProfileModel from '../../features/patient/profile/model/patientProfileModel'
import MedicalPersonnelProfileModel from '../../features/medicalPersonnel/profile/model/profileModel'
import hashedKey from 'bcryptjs'
import TypedResponse from '../../util/interface/TypedResponse'
import { ResponseBodyProps } from '../../util/interface/ResponseBodyProps'
import {v4} from 'uuid'

interface GoogleAuthResponseProps {
  name:string,
  email:string
}

export const googleSignUpSignInAuthcontroller = async (req:express.Request,res:express.Response) =>   {
   try {
    

    const savedData = await userTempRoleModel.findOne()
    const salt = await hashedKey.genSalt(10)
    const secretKey = await hashedKey.hash(process.env.JWT_SECRET!!,salt)
 
     const userRole = savedData?.userRole

     const userDetails = req.user._json as GoogleAuthResponseProps

     const userAccount = await  newUserModel.findOne({
       email:userDetails.email
     })
     
 console.log(userRole)

    if(savedData?.authType === "login" && userAccount){

      if(userAccount.role === USER_ROLES.CLIENT.toString()){
             
        const userProfile = await PatientProfileModel.findOne({
          userId:userAccount._id
        })
       
        const token = jwt.sign({
          ...userAccount.toJSON()
        },process.env.JWT_SECRET!!,{expiresIn:'30d'})

        /*const encode = jwt.sign({
          ...userAccount.toJSON(),
          userProfile:userProfile?.toJSON(),
          token,
          secretKey
        },process.env.JWT_SECRET!!,{expiresIn:Math.floor(Date.now()/1000)+300})*/
           
         await userTempRoleModel.updateOne({userData:{
          ...userAccount.toJSON(),
          userProfile:userProfile?.toJSON(),
          token,
          secretKey
        }})
        
     
         
        res.set("Location",`${process.env.web_base_url}/auth`)
        res.status(302).send()
         return


      }else if(userAccount.role === USER_ROLES.DOCTOR.toString()){

        const userProfile = await MedicalPersonnelProfileModel.findOne({
          userId:userAccount._id
        })
       
        const token = jwt.sign({
          ...userAccount.toJSON()
        },process.env.JWT_SECRET!!,{expiresIn:'30d'})

       
        
  

        await userTempRoleModel.updateOne({userData:{
          ...userAccount.toJSON(),
          userProfile:userProfile?.toJSON(),
          token,
          secretKey
        }})
        

        res.set("Location",`${process.env.web_base_url}/auth`)
        res.status(302).send()
     
    return
      }
      
  return
}








     if(!userRole){
      res.status(SERVER_STATUS.BAD_REQUEST).json({
        message:'Something went wrong try again.'
      })
      return
     }

      


         




        if(userAccount){
        
          if(userAccount.role === USER_ROLES.CLIENT.toString()){
             
            const userProfile = await PatientProfileModel.findOne({
              userId:userAccount._id
            })
           
            const token = jwt.sign({
              ...userAccount.toJSON()
            },process.env.JWT_SECRET!!,{expiresIn:'30d'})

            /*const encode = jwt.sign({
              ...userAccount.toJSON(),
              userProfile:userProfile?.toJSON(),
              token,
              secretKey
            },process.env.JWT_SECRET!!,{expiresIn:Math.floor(Date.now()/1000)+300})*/
               
             await userTempRoleModel.updateOne({userData:{
              ...userAccount.toJSON(),
              userProfile:userProfile?.toJSON(),
              token,
              secretKey
            }})
            
            //await  userTempRoleModel.deleteMany()

           

          /*  const url = new URL(`${process.env.web_base_url}/auth`,req.protocol+'://'+req.get('host'))
            url.searchParams.set('redirect','true')
            url.searchParams.set('token',encode)
          
            res.redirect(301,url.href)*/
           
             
            res.set("Location",`${process.env.web_base_url}/auth`)
            res.status(302).send()
             return


          }else if(userAccount.role === USER_ROLES.DOCTOR.toString()){

            const userProfile = await MedicalPersonnelProfileModel.findOne({
              userId:userAccount._id
            })
           
            const token = jwt.sign({
              ...userAccount.toJSON()
            },process.env.JWT_SECRET!!,{expiresIn:'30d'})

           
            
      

            await userTempRoleModel.updateOne({userData:{
              ...userAccount.toJSON(),
              userProfile:userProfile?.toJSON(),
              token,
              secretKey
            }})
            

            res.set("Location",`${process.env.web_base_url}/auth`)
            res.status(302).send()
         
        return
          }


          return

        }


       const newAccount =  await  new newUserModel({
        email:userDetails.email,
        fullName:userDetails.name.split(' ')[1],
        lastName:userDetails.name.split(' ')[0],
        role:userRole === 'patient' ? 'client':userRole,
        password:v4()
       }).save()

       const token = jwt.sign({
        ...newAccount.toJSON()
      },process.env.JWT_SECRET!!,{expiresIn:'30d'})

      

      await userTempRoleModel.updateOne({userData:{
        ...newAccount.toJSON(),
        token,
        secretKey
      },newAccount:true})
    

      res.set("Location",`${process.env.web_base_url}/auth`)
      res.status(302).send()



   } catch (error:any) {
    
    res.status(SERVER_STATUS.BAD_REQUEST).json({
      message:'Something went wrong try again.',
      error:error.message
    })


   }
 




          
      
}

export const getGoogleAuthUserDetails = async (req:express.Request,res:TypedResponse<ResponseBodyProps>) =>{

   const {token} = req.body

   if(!token){
    res.status(SERVER_STATUS.BAD_REQUEST).json({
      title:"Auth token validator",
      status:SERVER_STATUS.BAD_REQUEST,
      successful:false,
      message:"token needed to continue."
    })

    return
   }

   const data = await userTempRoleModel.findOne({
    token
   })

   if(!data){
    res.status(SERVER_STATUS.BAD_REQUEST).json({
      title:"Auth token validator",
      status:SERVER_STATUS.BAD_REQUEST,
      successful:false,
      message:"invalid token provided."
    })

    return
   }

   await userTempRoleModel.deleteOne({
    token
   })

 res.status(SERVER_STATUS.SUCCESS).json({
  title:"Auth token validator",
  status:SERVER_STATUS.SUCCESS,
  successful:true,
  message:"successfully fetched.",
  data:{
    userDetails:data.userData,
    newAccount:data.newAccount
  }
 })



     

}