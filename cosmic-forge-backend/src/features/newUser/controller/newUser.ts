import SERVER_STATUS from "../../../util/interface/CODE"
import { ResponseBodyProps } from "../../../util/interface/ResponseBodyProps"
import TypedRequest from "../../../util/interface/TypedRequest"
import TypedResponse from "../../../util/interface/TypedResponse"



import UsersModel from '../../../features/newUser/model/newUserModel'
import OTPModel from '../model/otpVerificationModel'
import generateOTP from "../../../util/otpGenerator"
import sendMail from "../../../config/mail/nodeMailer"



export interface RequestBodyProps {
    email?: string
}

export const registerNewUser = async (req: TypedRequest<RequestBodyProps>, res: TypedResponse<ResponseBodyProps>) => {

   

    
    try {
        

        const {email} = req.body

    if (!email) {
        return res.status(SERVER_STATUS.BAD_REQUEST).json({
            title: "Register User Message",
            status: SERVER_STATUS.BAD_REQUEST,
            successful: false,
            message: "Email field is required to continue."

        })
    }

    console.log(await UsersModel.findOne({ email }))
    const isEmailAlreadyRegistered = await UsersModel.findOne({ email })

    if (isEmailAlreadyRegistered) {
        return res.status(SERVER_STATUS.BAD_REQUEST).json({
            title: "Register User Message",
            status: SERVER_STATUS.BAD_REQUEST,
            successful: false,
            message: "Email provided already registered."
        })
    }
    
    await OTPModel.deleteMany()

        const isUserAlreadySentOtp = await OTPModel.findOne({ "userDetails.email": email })
           
        if (isUserAlreadySentOtp) {

            return res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: "Register User Message",
                status: SERVER_STATUS.BAD_REQUEST,
                successful: false,
                message: "Already sent otp to email and verify otp and complete rigration."
            })

            return
        }

        //send user otp
        const otp = await generateOTP()

        const storeOTP = new OTPModel({
            userDetails: {
                email
            },
            expiringTime: new Date(Date.now() + 3 * 60 * 1000),
            otpCode: otp

        })

        await storeOTP.save()

        sendMail({
            receiver: email,
            subject: "Otp Code For Registration",
              emailData:{
                email,
                otp
              },
            template:'send-user-otp.ejs'
        }).then(result => {
            res.status(SERVER_STATUS.SUCCESS).json({
                title: 'Register new user message',
                successful: true,
                status: SERVER_STATUS.SUCCESS,
                message: "Otp sent to user.",


            })

        }).catch(err => {
            res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
                title: 'Register new user message',
                successful: false,
                status: SERVER_STATUS.INTERNAL_SERVER_ERROR,
                message: "An error occured.",
                error: err.message

            })
        })

    } catch (error: any) {

        res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
            title: 'Register new user message',
            successful: false,
            status: SERVER_STATUS.INTERNAL_SERVER_ERROR,
            message: "An error occured.",
            error: error.message

        })


    }












}

const resendOTP = async (req: TypedRequest<RequestBodyProps>, res: TypedResponse<ResponseBodyProps>) => {

    const { email } = req.body


    try {

        const isUserAlreadySentOtp = await OTPModel.findOne({ "userDetails.email": email })

        if (!isUserAlreadySentOtp) {

            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: 'Register new user message',
                successful: false,
                status: SERVER_STATUS.INTERNAL_SERVER_ERROR,
                message: "An error occured.",



            })

            return
        }


    } catch (error) {

    }


}



