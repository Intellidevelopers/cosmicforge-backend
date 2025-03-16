import uploader from "../../../../config/cloudinary/cloudinary"
import SERVER_STATUS from "../../../../util/interface/CODE"
import { ResponseBodyProps } from "../../../../util/interface/ResponseBodyProps"
import TypedRequest from "../../../../util/interface/TypedRequest"
import TypedResponse from "../../../../util/interface/TypedResponse"
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