
import express from 'express'

import jwt  from 'jsonwebtoken'
import { userTempRoleModel } from '../model/tempRoleModel'
import SERVER_STATUS from '../../util/interface/CODE'
import newUserModel from '../../features/newUser/model/newUserModel'
import { USER_ROLES } from '../../util/interface/UserRole'
import PatientProfileModel from '../../features/patient/profile/model/patientProfileModel'
import MedicalPersonnelProfileModel from '../../features/medicalPersonnel/profile/model/profileModel'
import hashedKey from 'bcryptjs'

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
 console.log(userRole)
     if(!userRole){
      res.status(SERVER_STATUS.BAD_REQUEST).json({
        message:'Something went wrong try again.'
      })
      return
     }

        const userDetails = req.user._json as GoogleAuthResponseProps

        const userAccount = await  newUserModel.findOne({
          email:userDetails.email
        })


        if(userAccount){
          await  userTempRoleModel.deleteMany()
          if(userAccount.role === USER_ROLES.CLIENT.toString()){
             
            const userProfile = await PatientProfileModel.findOne({
              userId:userAccount._id
            })
           
            const token = jwt.sign({
              ...userAccount.toJSON()
            },process.env.JWT_SECRET!!,{expiresIn:'30d'})

            const encode = jwt.sign({
              ...userAccount.toJSON(),
              userProfile:userProfile?.toJSON(),
              token,
              secretKey
            },process.env.JWT_SECRET!!,{expiresIn:Math.floor(Date.now()/1000)+300})
               
           
            
            await  userTempRoleModel.deleteMany()

            const userAgent = req.headers['user-agent']

            const isMobile = /Androin|iphone|ipad/i.test(userAgent!!)

            if(isMobile){
              console.log('redirecting mobile......')
          res.set("Location",`${process.env.web_base_url}/auth?token=${encode}`)
          res.status(302).send()
              return
            }

            const url = new URL(`${process.env.web_base_url}/auth`,req.protocol+'://'+req.get('host'))
            url.searchParams.set('redirect','true')
            url.searchParams.set('token',encode)
          
            res.redirect(301,url.href)
             return


          }else if(userAccount.role === USER_ROLES.DOCTOR.toString()){

            const userProfile = await MedicalPersonnelProfileModel.findOne({
              userId:userAccount._id
            })
           
            const token = jwt.sign({
              ...userAccount.toJSON()
            },process.env.JWT_SECRET!!,{expiresIn:'30d'})

            const encode = jwt.sign({
              ...userAccount.toJSON(),
              userProfile:userProfile?.toJSON(),
              token,
              secretKey
            },process.env.JWT_SECRET!!,{expiresIn:'5mins'})
            await  userTempRoleModel.deleteMany()
            const url = new URL(`${process.env.web_base_url}/auth`,req.protocol+'://'+req.get('host'))
            url.searchParams.set('redirect','true')
            url.searchParams.set('token',encode)
 
            res.redirect(url.href)
        return
          }


          return

        }


       const newAccount =  await  new newUserModel({
        email:userDetails.email,
        fullName:userDetails.name.split(' ')[1],
        lastName:userDetails.name.split(' ')[0],
        role:userRole
       }).save()

       const token = jwt.sign({
        ...newAccount.toJSON()
      },process.env.JWT_SECRET!!,{expiresIn:'30d'})

      const encode = jwt.sign({
        ...newAccount.toJSON(),
        token,
        secretKey
      },process.env.JWT_SECRET!!,{expiresIn:'5mins'})
      await  userTempRoleModel.deleteMany()

      const url = new URL(`${process.env.web_base_url}/auth`,req.protocol+'://'+req.get('host'))
      url.searchParams.set('redirect','true')
      url.searchParams.set('token',encode)

      res.redirect(url.href)





   } catch (error:any) {
    
    res.status(SERVER_STATUS.BAD_REQUEST).json({
      message:'Something went wrong try again.',
      error:error.message
    })


   }
 




          
      
}