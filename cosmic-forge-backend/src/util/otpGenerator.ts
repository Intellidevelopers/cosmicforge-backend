
const generateOTP =  async () => {
    let otp = Math.floor(Math.random()*999999)

    while(otp<6){
        otp = Math.floor(Math.random()*999999)
    }

    return otp
}


export default generateOTP