import uploader from "../../../../config/cloudinary/cloudinary";
import SERVER_STATUS from "../../../../util/interface/CODE";
import { ResponseBodyProps } from "../../../../util/interface/ResponseBodyProps";
import TypedRequest from "../../../../util/interface/TypedRequest";
import TypedResponse from "../../../../util/interface/TypedResponse";
import MedicalPersonnelCertificationAndUploadModel from "../model/MedicalPersonnelCertModel";

export   const updloadCertificateOrLicense = async ( 
  req: TypedRequest<{
    fullName: string;
    institution: string;
    certificateNo?: string;
    licenceNo?: string;
    licenceImage?: string;
    certificateImage?: string;
    date: string;
    type: "licence" | "certificate";
    photoWithLicence:string
  }>,
  res: TypedResponse<ResponseBodyProps>
) => {


  try {

    const user = req.user
     

    const {
      fullName,
      institution,
      certificateImage,
      certificateNo,
      licenceImage,
      licenceNo,
      date,
      type,
      photoWithLicence
    } = req.body;

    console.log(fullName)

    if (!fullName || !institution || !date || !type) {
      res.status(SERVER_STATUS.BAD_REQUEST).json({
        title: "Upload Licence or Certificate",
        status: SERVER_STATUS.BAD_REQUEST,
        successful: false,
        message:
          "fullName,institution,date and type fields are required to continue."
      });

      return;
    }

    if (type === "licence" && (!licenceNo || !licenceImage || !photoWithLicence)) {
      res.status(SERVER_STATUS.BAD_REQUEST).json({
        title: "Upload Licence or Certificate",
        status: SERVER_STATUS.BAD_REQUEST,
        successful: false,
        message: "licenceImage,photoWithLicence  and licenceNo  fields are required to continue."
      });

      return;
    }

    if (type === "certificate" && (!certificateNo || !certificateImage)) {
      res.status(SERVER_STATUS.BAD_REQUEST).json({
        title: "Upload Licence or Certificate",
        status: SERVER_STATUS.BAD_REQUEST,
        successful: false,
        message:
          "certificateNo and certificateImage  fields are required to continue."
      });

      return;
    }


    const userDocument = await  MedicalPersonnelCertificationAndUploadModel.findOne({
        userId:user?._id

    })

    if(userDocument){
        
        if(type === "licence"){

                const regex = /^data:image\/(png|jpg|jpeg|gif|svg);base64,/i;
                     
                          if(!regex.test(licenceImage!!) || !regex.test(photoWithLicence)){
                     
                             res.status(SERVER_STATUS.BAD_REQUEST).json({
                                 title: 'Upload Licence or Certificate',
                                 status: SERVER_STATUS.BAD_REQUEST,
                                 successful: false,
                                 message: 'Invalid licence image or photoWithLicence format provided. only png|jpg|jpeg|gif|svg is supported'
                             })
                     
                             return
                     
                          }



                        const licenceUrl = await new Promise<string>((resolve,reject)=>{
                                              uploader.upload(licenceImage!!,{
                                                  folder:user?._id.concat('/licence')
                                               },(error,uploadedResult)=>{
                                                  
                                                  if(error){
                                                      reject(error.message)
                                                  }
                          
                                                  resolve(uploadedResult?.secure_url!!)
                                          
                                                
                                               })
                                          })

                         const photoWithLicenceUrl = await new Promise<string>((resolve,reject)=>{
                                            uploader.upload(photoWithLicence!!,{
                                                folder:user?._id.concat('/photoWithLicence')
                                             },(error,uploadedResult)=>{
                                                
                                                if(error){
                                                    reject(error.message)
                                                }
                        
                                                resolve(uploadedResult?.secure_url!!)
                                        
                                              
                                             })
                                        })

                    
                                          const  isUploadValid = licenceUrl.includes("https") &&  photoWithLicenceUrl.includes("https")

                                          if(!isUploadValid){
                                            res.status(SERVER_STATUS.BAD_REQUEST).json({
                                                title: 'Upload Licence or Certificate',
                                                status: SERVER_STATUS.BAD_REQUEST,
                                                successful: false,
                                                message: 'Failed to upload.'
                                            })
                                            return
                                          }


                                          console.log(licenceUrl)

            await userDocument.updateOne({
                licence:{
                    fullName:fullName??userDocument.licence?.fullName,
                     institution:institution??userDocument.licence?.institution,
                     photoWithLicence:photoWithLicenceUrl,
    licenseNo:licenceNo??userDocument.licence?.licenseNo,
    licenseImage:licenceUrl??userDocument.licence?.licenseImage,
    date,
                }
            
            })



            const updatedDocument = await  MedicalPersonnelCertificationAndUploadModel.findOne({
                userId:user?._id
        
            })

            console.log(updatedDocument)


            res.status(SERVER_STATUS.SUCCESS).json({
                title: 'Upload Licence or Certificate',
                status: SERVER_STATUS.SUCCESS,
                successful: true,
                message: 'Successfully uploaded.',
                data:updatedDocument
            })





        }






        if(type === "certificate"){


            const regex = /^data:image\/(png|jpg|jpeg|gif|svg);base64,/i;
                     
            if(!regex.test(certificateImage!!)){
       
               res.status(SERVER_STATUS.BAD_REQUEST).json({
                   title: 'Upload Licence or Certificate',
                   status: SERVER_STATUS.BAD_REQUEST,
                   successful: false,
                   message: 'Invalid certification image format provided.'
               })
       
               return
       
            }



          const certUrl = await new Promise<string>((resolve,reject)=>{
                                uploader.upload(certificateImage!!,{
                                    folder:user?._id.concat('/certificate')
                                 },(error,uploadedResult)=>{
                                    
                                    if(error){
                                        reject(error.message)
                                    }
            
                                    resolve(uploadedResult?.secure_url!!)
                            
                                  
                                 })
                            })


      
                            const  isUploadValid = certUrl.includes("https")

                            if(!isUploadValid){
                              res.status(SERVER_STATUS.BAD_REQUEST).json({
                                  title: 'Upload Licence or Certificate',
                                  status: SERVER_STATUS.BAD_REQUEST,
                                  successful: false,
                                  message: 'Failed to upload.'
                              })
                              return
                            }








            await userDocument.updateOne({
                certification:{
                    fullName:fullName??userDocument.certification?.fullName,
                     institution:institution??userDocument.certification?.institution,
    certificateNo:certificateNo??userDocument.certification?.certificateNo,
   certificateImage:certUrl??userDocument.certification?.certificateImage,
    date,
                }
            
            })



            const updatedDocument = await  MedicalPersonnelCertificationAndUploadModel.findOne({
                userId:user?._id
        
            })



            res.status(SERVER_STATUS.SUCCESS).json({
                title: 'Upload Licence or Certificate',
                status: SERVER_STATUS.SUCCESS,
                successful: true,
                message: 'Successfully uploaded.',
                data:updatedDocument
            })






        }





    }else{


        if(type === "licence"){



            const regex = /^data:image\/(png|jpg|jpeg|gif|svg);base64,/i;
                     
            if(!regex.test(licenceImage!!) && ! regex.test(photoWithLicence!!)){
       
               res.status(SERVER_STATUS.BAD_REQUEST).json({
                   title: 'Upload Licence or Certificate',
                   status: SERVER_STATUS.BAD_REQUEST,
                   successful: false,
                   message: 'Invalid licence image format provided.'
               })
       
               return
       
            }



          const licenceUrl = await new Promise<string>((resolve,reject)=>{
                                uploader.upload(licenceImage!!,{
                                    folder:user?._id.concat('/licence')
                                 },(error,uploadedResult)=>{
                                    
                                    if(error){
                                        reject(error.message)
                                    }
            
                                    resolve(uploadedResult?.secure_url!!)
                            
                                  
                                 })
                            })


                            const photeWithLicenceUrl = await new Promise<string>((resolve,reject)=>{
                                uploader.upload(photoWithLicence!!,{
                                    folder:user?._id.concat('/photoWithLicence')
                                 },(error,uploadedResult)=>{
                                    
                                    if(error){
                                        reject(error.message)
                                    }
            
                                    resolve(uploadedResult?.secure_url!!)
                            
                                  
                                 })
                            })

      
                            const  isUploadValid = licenceUrl.includes("https") && photeWithLicenceUrl.includes("https")

                            if(!isUploadValid){
                              res.status(SERVER_STATUS.BAD_REQUEST).json({
                                  title: 'Upload Licence or Certificate',
                                  status: SERVER_STATUS.BAD_REQUEST,
                                  successful: false,
                                  message: 'Failed to upload.'
                              })
                              return
                            }


                         



            
        
                            const newDocument =      await new MedicalPersonnelCertificationAndUploadModel({
                                userId:user?._id,
                licence:{
                    fullName:fullName,
                     institution:institution,
    licenseNo:licenceNo,
    licenseImage:licenceUrl,
    date,
    photoWithLicence:photeWithLicenceUrl
                }
            
            }).save()


            



            res.status(SERVER_STATUS.SUCCESS).json({
                title: 'Upload Licence or Certificate',
                status: SERVER_STATUS.SUCCESS,
                successful: true,
                message: 'Successfully uploaded.',
                data:newDocument
            })


        
        
        }





        if(type === "certificate"){




            const regex = /^data:image\/(png|jpg|jpeg|gif|svg);base64,/i;
                     
            if(!regex.test(certificateImage!!)){
       
               res.status(SERVER_STATUS.BAD_REQUEST).json({
                   title: 'Upload Licence or Certificate',
                   status: SERVER_STATUS.BAD_REQUEST,
                   successful: false,
                   message: 'Invalid certification image format provided.'
               })
       
               return
       
            }



          const certUrl = await new Promise<string>((resolve,reject)=>{
                                uploader.upload(certificateImage!!,{
                                    folder:user?._id.concat('/certificate')
                                 },(error,uploadedResult)=>{
                                    
                                    if(error){
                                        reject(error.message)
                                    }
            
                                    resolve(uploadedResult?.secure_url!!)
                            
                                  
                                 })
                            })


      
                            const  isUploadValid = certUrl.includes("https")

                            if(!isUploadValid){
                              res.status(SERVER_STATUS.BAD_REQUEST).json({
                                  title: 'Upload Licence or Certificate',
                                  status: SERVER_STATUS.BAD_REQUEST,
                                  successful: false,
                                  message: 'Failed to upload.'
                              })
                              return
                            }

         const newDocument =   await new MedicalPersonnelCertificationAndUploadModel({
            userId:user?._id,
                certification:{
                    fullName:fullName,
                     institution:institution,
                     certificateNo,
                    certificateImage:certUrl,
                     date,
                }
            
            }).save()

            res.status(SERVER_STATUS.SUCCESS).json({
                title: 'Upload Licence or Certificate',
                status: SERVER_STATUS.SUCCESS,
                successful: true,
                message: 'Successfully uploaded.',
                data:newDocument
            })


        }

        

       

    }

    
  } catch (error:any) {

    res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
        title: 'Upload Licence or Certificate',
        status: SERVER_STATUS.INTERNAL_SERVER_ERROR,
        successful: false,
        message: 'Internal server error try again.',
        error:error.message
    })



  }
};


export const getupdloadCertificateOrLicense = async ( req: TypedRequest<{}>,
  res: TypedResponse<ResponseBodyProps>) => {

    const user = req.user

     const document = await MedicalPersonnelCertificationAndUploadModel.findOne({
        userId:user?._id
     })

     res.status(SERVER_STATUS.SUCCESS).json({
        title: 'Upload Licence or Certificate',
        status: SERVER_STATUS.SUCCESS,
        successful: true,
        message: 'Successfully fetched.',
       data:document
    })
    

}
