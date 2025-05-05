import mongoose from "mongoose"
import SERVER_STATUS from "../../../util/interface/CODE"
import { ResponseBodyProps } from "../../../util/interface/ResponseBodyProps"
import TypedRequest from "../../../util/interface/TypedRequest"
import TypedResponse from "../../../util/interface/TypedResponse"
import PatientProfileModel from "../../patient/profile/model/patientProfileModel"
import { RatingsAndReviewsModel } from "../model/ratingsAndReviewsModel"
import newUserModel from "../../newUser/model/newUserModel"
import { USER_ROLES } from "../../../util/interface/UserRole"


 interface RatingsAndReviewsProps {
    rating:number,
    review?:string,
    doctorId:string

 }


export const  rate_and_review_a_doctor =   async (req:TypedRequest<RatingsAndReviewsProps>,res:TypedResponse<ResponseBodyProps>) =>{

  try {

    const user = req.user

    if(!user){
        res.status(SERVER_STATUS.Forbidden).json({
            title:"Ratings And Review Message.",
            status:SERVER_STATUS.Forbidden,
            successful:false,
            message:"You are not authorized"
        })
        return
    }

    if(user.role !== USER_ROLES.CLIENT.toString()){

        res.status(SERVER_STATUS.UNAUTHORIZED).json({
            title:"Ratings And Review Message.",
            status:SERVER_STATUS.UNAUTHORIZED,
            successful:false,
            message:"you are not authorized"
        })
        return
    }

    const {doctorId,rating,review} = req.body

     if(!doctorId || !rating){
        res.status(SERVER_STATUS.BAD_REQUEST).json({
            title:"Ratings And Review Message.",
            status:SERVER_STATUS.BAD_REQUEST,
            successful:false,
            message:"Atleast doctorId and rating  fields are needed to continue."
        })
        return
     }

     const isDoctorIdValid =  mongoose.Types.ObjectId.isValid(doctorId)

     if(!isDoctorIdValid){
        res.status(SERVER_STATUS.BAD_REQUEST).json({
            title:"Ratings And Review Message.",
            status:SERVER_STATUS.BAD_REQUEST,
            successful:false,
            message:"Invalid id provided."
        })
        return 
     }
     const isDoctorRegistered = await newUserModel.findOne({_id:doctorId})

     if( !isDoctorRegistered || isDoctorRegistered.role !== USER_ROLES.DOCTOR.toString()){
        res.status(SERVER_STATUS.BAD_REQUEST).json({
            title:"Ratings And Review Message.",
            status:SERVER_STATUS.BAD_REQUEST,
            successful:false,
            message:"Account not registered."
        })
        return
     }

    const userProfile = await PatientProfileModel.findOne({userId:user._id})

      let isReviewedAlready = await RatingsAndReviewsModel.findOne({
        doctorReviewed:doctorId,
        patientReviewing:user._id
      })

      if(isReviewedAlready){

        isReviewedAlready =  await isReviewedAlready.updateOne({
            rating:rating,
            rewiew: review ?? isReviewedAlready.rewiew,
        },{ new:true})

        res.status(SERVER_STATUS.SUCCESS).json({
            title:"Ratings And Review Message.",
            status:SERVER_STATUS.SUCCESS,
            successful:true,
            message:"Successfully.",
            data:isReviewedAlready
        })
        return
      }
    
    const rateAndReview = new RatingsAndReviewsModel({
        doctorReviewed:doctorId,
        patientReviewing:user._id,
        patienFullName:`${user.lastName} ${user.lastName}`,
        patientProfile:userProfile?.profilePicture,
        rewiew: review ?? '',
        rating:rating

    })

     await rateAndReview.save()

     res.status(SERVER_STATUS.SUCCESS).json({
        title:"Ratings And Review Message.",
        status:SERVER_STATUS.SUCCESS,
        successful:true,
        message:"Successfully.",
        data:rateAndReview
    })

    
  } catch (error:any) {
    res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
        title:"Ratings And Review Message.",
        status:SERVER_STATUS.INTERNAL_SERVER_ERROR,
        successful:false,
        message:"Internal Server Error.",
        error:error.message
    }) 
  }

}


