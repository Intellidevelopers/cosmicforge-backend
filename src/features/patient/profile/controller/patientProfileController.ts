import SERVER_STATUS from "../../../../util/interface/CODE";
import { ResponseBodyProps } from "../../../../util/interface/ResponseBodyProps";
import TypedRequest from "../../../../util/interface/TypedRequest";
import TypedResponse from "../../../../util/interface/TypedResponse";
import { USER_ROLES } from "../../../../util/interface/UserRole";
import jwt from 'jsonwebtoken'
import newUserModel from "../../../newUser/model/newUserModel";
import PatientProfileModel from "../model/patientProfileModel";
import uploader from "../../../../config/cloudinary/cloudinary";
import ChatModel from "../../../io/chat/model/chatModel";

enum profileType {
    personal, family
}

export interface PatientProfileRequestProps {
    email?: string,
    mobileNo?: string,
    homeAddress?: string,
    workAddress?: string,
    dateOfBirth?: string,
    gender?: string,
    profilePicture?: string,

}

interface PatientVitalSignsProps {
    oxygenSaturation: string,
    bloodPressure: string,
    bodyTemperature: string,
    weight: string,
    height: string,
    profileType: profileType,
    dateOfBirth: string,
    gender: string,

}

export const updatePatientProfile = async (req: TypedRequest<PatientProfileRequestProps>, res: TypedResponse<ResponseBodyProps>) => {


    try {

        const user = req.user!!

        if (!user || user.role !== USER_ROLES.CLIENT) {
            res.status(SERVER_STATUS.Forbidden).json({
                title: 'Update Profile Message',
                status: SERVER_STATUS.Forbidden,
                successful: false,
                message: 'UnAuthorized access.'
            })

            return
        }



        const { email, mobileNo, homeAddress, workAddress,profilePicture } = req.body

        if (!email && !mobileNo && !homeAddress && !workAddress && !profilePicture) {

            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: 'Update Profile Message',
                status: SERVER_STATUS.BAD_REQUEST,
                successful: false,
                message: 'Either email,mobileNo,homeAddress,workAddress,profilePicture is needed to continue .'
            })

            return

        }

        if(profilePicture){

            const regex = /^data:image\/(png|jpg|jpeg|gif);base64,/i;
        
             if(!regex.test(profilePicture)){
        
                res.status(SERVER_STATUS.BAD_REQUEST).json({
                    title: 'Update Profile Message',
                    status: SERVER_STATUS.BAD_REQUEST,
                    successful: false,
                    message: 'Invalid profile picture format provided.'
                })
        
                return
        
             }
        

             
        
                }


        //update token if email is channged
        let token = null

        if (email && email !== user.email) {
            await newUserModel.findOneAndUpdate({ _id: user._id }, {
                email
            })

            const updatedTokenObject = {
                _id: user._id,
                email,
                password: user.password,
                fullName: user.fullName,
                lastName: user.lastName,
                role: user.role


            }

            token = jwt.sign(updatedTokenObject, process.env?.JWT_SECRET!!, { expiresIn: '30d' })


        }

        let userProfile = await PatientProfileModel.findOne({userId:user._id })
        const userAccount = await newUserModel.findOne({ _id: user._id })

        if (userProfile) {

            let profileUrl:string | null = null

            if(profilePicture){

                profileUrl = await new Promise<string>((resolve,reject)=>{
                    uploader.upload(profilePicture,{
                        folder:user._id.concat('/profile')
                     },(error,uploadedResult)=>{
                        
                        if(error){
                            reject(error)
                        }

                        resolve(uploadedResult?.secure_url!!)
                
                      
                     })
                })
            }
         await  userProfile.updateOne({
                profilePicture: profileUrl ?? userProfile.profilePicture,
                homeAddress: homeAddress ?? userProfile.homeAddress,
                mobileNo: mobileNo ?? userProfile.mobileNo,
                workAddress: workAddress ?? userProfile.workAddress,
                

            }, {
                new:true,
                returnDocument:'after'
            })
            userProfile = await PatientProfileModel.findOne({userId:user._id })



            if (token) {

                const updatedProfile = {
                    ...userAccount,
                    profile: userProfile,
                    token
                }

            
                const messageProfile =  await ChatModel.find({
                    $or:[
                     {
                         "userOneID.userId":user._id
                     },
                     {
                         "userTwoID.userId":user._id
                     }
                    ] 
                 })
        
                 if(messageProfile && messageProfile.length>0){
        
        
               
        
                      messageProfile.forEach( async data=>{
        
                        if( data.userOneID?.userId === user._id){
        
                            await  data.updateOne({
                                   userOneID:{
                                      userId:user._id,
                           userName:userAccount?.lastName.concat(' ').concat(userAccount.fullName),
                           userProfile:userProfile
                                   }
                              })
          
          
                          } else if (data.userTwoID?.userId === user._id){
                           
                           await  data.updateOne({
                               userTwoID:{
                                  userId:user._id,
                       userName:userAccount?.lastName.concat(' ').concat(userAccount.fullName),
                       userProfile:userProfile
                               }
                          })
                          }
        
                      })
        
                   
                 }







                res.status(SERVER_STATUS.SUCCESS).json({
                    title: 'Update Profile Message',
                    status: SERVER_STATUS.SUCCESS,
                    successful: true,
                    message: 'Successfully Updated Profile',
                    data: updatedProfile

                })


                return


            }


           

            const updatedProfile = {
                ...userAccount?.toObject(),
                profile:userProfile



            }



          
            const messageProfile =  await ChatModel.find({
                $or:[
                 {
                     "userOneID.userId":user._id
                 },
                 {
                     "userTwoID.userId":user._id
                 }
                ] 
             })
    
             if(messageProfile && messageProfile.length>0){
    
    
           
    
                  messageProfile.forEach( async data=>{
    
                    if( data.userOneID?.userId === user._id){
    
                        await  data.updateOne({
                               userOneID:{
                                  userId:user._id,
                       userName:userAccount?.lastName.concat(' ').concat(userAccount.fullName),
                       userProfile:userProfile
                               }
                          })
      
      
                      } else if (data.userTwoID?.userId === user._id){
                       
                       await  data.updateOne({
                           userTwoID:{
                              userId:user._id,
                   userName:userAccount?.lastName.concat(' ').concat(userAccount.fullName),
                   userProfile:userProfile
                           }
                      })
                      }
    
                  })
    
               
             }

            res.status(SERVER_STATUS.SUCCESS).json({
                title: 'Update Profile Message',
                status: SERVER_STATUS.SUCCESS,
                successful: true,
                message: 'Successfully Updated Profile',
                data: updatedProfile

            })



            return
        }

        let profileUrl:string | null = null

        if(profilePicture){

            profileUrl = await new Promise<string>((resolve,reject)=>{
                uploader.upload(profilePicture,{
                    folder:user._id.concat('/profile')
                 },(error,uploadedResult)=>{
                    
                    if(error){
                        reject(error)
                    }

                    resolve(uploadedResult?.secure_url!!)
            
                  
                 })
            })


        }


        let createProfileforUser = new PatientProfileModel({
            userId: user._id,
            profilePicture:profileUrl,
            mobileNo,
            homeAddress,
            workAddress,
          
        

        })

        await createProfileforUser.save()

        if (token) {

            const updatedProfile = {
                ...userAccount,
                profile: createProfileforUser,
                token
            }


           
            const messageProfile =  await ChatModel.find({
                $or:[
                 {
                     "userOneID.userId":user._id
                 },
                 {
                     "userTwoID.userId":user._id
                 }
                ] 
             })
    
             if(messageProfile && messageProfile.length>0){
    
    
           
    
                  messageProfile.forEach( async data=>{
    
                    if( data.userOneID?.userId === user._id){
    
                        await  data.updateOne({
                               userOneID:{
                                  userId:user._id,
                       userName:userAccount?.lastName.concat(' ').concat(userAccount.fullName),
                       userProfile:userProfile
                               }
                          })
      
      
                      } else if (data.userTwoID?.userId === user._id){
                       
                       await  data.updateOne({
                           userTwoID:{
                              userId:user._id,
                   userName:userAccount?.lastName.concat(' ').concat(userAccount.fullName),
                   userProfile:userProfile
                           }
                      })
                      }
    
                  })
    
               
             }

            res.status(SERVER_STATUS.SUCCESS).json({
                title: 'Update Profile Message',
                status: SERVER_STATUS.SUCCESS,
                successful: true,
                message: 'Successfully Updated Profile',
                data: updatedProfile

            })


            return


        }




        const updatedProfile = {
            ...userAccount?.toObject(),
            profile: createProfileforUser



        }


        const messageProfile =  await ChatModel.find({
            $or:[
             {
                 "userOneID.userId":user._id
             },
             {
                 "userTwoID.userId":user._id
             }
            ] 
         })

         if(messageProfile && messageProfile.length>0){


       

              messageProfile.forEach( async data=>{

                if( data.userOneID?.userId === user._id){

                    await  data.updateOne({
                           userOneID:{
                              userId:user._id,
                   userName:userAccount?.lastName.concat(' ').concat(userAccount.fullName),
                   userProfile:userProfile
                           }
                      })
  
  
                  } else if (data.userTwoID?.userId === user._id){
                   
                   await  data.updateOne({
                       userTwoID:{
                          userId:user._id,
               userName:userAccount?.lastName.concat(' ').concat(userAccount.fullName),
               userProfile:userProfile
                       }
                  })
                  }

              })

           
         }

        res.status(SERVER_STATUS.SUCCESS).json({
            title: 'Update Profile Message',
            status: SERVER_STATUS.SUCCESS,
            successful: true,
            message: 'Successfully Updated Profile',
            data: updatedProfile

        })





    } catch (error: any) {
        res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
            title: 'Update Profile Message',
            status: SERVER_STATUS.INTERNAL_SERVER_ERROR,
            successful: true,
            message: 'An error occured.',
            error: error.message


        })
    }


}


