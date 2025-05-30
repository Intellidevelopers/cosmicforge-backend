import uploader from "../../../../config/cloudinary/cloudinary";
import sendMail from "../../../../config/mail/nodeMailer";
import SERVER_STATUS from "../../../../util/interface/CODE";
import { ResponseBodyProps } from "../../../../util/interface/ResponseBodyProps";
import TypedRequest from "../../../../util/interface/TypedRequest";
import TypedResponse from "../../../../util/interface/TypedResponse";
import newUserModel from "../../../newUser/model/newUserModel";
import MedicalPersonnelProfileModel from "../../profile/model/profileModel";
import MedicalPersonnelCertificationAndUploadModel from "../model/MedicalPersonnelCertModel";
import jwt from 'jsonwebtoken'
import path from 'path'

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
    photoWithLicence: string,


    institution: string,
    certificateNo: string,
    date: string,
    certificate: string,
    photoWithCertification: string
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
      photoWithLicence,
      institution,certificateNo,date,certificate,photoWithCertification
    } = req.body;

   

    if (!type ) {
      res.status(SERVER_STATUS.BAD_REQUEST).json({
        title: "Upload Licence or Certificate",
        status: SERVER_STATUS.BAD_REQUEST,
        successful: false,
        message:
          " type field are required to continue."
      });

      return;
    }

    if (type === "licence" && (!fullName || !LicenseNumber || !license || !expiration ||
      !country || !docummentType ||
      !documentId  ||
      !documentHoldName ||
      !documentImage ||
      !pictureWithDocument  || !photoWithLicence || !doctorImage)) {
      res.status(SERVER_STATUS.BAD_REQUEST).json({
        title: "Upload Licence or Certificate",
        status: SERVER_STATUS.BAD_REQUEST,
        successful: false,
        message: "fullName,LicenseNumber,license, expiration,country,docummentType, documentId,documentHoldName,  documentImage,pictureWithDocument, doctorImage ,type,photoWithLicence,doctorImage,documentImage and pictureWithDocument  fields are required to continue."
      });

      return;
    }

  



    if (type === "certificate" && (!fullName || !country || !docummentType ||
      !documentId  ||
      !documentHoldName ||
      !documentImage ||
      !pictureWithDocument  || !doctorImage ||  !institution || !certificateNo || !date || !certificate || !photoWithCertification)) {
     
        res.status(SERVER_STATUS.BAD_REQUEST).json({
        title: "Upload Licence or Certificate",
        status: SERVER_STATUS.BAD_REQUEST,
        successful: false,
        message:
          "fullName,country,docummentType,documentId,documentHoldName,documentImage, pictureWithDocument, doctorImage, institution,certificateNo,certificate, photoWithCertification fields are required to continue."
      });

      return;
    }


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
                licenseDetails:{
                    fullName:fullName??userDocument.licenseDetails?.fullName,
                     license:licenceUrl??userDocument.licenseDetails?.license,
                     LicenseNumber:LicenseNumber??userDocument.licenseDetails?.LicenseNumber,
                     expiration:expiration??userDocument.licenseDetails?.expiration,
                     country:country??userDocument.licenseDetails?.country,
                     docummentType:docummentType??userDocument.licenseDetails?.docummentType,
                     documentId:documentId??userDocument.licenseDetails?.documentId,
                     documentHoldName:documentHoldName??userDocument.licenseDetails?.documentHoldName,
                     documentImage:documentUrl??userDocument.licenseDetails?.documentImage,
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


            /**
             * send mail to cosmicforge for verification
             */

              const verificationTokenForApproval = jwt.sign({verificationId:user?._id,license:userDocument.licenseDetails?.license,
                status:'approved'
              },process.env.JWT_SECRET!!,{algorithm:'HS256'})

              const verificationTokenForDisApproval = jwt.sign({verificationId:user?._id,license:userDocument.licenseDetails?.license,
                status:'disapproved'
              },process.env.JWT_SECRET!!,{algorithm:'HS256'})


              const urlForApproval =`${process.env.backend_base_url}/user/medics/certification/verification?token=${verificationTokenForApproval}`
            
               const urlForDisApproval =`${process.env.backend_base_url}/user/medics/certification/verification?token=${verificationTokenForDisApproval}`

            
              await sendMail({receiver:'noreply@cosmicforgehealthnet.com',subject:"Doctor Requesting for Verification.",emailData:{
                        fullName:`${fullName}`,
                        license:licenceUrl??userDocument.licenseDetails?.license,
                        LicenseNumber:LicenseNumber??userDocument.licenseDetails?.LicenseNumber,
                        expiration:expiration??userDocument.licenseDetails?.expiration,
                        country:country??userDocument.licenseDetails?.country,
                        docummentType:docummentType??userDocument.licenseDetails?.docummentType,
                        documentId:documentId??userDocument.licenseDetails?.documentId,
                        documentHoldName:documentHoldName??userDocument.licenseDetails?.documentHoldName,
                        documentImage:documentUrl??userDocument.licenseDetails?.documentImage,
                        pictureWithDocument:photoWithDocumentUrl??userDocument.licenseDetails?.pictureWithDocument,
                        doctorImage:doctorImageUrl??userDocument.licenseDetails?.doctorImage,
                        photoWithLicence:photoWithLicenceUrl??userDocument.licenseDetails?.photoWithLicence,
                        verificationId:user?._id,
                        timeStamp:new Date().toISOString(),
                        urlForApproval,
                        urlForDisApproval
                 

                    },template:"doctor-verification.ejs"})


                  



        }






       if(type === "certificate"){


            const regex = /^data:image\/(png|jpg|jpeg|gif|svg);base64,/i;
                     
            if(!regex.test(certificate!!) || !regex.test(photoWithCertification) || !regex.test(doctorImage) || !regex.test(documentImage) || !regex.test(pictureWithDocument) ){
       
               res.status(SERVER_STATUS.BAD_REQUEST).json({
                   title: 'Upload Licence or Certificate',
                   status: SERVER_STATUS.BAD_REQUEST,
                   successful: false,
                   message: 'Invalid certification image format provided.'
               })
       
               return
       
            }



          const certUrl = await new Promise<string>((resolve,reject)=>{
                                uploader.upload(certificate!!,{
                                    folder:user?._id.concat('/certificate')
                                 },(error,uploadedResult)=>{
                                    
                                    if(error){
                                        reject(error.message)
                                    }
            
                                    resolve(uploadedResult?.secure_url!!)
                            
                                  
                                 })
                            })

                            const photoWithCertUrl = await new Promise<string>((resolve,reject)=>{
                              uploader.upload(photoWithCertification!!,{
                                  folder:user?._id.concat('/certificate')
                               },(error,uploadedResult)=>{
                                  
                                  if(error){
                                      reject(error.message)
                                  }
          
                                  resolve(uploadedResult?.secure_url!!)
                          
                                
                               })
                          })


                          const certDocUrl = await new Promise<string>((resolve,reject)=>{
                            uploader.upload(certificate!!,{
                                folder:user?._id.concat('/certificateDoc')
                             },(error,uploadedResult)=>{
                                
                                if(error){
                                    reject(error.message)
                                }
        
                                resolve(uploadedResult?.secure_url!!)
                        
                              
                             })
                        })

                        const photoWithCertDocUrl = await new Promise<string>((resolve,reject)=>{
                          uploader.upload(photoWithCertification!!,{
                              folder:user?._id.concat('/photoWithCertificate')
                           },(error,uploadedResult)=>{
                              
                              if(error){
                                  reject(error.message)
                              }
      
                              resolve(uploadedResult?.secure_url!!)
                      
                            
                           })
                      })


      
                          








            await userDocument.updateOne({
                certificationDetails:{
                    fullName:fullName??userDocument.certificationDetails?.fullName,
                     institution:institution??userDocument.certificationDetails?.institution,
                     certificateNo:certificateNo??userDocument.certificationDetails?.certificateNo,
                     certificate:certUrl??userDocument.certificationDetails?.certificate,
                     date:date??userDocument.certificationDetails?.date,
                     country:country??userDocument.licenseDetails?.country,
                     docummentType:docummentType??userDocument.certificationDetails?.docummentType,
                     documentId:documentId??userDocument.certificationDetails?.documentId,
                     documentHoldName:documentHoldName??userDocument.certificationDetails?.documentHoldName,
                     documentImage:documentImage??userDocument.certificationDetails?.documentImage,
                     pictureWithDocument:photoWithCertDocUrl??userDocument.certificationDetails?.pictureWithDocument,
                    photoWithCertification:photoWithCertUrl??userDocument.certificationDetails?.photoWithCertification,
                    doctorImage:certDocUrl??userDocument.certificationDetails?.doctorImage
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


            

         await MedicalPersonnelProfileModel.findOneAndUpdate({_id:user?._id},{certificationDetails:newDocument._id})
       



            res.status(SERVER_STATUS.SUCCESS).json({
                title: 'Upload Licence or Certificate',
                status: SERVER_STATUS.SUCCESS,
                successful: true,
                message: 'Successfully uploaded.',
                data:newDocument
            })


        
            /**
             * send mail to cosmicforge for verification
             */

             

              const verificationTokenForApproval = jwt.sign({verificationId:user?._id,license:license,
                status:'approved'
              },process.env.JWT_SECRET!!,{algorithm:'HS256'})

              const verificationTokenForDisApproval = jwt.sign({verificationId:user?._id,license:license,
                status:'disapproved'
              },process.env.JWT_SECRET!!,{algorithm:'HS256'})


              const urlForApproval =`${process.env.backend_base_url}/user/medics/certification/verification?token=${verificationTokenForApproval}`
            
               const urlForDisApproval =`${process.env.backend_base_url}/user/medics/certification/verification?token=${verificationTokenForDisApproval}`

            await sendMail({receiver:'noreply@cosmicforgehealthnet.com',subject:"Doctor Requesting for Verification.",emailData:{
              fullName:`${fullName}`,
              license:license,
              LicenseNumber:LicenseNumber,
              expiration:expiration,
              country:country,
              docummentType:docummentType,
              documentId:documentId,
              documentHoldName:documentHoldName,
              documentImage:documentImage,
              pictureWithDocument:pictureWithDocument,
              doctorImage:doctorImage,
              photoWithLicence:photoWithLicence,
              verificationID:user?._id,
              timeStamp:new Date().toISOString(),
              urlForApproval,
              urlForDisApproval
       

          },template:"doctor-verification.ejs"})

        
        }





       if(type === "certificate"){




            const regex = /^data:image\/(png|jpg|jpeg|gif|svg);base64,/i;
                     
            if(!regex.test(certificate!!) || !regex.test(photoWithCertification) || !regex.test(doctorImage) || !regex.test(documentImage) || !regex.test(pictureWithDocument)){
       
               res.status(SERVER_STATUS.BAD_REQUEST).json({
                   title: 'Upload Licence or Certificate',
                   status: SERVER_STATUS.BAD_REQUEST,
                   successful: false,
                   message: 'Invalid certification image format provided.'
               })
       
               return
       
            }



         
            const certUrl = await new Promise<string>((resolve,reject)=>{
              uploader.upload(certificate!!,{
                  folder:user?._id.concat('/certificate')
               },(error,uploadedResult)=>{
                  
                  if(error){
                      reject(error.message)
                  }

                  resolve(uploadedResult?.secure_url!!)
          
                
               })
          })

          const photoWithCertUrl = await new Promise<string>((resolve,reject)=>{
            uploader.upload(photoWithCertification!!,{
                folder:user?._id.concat('/certificate')
             },(error,uploadedResult)=>{
                
                if(error){
                    reject(error.message)
                }

                resolve(uploadedResult?.secure_url!!)
        
              
             })
        })


        const certDocUrl = await new Promise<string>((resolve,reject)=>{
          uploader.upload(certificate!!,{
              folder:user?._id.concat('/certificateDoc')
           },(error,uploadedResult)=>{
              
              if(error){
                  reject(error.message)
              }

              resolve(uploadedResult?.secure_url!!)
      
            
           })
      })

      const photoWithCertDocUrl = await new Promise<string>((resolve,reject)=>{
        uploader.upload(photoWithCertification!!,{
            folder:user?._id.concat('/photoWithCertificate')
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
                certificationDetails:{
                  fullName:fullName,
                  institution:institution,
                  certificateNo:certificateNo,
                  certificate:certUrl,
                  date:date,
                  country:country,
                  docummentType:docummentType,
                  documentId:documentId,
                  documentHoldName:documentHoldName,
                  documentImage:documentImage,
                  pictureWithDocument:photoWithCertDocUrl,
                 photoWithCertification:photoWithCertUrl,
                 doctorImage:certDocUrl
         
                 
                }
            
            }).save()


               await MedicalPersonnelProfileModel.findOneAndUpdate({_id:user?._id},{certificationDetails:newDocument._id})
       

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



export  const  approveDoctorLicenseVerification = async (req:TypedRequest<{doctorId:string,}>,res:TypedResponse<ResponseBodyProps>) =>{


     const tokenQuery = req.query.token as string

     

    try {

       if(!tokenQuery){

        res.status(SERVER_STATUS.BAD_REQUEST).json({
            title:"Verification",
            status:SERVER_STATUS.BAD_REQUEST,
            successful:false,
            message:'Failed to process request.'
        })

        return
     }


     const  token = jwt.verify(tokenQuery!!,process.env.JWT_SECRET!!) as {verificationId:string,license:string,status:'approved'|'disapproved' }

    

     if(!token.verificationId || !token.license || !token.status){


        res.status(SERVER_STATUS.BAD_REQUEST).json({
            title:"Verification",
            status:SERVER_STATUS.BAD_REQUEST,
            successful:false,
            message:'Failed to process request.'
        })

        return
     }


     if(token.status === 'approved'){

        const doctorDetails = await  MedicalPersonnelCertificationAndUploadModel.findOne({
      userId:token.verificationId,
      
     })

    


     if(!doctorDetails){
        res.status(SERVER_STATUS.BAD_REQUEST).json({
            title:"Verification",
            status:SERVER_STATUS.BAD_REQUEST,
            successful:false,
            message:'Failed to process request.'
        })

        return
     }

     
      const doctorData = await newUserModel.findOne({
      _id:doctorDetails?.userId
     })

     await doctorDetails.updateOne({
       'licenseDetails.isVerified':true
     })


     res.status(SERVER_STATUS.SUCCESS).render(path.join(path.resolve(__dirname, "../../../../"),'views','approvedLicenseTemplate.ejs'))
     
     await  sendMail({receiver: `${doctorData?.email}`,subject:"Doctor Verification .",emailData:{
          
        },template:"approvedLicenseTemplate.ejs"})

      
     }

   
      
    } catch (error:any) {

       res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
            title:"Verification",
            status:SERVER_STATUS.INTERNAL_SERVER_ERROR,
            successful:false,
            message:'Error occured.',
            error:error.message
        })

      
    }


     



}