export const get_1_star_ratings  =  async (req:TypedRequest<any>,res:TypedResponse<ResponseBodyProps>) =>{

    try {

        const user = req.user

        if(!user){
            res.status(SERVER_STATUS.Forbidden).json({
                title:"Ratings And Review Message.",
                status:SERVER_STATUS.Forbidden,
                successful:false,
                message:"You are not authorized"
            })
            return
        }
    
        if(user.role !== USER_ROLES.CLIENT.toString()){
    
            res.status(SERVER_STATUS.UNAUTHORIZED).json({
                title:"Ratings And Review Message.",
                status:SERVER_STATUS.UNAUTHORIZED,
                successful:false,
                message:"you are not authorized"
            })
            return
        }
    

        const OneStarRating = await RatingsAndReviewsModel.find({rating:1})

        res.status(SERVER_STATUS.SUCCESS).json({
            title:"Ratings And Review Message.",
            status:SERVER_STATUS.SUCCESS,
            successful:true,
            message:"Successfully.",
            data:{
                total:OneStarRating.length,
                ratings:OneStarRating
            }
        })
        
    } catch (error:any) {
        res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
            title:"Ratings And Review Message.",
            status:SERVER_STATUS.INTERNAL_SERVER_ERROR,
            successful:false,
            message:"Internal Server Error.",
            error:error.message
        })  
    }

}


export const get_2_star_ratings  =  async (req:TypedRequest<any>,res:TypedResponse<ResponseBodyProps>) =>{

    try {

        const user = req.user

        if(!user){
            res.status(SERVER_STATUS.Forbidden).json({
                title:"Ratings And Review Message.",
                status:SERVER_STATUS.Forbidden,
                successful:false,
                message:"You are not authorized"
            })
            return
        }
    
        if(user.role !== USER_ROLES.CLIENT.toString()){
    
            res.status(SERVER_STATUS.UNAUTHORIZED).json({
                title:"Ratings And Review Message.",
                status:SERVER_STATUS.UNAUTHORIZED,
                successful:false,
                message:"you are not authorized"
            })
            return
        }
    

        const twoStarRatings = await RatingsAndReviewsModel.find({rating:2})

        res.status(SERVER_STATUS.SUCCESS).json({
            title:"Ratings And Review Message.",
            status:SERVER_STATUS.SUCCESS,
            successful:true,
            message:"Successfully.",
            data:{
                total:twoStarRatings.length,
                ratings:twoStarRatings
            }
        })
        
    } catch (error:any) {
        res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
            title:"Ratings And Review Message.",
            status:SERVER_STATUS.INTERNAL_SERVER_ERROR,
            successful:false,
            message:"Internal Server Error.",
            error:error.message
        })  
    }

}

export const get_3_star_ratings  =  async (req:TypedRequest<any>,res:TypedResponse<ResponseBodyProps>) =>{

    try {

        const user = req.user

        if(!user){
            res.status(SERVER_STATUS.Forbidden).json({
                title:"Ratings And Review Message.",
                status:SERVER_STATUS.Forbidden,
                successful:false,
                message:"You are not authorized"
            })
            return
        }
    
        if(user.role !== USER_ROLES.CLIENT.toString()){
    
            res.status(SERVER_STATUS.UNAUTHORIZED).json({
                title:"Ratings And Review Message.",
                status:SERVER_STATUS.UNAUTHORIZED,
                successful:false,
                message:"you are not authorized"
            })
            return
        }
    

        const twoStarRatings = await RatingsAndReviewsModel.find({rating:3})

        res.status(SERVER_STATUS.SUCCESS).json({
            title:"Ratings And Review Message.",
            status:SERVER_STATUS.SUCCESS,
            successful:true,
            message:"Successfully.",
            data:{
                total:twoStarRatings.length,
                ratings:twoStarRatings
            }
        })
        
    } catch (error:any) {
        res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
            title:"Ratings And Review Message.",
            status:SERVER_STATUS.INTERNAL_SERVER_ERROR,
            successful:false,
            message:"Internal Server Error.",
            error:error.message
        })  
    }

}