export const updateVitalSigns = async (req:TypedRequest<PatientVitalSignsProps>,res:TypedResponse<ResponseBodyProps>) =>{

    try {

        const user = req.user!!

        if (!user || user.role !== USER_ROLES.CLIENT) {
            res.status(SERVER_STATUS.Forbidden).json({
                title: 'Update Profile Message',
                status: SERVER_STATUS.Forbidden,
                successful: false,
                message: 'UnAuthorized access.'
            })

            return
        }


        const {bloodPressure,bodyTemperature,oxygenSaturation,weight,height,profileType,dateOfBirth,gender} = req.body
        if(!bloodPressure || !bodyTemperature || !oxygenSaturation || !weight || !height || !profileType || !dateOfBirth || !gender){
            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: 'Update Vital Signs Message',
                status: SERVER_STATUS.BAD_REQUEST,
                successful:false,
                message: 'bloodPressure,bodyTemperature,oxygenSaturation,weight,height,profileType,dateOfBirth,gender fields are needed to '
            })

            return
        }

        const userAccount = await newUserModel.findOne({_id:user._id})

        let userProfile = await PatientProfileModel.findOne({userId:userAccount?._id})
        

        if(userProfile){
        
           await userProfile.updateOne({vitalSigns:{
                bloodPressure,
                bodyTemperature,
                oxygenSaturation,
                weight,
                height,
                gender,
                dateOfBirth
            },
        profileType},{
            new:true
        })

        userProfile = await PatientProfileModel.findOne({userId:user._id})

        res.status(SERVER_STATUS.SUCCESS).json({
            title: 'Update Vital Signs Message',
            status: SERVER_STATUS.SUCCESS,
            successful:true,
            message: 'successfully updated vital signs. ',
            data:{
                ...userAccount?.toObject(),
                profile:userProfile

            }
        })

        return 
        }

        const newProfile =  new PatientProfileModel({
            vitalSigns:{
                bloodPressure,
                bodyTemperature,
                oxygenSaturation,
                weight,
                height,
                gender,
                dateOfBirth
            },
            profileType,
            userId:user._id
            
        })

        await newProfile.save()

        res.status(SERVER_STATUS.SUCCESS).json({
            title: 'Update Vital Signs Message',
            status: SERVER_STATUS.SUCCESS,
            successful:true,
            message: 'successfully updated vital signs. ',
            data:{
                ...userAccount?.toObject(),
                profile:newProfile

            }
        })

        
    } catch (error:any) {
        res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
            title: 'Update Vital Signs Message',
            status: SERVER_STATUS.INTERNAL_SERVER_ERROR,
            successful: false,
            message: 'An error occured.',
            error: error.message


        })
    }


}