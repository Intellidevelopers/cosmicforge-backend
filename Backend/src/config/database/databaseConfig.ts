
import mongoose from 'mongoose'

 let  LOCAL_DB_URL = "mongodb://localhost:27017/cosmicbacken"
 let  STAGING_URL = "mongodb+srv://CosmicForge:DevTeam1234@cluster0.amtdi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0";


// Create a MongoClient with a MongoClientOptions object to set the Stable API version

 export  const connectDB = async () =>{
   return mongoose.connect(STAGING_URL)
 } 