export const get_4_star_ratings  =  async (req:TypedRequest<any>,res:TypedResponse<ResponseBodyProps>) =>{

    try {

        const user = req.user

        if(!user){
            res.status(SERVER_STATUS.Forbidden).json({
                title:"Ratings And Review Message.",
                status:SERVER_STATUS.Forbidden,
                successful:false,
                message:"You are not authorized"
            })
            return
        }
    
        if(user.role !== USER_ROLES.CLIENT.toString()){
    
            res.status(SERVER_STATUS.UNAUTHORIZED).json({
                title:"Ratings And Review Message.",
                status:SERVER_STATUS.UNAUTHORIZED,
                successful:false,
                message:"you are not authorized"
            })
            return
        }
    

        const fourStarRatings = await RatingsAndReviewsModel.find({rating:4})

        res.status(SERVER_STATUS.SUCCESS).json({
            title:"Ratings And Review Message.",
            status:SERVER_STATUS.SUCCESS,
            successful:true,
            message:"Successfully.",
            data:{
                total:fourStarRatings.length,
                ratings:fourStarRatings
            }
        })
        
    } catch (error:any) {
        res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
            title:"Ratings And Review Message.",
            status:SERVER_STATUS.INTERNAL_SERVER_ERROR,
            successful:false,
            message:"Internal Server Error.",
            error:error.message
        })  
    }

}

export const get_5_star_ratings  =  async (req:TypedRequest<any>,res:TypedResponse<ResponseBodyProps>) =>{

    try {

        const user = req.user

        if(!user){
            res.status(SERVER_STATUS.Forbidden).json({
                title:"Ratings And Review Message.",
                status:SERVER_STATUS.Forbidden,
                successful:false,
                message:"You are not authorized"
            })
            return
        }
    
        if(user.role !== USER_ROLES.CLIENT.toString()){
    
            res.status(SERVER_STATUS.UNAUTHORIZED).json({
                title:"Ratings And Review Message.",
                status:SERVER_STATUS.UNAUTHORIZED,
                successful:false,
                message:"you are not authorized"
            })
            return
        }
    

        const fiveStarRatings = await RatingsAndReviewsModel.find({rating:5})

        res.status(SERVER_STATUS.SUCCESS).json({
            title:"Ratings And Review Message.",
            status:SERVER_STATUS.SUCCESS,
            successful:true,
            message:"Successfully.",
            data:{
                total:fiveStarRatings.length,
                ratings:fiveStarRatings
            }
        })
        
    } catch (error:any) {
        res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
            title:"Ratings And Review Message.",
            status:SERVER_STATUS.INTERNAL_SERVER_ERROR,
            successful:false,
            message:"Internal Server Error.",
            error:error.message
        })  
    }

}

export const getRatings  =  async (req:TypedRequest<any>,res:TypedResponse<ResponseBodyProps>) =>{

    try {

        const user = req.user

        if(!user){
            res.status(SERVER_STATUS.Forbidden).json({
                title:"Ratings And Review Message.",
                status:SERVER_STATUS.Forbidden,
                successful:false,
                message:"You are not authorized"
            })
            return
        }
    
        if(user.role !== USER_ROLES.CLIENT.toString()){
    
            res.status(SERVER_STATUS.UNAUTHORIZED).json({
                title:"Ratings And Review Message.",
                status:SERVER_STATUS.UNAUTHORIZED,
                successful:false,
                message:"you are not authorized"
            })
            return
        }
    

        const allRatings = await RatingsAndReviewsModel.find()

        res.status(SERVER_STATUS.SUCCESS).json({
            title:"Ratings And Review Message.",
            status:SERVER_STATUS.SUCCESS,
            successful:true,
            message:"Successfully.",
            data:{
                total:allRatings.length,
                ratings:allRatings
            }
        })
        
    } catch (error:any) {
        res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
            title:"Ratings And Review Message.",
            status:SERVER_STATUS.INTERNAL_SERVER_ERROR,
            successful:false,
            message:"Internal Server Error.",
            error:error.message
        })  
    }

}

