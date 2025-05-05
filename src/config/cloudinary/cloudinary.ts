   import { v2 as cloudinary} from 'cloudinary'
  import dotevn from "dotenv"
  dotevn.config()


   cloudinary.config({
    cloud_name:process.env.cloud_name,
    api_key:process.env.api_key,
    api_secret:process.env.api_secret
   })


   
   export default cloudinary.uploader
   


   