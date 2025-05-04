import SERVER_STATUS from "../../../../util/interface/CODE"
import { ResponseBodyProps } from "../../../../util/interface/ResponseBodyProps"
import TypedRequest from "../../../../util/interface/TypedRequest"
import TypedResponse from "../../../../util/interface/TypedResponse"
import newUserModel from "../../../newUser/model/newUserModel"
import jwt from 'jsonwebtoken'
import MedicalPersonnelProfileModel from "../model/profileModel"
import { USER_ROLES } from "../../../../util/interface/UserRole"
import uploader from "../../../../config/cloudinary/cloudinary"
import ChatModel from "../../../io/chat/model/chatModel"


export interface MedicalPersonnelRequestProps {
    email?: string,
    mobileNo?: string,
    professionalTitle?: string,
    specialization?: string,
    currentClinic?: string,
    department?: string,
    location?: string,
    profilePicture?: string,
    pricing:number,
    fullName:string,
    lastName:string,
    experience:{},
    workingHours:{}

}

export const updateProfile = async (req: TypedRequest<MedicalPersonnelRequestProps>, res: TypedResponse<ResponseBodyProps>) => {
   
    try {
        const user = req.user!!



        if (!user._id || user._id === undefined || user._id === "") {

            res.status(SERVER_STATUS.Forbidden).json({
                title: 'Update Profile Message',
                status: SERVER_STATUS.Forbidden,
                successful: false,
                message: 'You not authorized to continue.'
            })
            return
        }

        if (user.role != USER_ROLES.DOCTOR) {
            res.status(SERVER_STATUS.Forbidden).json({
                title: 'Update Profile Message',
                status: SERVER_STATUS.Forbidden,
                successful: false,
                message: 'You not authorized to continue.'
            })
            return
        }


        const { email, mobileNo, professionalTitle, specialization, currentClinic, department, location, profilePicture,pricing,fullName,lastName, workingHours,experience } = req.body

        if (!email && !mobileNo && !professionalTitle && !specialization && !currentClinic && !location && !profilePicture && !department && !pricing && !fullName && !lastName ) {

            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: 'Update Profile Message',
                status: SERVER_STATUS.BAD_REQUEST,
                successful: false,
                message: 'Either email,mobileNo,professionalTitle,specialization,currentClinic,department,location,profilePicture,pricing, fullName,lastName field is needed to continue.'
            })

            return
        }


        let userAccount = await newUserModel.findOne({ _id:user._id })

        //update token if email is channged
        let token = null

        if(fullName || lastName){

             if(userAccount?.fullName!==fullName || userAccount?.lastName!==lastName){
            await userAccount?.updateOne({
                fullName:fullName ?? userAccount.fullName,
                lastName:lastName ?? userAccount.fullName
              })

              const updatedTokenObject = {
                _id: user._id,
                email:user.email,
                password: user.password,
                fullName:fullName,
                lastName:lastName,
                role: user.role


            }

            token = jwt.sign(updatedTokenObject, process.env?.JWT_SECRET!!, { expiresIn: '30d' })
        }

        }

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

        let userProfile = await MedicalPersonnelProfileModel.findOne({ userId: user._id })
      

        if(profilePicture){

            const regex = /^data:image\/(png|jpg|jpeg|gif|svg);base64,/i;
        
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










        if (userProfile) {

            let profileUrl:string | null = null

            if(profilePicture){

                profileUrl = await new Promise<string>((resolve,reject)=>{
                    uploader.upload(profilePicture,{
                        folder:user._id.concat('/profile')
                     },(error,uploadedResult)=>{
                        
                        if(error){
                            reject(error.message)
                        }

                        resolve(uploadedResult?.secure_url!!)
                
                      
                     })
                })
            }

        
           await userProfile.updateOne({
                profilePicture: profileUrl ?? userProfile.profilePicture,
                professionalTitle: professionalTitle ?? userProfile.professionalTitle,
                mobileNo: mobileNo ?? userProfile.mobileNo,
                specializationTitle: specialization ?? userProfile.specializationTitle,
                currentClinic: currentClinic ?? userProfile.currentClinic,
                department: department ?? userProfile.department,
                location: location ?? userProfile.location,
                pricing:pricing?? userProfile.pricing,
                experience,
                workTime: workingHours

                

            }, {
                returnOriginal: false
            })


            userProfile = await MedicalPersonnelProfileModel.findOne({ userId: user._id })
            userAccount = await newUserModel.findOne({ _id: user._id })

            if (token) {

                const updatedProfile = {
                    ...userAccount?.toObject(),
                    profile: userProfile?.toObject(),
                    token
                }

                const messageProfile =  await ChatModel.findOne({
                   $or:[
                    {
                        "userOneID.userId":user._id
                    },
                    {
                        "userTwoID.userId":user._id
                    }
                   ] 
                })

                if(messageProfile){
                   if( messageProfile.userOneID?.userId === user._id){

                     await  messageProfile.updateOne({
                            userOneID:{
                    userName:userAccount?.lastName.concat(' ').concat(userAccount.fullName),
                    userProfile:userProfile
                            }
                       })


                   }else if (messageProfile.userTwoID?.userId === user._id){

                    await  messageProfile.updateOne({
                        userOneID:{
                userName:userAccount?.lastName.concat(' ').concat(userAccount.fullName),
                userProfile:userProfile
                        }
                   })
                   }
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





            const convertToObject = userProfile?.toObject()

            const updatedProfile = {
                ...userAccount?.toObject(),
                profile: convertToObject



            }


            const messageProfile =  await ChatModel.find({
                $or:[
                    {
                        'userOneID.userId':user._id
                       } 
                       ,
                       {
                        'userTwoID.userId':user._id
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
                        reject(error.message)
                    }

                    resolve(uploadedResult?.secure_url!!)
            
                  
                 })
            })


        }


        let createProfileforUser = new MedicalPersonnelProfileModel({
            userId: user._id,
            profilePicture:profileUrl,
            mobileNo,
            professionalTitle,
            specialization,
            currentClinic,
            department,
            location,
            pricing

        })

        await createProfileforUser.save()

        if (token) {
            
            const updatedProfile = {
                ...userAccount?.toObject(),
                profile: createProfileforUser.toObject(),
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
            profile: createProfileforUser.toObject()



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