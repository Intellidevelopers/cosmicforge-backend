import uploader from "../../../../config/cloudinary/cloudinary";
import SERVER_STATUS from "../../../../util/interface/CODE";
import { ResponseBodyProps } from "../../../../util/interface/ResponseBodyProps";
import TypedRequest from "../../../../util/interface/TypedRequest";
import TypedResponse from "../../../../util/interface/TypedResponse";
import MedicalPersonnelCertificationAndUploadModel from "../model/MedicalPersonnelCertModel";

export   const updloadCertificateOrLicense = async ( 
  req: TypedRequest<{
    fullName: string,
    LicenseNumber: string,
    license: string,
    expiration: string,
    country: string,
    docummentType:string,
    documentId: string,
    documentHoldName: string,
    documentImage: string,
    pictureWithDocument: string,
    doctorImage: string,
    type: "licence" | "certificate";
    photoWithLicence: string
  }>,
  res: TypedResponse<ResponseBodyProps>
) => {


  try {

    const user = req.user
     
    
    
    const {
      fullName,LicenseNumber,license, expiration,
      country,
      docummentType,
      documentId,
      documentHoldName,
      documentImage,
      pictureWithDocument,
      doctorImage,
      type,
      photoWithLicence
    } = req.body;

    console.log(fullName)

    if (!fullName || !LicenseNumber || !license || !expiration ||
      !country || !docummentType ||
      !documentId  ||
      !documentHoldName ||
      !documentImage ||
      !pictureWithDocument ||
      !doctorImage || !type || !photoWithLicence) {
      res.status(SERVER_STATUS.BAD_REQUEST).json({
        title: "Upload Licence or Certificate",
        status: SERVER_STATUS.BAD_REQUEST,
        successful: false,
        message:
          " fullName,LicenseNumber,license, expiration,country,docummentType, documentId,documentHoldName,  documentImage,pictureWithDocument, doctorImage ,type and photoWithLicence fields are required to continue."
      });

      return;
    }

    if (type === "licence" && (!license || !photoWithLicence || !doctorImage || !documentImage || !pictureWithDocument)) {
      res.status(SERVER_STATUS.BAD_REQUEST).json({
        title: "Upload Licence or Certificate",
        status: SERVER_STATUS.BAD_REQUEST,
        successful: false,
        message: "license,photoWithLicence,doctorImage,documentImage and pictureWithDocument  fields are required to continue."
      });

      return;
    }




    /*if (type === "certificate" && (!certificateNo || !certificateImage)) {
      res.status(SERVER_STATUS.BAD_REQUEST).json({
        title: "Upload Licence or Certificate",
        status: SERVER_STATUS.BAD_REQUEST,
        successful: false,
        message:
          "certificateNo and certificateImage  fields are required to continue."
      });

      return;
    }*/


    const userDocument = await  MedicalPersonnelCertificationAndUploadModel.findOne({userId:user?._id })

    if(userDocument){
        
        if(type === "licence"){

                const regex = /^data:image\/(png|jpg|jpeg|gif|svg);base64,/i;
                     
                if(!regex.test(license!!) || !regex.test(photoWithLicence) || !regex.test(doctorImage) || !regex.test(documentImage) || !regex.test(pictureWithDocument) ){
                     
                             res.status(SERVER_STATUS.BAD_REQUEST).json({
                                 title: 'Upload Licence or Certificate',
                                 status: SERVER_STATUS.BAD_REQUEST,
                                 successful: false,
                                 message: 'Invalid image format provided. only png|jpg|jpeg|gif|svg is supported'
                             })
                     
                             return
                     
                          }



                        const licenceUrl = await new Promise<string>((resolve,reject)=>{
                                              uploader.upload(license!!,{
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

                                        const doctorImageUrl = await new Promise<string>((resolve,reject)=>{
                                          uploader.upload(doctorImage!!,{
                                              folder:user?._id.concat('/doctorImage')
                                           },(error,uploadedResult)=>{
                                              
                                              if(error){
                                                  reject(error.message)
                                              }
                      
                                              resolve(uploadedResult?.secure_url!!)
                                      
                                            
                                           })
                                      })

                                      const documentUrl = await new Promise<string>((resolve,reject)=>{
                                        uploader.upload(documentImage!!,{
                                            folder:user?._id.concat('/document')
                                         },(error,uploadedResult)=>{
                                            
                                            if(error){
                                                reject(error.message)
                                            }
                    
                                            resolve(uploadedResult?.secure_url!!)
                                    
                                          
                                         })
                                    })


                                    const photoWithDocumentUrl = await new Promise<string>((resolve,reject)=>{
                                      uploader.upload(pictureWithDocument!!,{
                                          folder:user?._id.concat('/photoWithDocument')
                                       },(error,uploadedResult)=>{
                                          
                                          if(error){
                                              reject(error.message)
                                          }
                  
                                          resolve(uploadedResult?.secure_url!!)
                                  
                                        
                                       })
                                  })



                  

            await userDocument.updateOne({
                licence:{
                    fullName:fullName??userDocument.licenseDetails?.fullName,
                     license:licenceUrl??userDocument.licenseDetails?.license,
                     LicenseNumber:LicenseNumber??userDocument.licenseDetails?.LicenseNumber,
                     expiration:expiration??userDocument.licenseDetails?.expiration,
                     country:country??userDocument.licenseDetails?.country,
                     docummentType:docummentType??userDocument.licenseDetails?.docummentType,
                     documentId:documentId??userDocument.licenseDetails?.documentId,
                     documentHoldName:documentHoldName??userDocument.licenseDetails?.documentHoldName,
                     documentImage:doctorImageUrl??userDocument.licenseDetails?.doctorImage,
                     pictureWithDocument:photoWithDocumentUrl??userDocument.licenseDetails?.pictureWithDocument,
                     doctorImage:doctorImageUrl??userDocument.licenseDetails?.doctorImage,
                     photoWithLicence:photoWithLicenceUrl??userDocument.licenseDetails?.photoWithLicence
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






      /*  if(type === "certificate"){


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






        }*/





    }else{


        if(type === "licence"){



            const regex = /^data:image\/(png|jpg|jpeg|gif|svg);base64,/i;
                     
            if(!regex.test(license!!) || !regex.test(photoWithLicence) || !regex.test(doctorImage) || !regex.test(documentImage) || !regex.test(pictureWithDocument)){
       
               res.status(SERVER_STATUS.BAD_REQUEST).json({
                   title: 'Upload Licence or Certificate',
                   status: SERVER_STATUS.BAD_REQUEST,
                   successful: false,
                   message: 'Invalid licence image format provided.'
               })
       
               return
       
            }

       
          const licenceUrl = await new Promise<string>((resolve,reject)=>{
                                uploader.upload(license!!,{
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

              

                            const doctorImageUrl = await new Promise<string>((resolve,reject)=>{
                              uploader.upload(doctorImage!!,{
                                  folder:user?._id.concat('/doctorImage')
                               },(error,uploadedResult)=>{
                                  
                                  if(error){
                                      reject(error.message)
                                  }
          
                                  resolve(uploadedResult?.secure_url!!)
                          
                                
                               })
                          })
                       
                          const documentUrl = await new Promise<string>((resolve,reject)=>{
                            uploader.upload(documentImage!!,{
                                folder:user?._id.concat('/document')
                             },(error,uploadedResult)=>{
                                
                                if(error){
                                    reject(error.message)
                                }
        
                                resolve(uploadedResult?.secure_url!!)
                        
                              
                             })
                        })

                       
                        const photoWithDocumentUrl = await new Promise<string>((resolve,reject)=>{
                          uploader.upload(documentImage!!,{
                              folder:user?._id.concat('/photoWithDocument')
                           },(error,uploadedResult)=>{
                              
                              if(error){
                                  reject(error.message)
                              }
      
                              resolve(uploadedResult?.secure_url!!)
                      
                            
                           })
                      })

                    

                         



            
          const newDocument =      await new MedicalPersonnelCertificationAndUploadModel({
                                userId:user?._id,
             licenseDetails:{
              fullName,
                     license:licenceUrl,
                     LicenseNumber,
                     expiration,
                     country,
                     docummentType,
                     documentId,
                     documentHoldName,
                     documentImage:doctorImageUrl,
                     pictureWithDocument:photoWithDocumentUrl,
                     doctorImage:doctorImageUrl,
                     photoWithLicence:photoWithLicenceUrl
                
          
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





       /* if(type === "certificate"){




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
                     isVerified:true
                }
            
            }).save()

            res.status(SERVER_STATUS.SUCCESS).json({
                title: 'Upload Licence or Certificate',
                status: SERVER_STATUS.SUCCESS,
                successful: true,
                message: 'Successfully uploaded.',
                data:newDocument
            })


        }*/

        

       

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
