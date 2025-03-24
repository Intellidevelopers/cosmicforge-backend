import crypto from 'crypto'



export  const  encryptAES256 = async (paymentData:any) => {

    const iv = crypto.randomBytes(16)
    const cipher = crypto.createCipheriv('aes-256-gcm',process?.env?.kora_payment_gateway_enc!!,iv)

    const encrypted = cipher.update(paymentData);
    
    const ivToHex = iv.toString('hex');
    const encryptedToHex = Buffer.concat([encrypted, cipher.final()]).toString('hex');
    
    return `${ivToHex}:${encryptedToHex}:${cipher.getAuthTag().toString('hex')}`;
}