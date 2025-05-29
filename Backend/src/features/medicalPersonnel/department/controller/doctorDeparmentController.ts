import uploader from "../../../../config/cloudinary/cloudinary"
import SERVER_STATUS from "../../../../util/interface/CODE"
import { ResponseBodyProps } from "../../../../util/interface/ResponseBodyProps"
import TypedRequest from "../../../../util/interface/TypedRequest"
import TypedResponse from "../../../../util/interface/TypedResponse"
import BookAppointmentModel from "../../../appointment/model/bookAppointmentModel"
import SubscriptionModel from "../../../subscription/model/SubscriptionModel"
import MedicalPersonnelCertificationAndUploadModel from "../../certification/model/MedicalPersonnelCertModel"
import MedicalPersonnelProfileModel from "../../profile/model/profileModel"
import DoctorDepartmentModel from "../model/model"




const  addNewDepartment = async(req:TypedRequest<{departmentName:string,departmentImage:string}>,res:TypedResponse<ResponseBodyProps>) => {

   // const  user =  req.user

   // if(!us)


   try {

     const {departmentName,departmentImage} = req.body

     if(!departmentName && !departmentImage){
        res.status(SERVER_STATUS.BAD_REQUEST).json({
            title:"Add Department Message",
            status:SERVER_STATUS.BAD_REQUEST,
            successful:false,
            message:"departmentName and departmentImage is needed to continue."
        })
        return
     }

  const  departmentImageUrl= await new Promise<string>((resolve,reject)=>{
        uploader.upload(departmentImage,{
            folder:'DoctorsDepartment'
         },(error,uploadedResult)=>{
            
            if(error){
                reject(error.message)
            }

            resolve(uploadedResult?.secure_url!!)
    
          
         })
    })
    
   } catch (error) {
    
   }


}

 export const getDepartments =  async (req:TypedRequest<any>,res:TypedResponse<ResponseBodyProps>) =>{

    try {
        
        const user = req.user

        if(!user){
            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title:"Doctor Department Message",
                status:SERVER_STATUS.BAD_REQUEST,
                successful:false,
                message:"not authorized"
            })
            return 
        }

        const departments = await DoctorDepartmentModel.find().sort({name:'asc'})


        res.status(SERVER_STATUS.SUCCESS).json({
            title:"Doctor Department Message",
            status:SERVER_STATUS.SUCCESS,
            successful:true,
            message:'successfully fetched',
            data:departments
            
        })

    } catch (error:any) {
        res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
            title:"Doctor Department Message",
            status:SERVER_STATUS.INTERNAL_SERVER_ERROR,
            successful:false,
            message:"Internal server error"
        })
    }

}

export const getDepartmentsForLadingPage =  async (req:TypedRequest<any>,res:TypedResponse<ResponseBodyProps>) =>{

    try {
        
        

        const departments = await DoctorDepartmentModel.find().sort({name:'asc'})


        res.status(SERVER_STATUS.SUCCESS).json({
            title:"Doctor Department Message",
            status:SERVER_STATUS.SUCCESS,
            successful:true,
            message:'successfully fetched',
            data:departments
            
        })

    } catch (error:any) {
        res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
            title:"Doctor Department Message",
            status:SERVER_STATUS.INTERNAL_SERVER_ERROR,
            successful:false,
            message:"Internal server error"
        })
    }

}

export const  getDoctorsBySpecificDepartment = async (req:TypedRequest<{department:string}>,res:TypedResponse<ResponseBodyProps>) =>{

     const {department} = req.body

     try {

        const user = req.user

        if(!user){
            res.status(SERVER_STATUS.UNAUTHORIZED).json({
                title:'Get doctors by departments',
                status:SERVER_STATUS.UNAUTHORIZED,
                successful:false,
                message:'not authorized.'
            })
            return  
        }

        if(user.role !== 'client'){
            res.status(SERVER_STATUS.Forbidden).json({
                title:'Get doctors by departments',
                status:SERVER_STATUS.Forbidden,
                successful:false,
                message:'forbidden.'
            })
            return  
        }

        if(!department){

            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title:'Get doctors by departments',
                status:SERVER_STATUS.BAD_REQUEST,
                successful:false,
                message:'department field is needed to continue.'
            })

            return
        }





        let doctors = await MedicalPersonnelProfileModel.find({
            department
        }).populate('userId','fullName lastName')

      


        if(doctors){
        const  doctorUpdate:any[] = [] 
        
      

         for (const doctor of doctors){

        

         let doctorStatus= await MedicalPersonnelCertificationAndUploadModel.findOne({
            userId:doctor.userId
         })
         
          let  doctorPlan = ''

                const isValid = await new Promise<boolean>(async(resolve,reject)=>{
                    const date = new Date()
                    const monthName = date.toLocaleString('en-Us',{
                        month:'long'
                      })
                      
                  const subscription = await SubscriptionModel.findOne({
                    userId:doctor.userId
                  })

                   doctorPlan = subscription?.planName!!

                 const  appointment = await BookAppointmentModel.find({
                    medicalPersonelID:doctor.userId,
                    appointmentDate:{
                        $regex:monthName , $options:'i'
                    }
                 })
    
    
                  switch(subscription?.planName){
                     
                    case 'Free':{
                        resolve(appointment.length===20)
                        return
                    }
    
    
                    case 'Basic':{
                        resolve(appointment.length===50)
                        return
                    }
    
    
                    case 'Premium':{
                        resolve(appointment.length ===100)
                        return
                    }
    
                    case 'Professional':{
                        resolve(false)
                        return
                    }
    
                    default : {
                        resolve(false)
                    }
               
                  }
             
    
              
    
                })



                   if(!isValid){
                    doctorUpdate.push({...doctor.toJSON(),isVerified:doctorStatus?.licenseDetails?.isVerified??false,totalPatient:await BookAppointmentModel.find({
                        appointmentStatus:'completed'
                    }).countDocuments(),doctorPlan})
                   }

         
     
           
         }
        
     
          
            res.status(SERVER_STATUS.SUCCESS).json({
                title:'Get doctors by departments',
                status:SERVER_STATUS.SUCCESS,
                successful:true,
                message:'successfully fetched.',
                data:doctorUpdate
            })
        }

  

       
        
     } catch (error:any) {
        res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
            title:'Get doctors by departments',
            status:SERVER_STATUS.INTERNAL_SERVER_ERROR,
            successful:false,
            message:'An error occured.',
            error:error.message
        }) 
     }

}