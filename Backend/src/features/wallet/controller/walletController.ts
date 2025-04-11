import { RequestBody } from "swagger-jsdoc"
import TypedRequest from "../../../util/interface/TypedRequest"
import TypedResponse from "../../../util/interface/TypedResponse"
import { ResponseBodyProps } from "../../../util/interface/ResponseBodyProps"
import SERVER_STATUS from "../../../util/interface/CODE"
import { encryptAES256 } from "../../../util/encryptData"
import  childProcess  from "child_process"



interface CardPaymentInterface {
    name:string,
   number:string,
   cvv:string,
  expiry_month:string,
   expiry_year:string,
    pin: string,
    paymentMadeBy:string,
    paymentReceiver:string,
    amount:number,
    currency:'NGN',
    customerName:string,
    customerEmail:string

}

const makePaymentWithCard = async (req:TypedRequest<CardPaymentInterface>,res:TypedResponse<ResponseBodyProps>) => {
    const url = "https://api.korapay.com/merchant/api/v1/charges/card"

    const {cvv,expiry_month,expiry_year,name,number,paymentMadeBy,paymentReceiver,pin,amount,
        currency,
        customerName,
        customerEmail} = req.body
     
    if(!cvv || !expiry_month || !expiry_year || name || !number || !paymentMadeBy || !paymentReceiver || currency ||
        customerName
       || customerEmail){

        res.status(SERVER_STATUS.BAD_REQUEST).json({
            title:'Card Payment Message',
            status:SERVER_STATUS.BAD_REQUEST,
            successful:false,
            message:'cvv,expiry_month,expiry_year,name,number,paymentMadeBy, paymentReceiver,currency, customerName and customerEmail fields are needed to continue. ',
        

        })

        return
    }



  const data =  {
        reference:paymentMadeBy.concat(paymentReceiver), // must be at least 8 characters
        "card": {
            name,
            number,
            cvv,
            expiry_month,
            expiry_year,
            pin // optional
        },
        "amount":amount,
        "currency": currency,
        "redirect_url": "https://merchant-redirect-url.com",
        "customer": {
            "name": customerName,
            "email": customerEmail
        },
        
    }



    
}


export const testFlow  = async () =>{
     const url = "https://api.korapay.com/merchant/api/v1/charges/card"
     
    const d = {
        "reference": "test-card-payment-1", // must be at least 8 characters
        "card": {
              "name": "",
            "number": "4084127883172787",
            "cvv": "123",
            "expiry_month": "09",
            "expiry_year": "30",
            "pin": "" // optional
        },
        "amount": 1000,
        "currency": "NGN",
        "redirect_url": "https://webhook.site/3f09d5de-3642-4ce7-ae10-dc7579532494",
        "customer": {
            "name": "John Doe",
            "email": "johndoe@korapay.com"
        }
        
    }

try{
    const data = await encryptAES256(JSON.stringify(d))
console.log(data)
   
/**
 *  fetch(url,{
        method:'post',
        headers:{
         Authorization:` Bearer ${process.env.kora_payment_gateway_sec}` 
        },
        
        body:"{charge_data:'jdjd'}"
    }).then(res=>{
        return res.json()
    }).then((result)=>{
        console.log(result)
    }).catch(err=>{
        console.log(err)
    })
 */

    const curlCommand =  `  curl --request POST \   --url https://api.korapay.com/merchant/api/v1/charges/card        --header  'Authorization:  Bearer ${process.env.kora_payment_gateway_sec}' \  --data '{ 'charge_data':'${data}' }'  `

    childProcess.exec(curlCommand,(err,stdout,stderr)=>{
        if(err){
            console.log(err)
            return
        }
        console.log(stdout)
    })
    /**
     * curl --request POST \
     --url https://api.korapay.com/merchant/api/v1/charges/card \
     --header 'Authorization: Bearer sk_test_hf3Kz9TLbscoR7Nwt1Log1B2xHaF5ugrUKmdwmh8' \
     --data '{
        "charge_data": c62ac600880756fa9456e812dbbaccc8:14ed28362057615390765db7eb6a9f4630f12d23c67ad462621cd7e8cc:f2197fe1911162010cefa3038a12188f}'
     */

}catch(e){
    
}

   
}