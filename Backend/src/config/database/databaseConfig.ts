
 import mongoose from "mongoose";

 let  LOCAL_DB_URL = "mongodb://localhost:27017/cosmicbacken"

 export  const connectDB = async () =>{
   return mongoose.connect(LOCAL_DB_URL)
 } 
