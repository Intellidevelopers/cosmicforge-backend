
import mongoose from 'mongoose'
//mongodb+srv://CosmicForge:DevTeam1234@cluster0.amtdi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
 let  LOCAL_DB_URL = "mongodb://localhost:27017/cosmicbacken"
 let  STAGING_URL = "mongodb+srv://cosmicforgehealthnetDb:ew6EOylqK6oAVm3o@cosmicforge1.ouy8f.mongodb.net/CosmicForgeDb?retryWrites=true&w=majority&appName=Cosmicforge1";


// Create a MongoClient with a MongoClientOptions object to set the Stable API version

 export  const connectDB = async () =>{
 
  const source = "mongodb+srv://CosmicForge:DevTeam1234@cluster0.amtdi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
  //const target = "mongodb+srv://cosmicforgehealthnetDb:ew6EOylqK6oAVm3o@cosmicforge1.ouy8f.mongodb.net/CosmicForgeDb?retryWrites=true&w=majority&appName=Cosmicforge1"
   
  const ts =  mongoose.connect(STAGING_URL)
/*
  const sd =   mongoose.createConnection(source)



  const patientVitalSignsSchema = new mongoose.Schema({
    
       bodyTemperature:{
          type:mongoose.SchemaTypes.String
       },
       bloodPressure:{
          type:mongoose.SchemaTypes.String
       },
       oxygenSaturation:{
          type:mongoose.SchemaTypes.String
       },
       weight:{
          type:mongoose.SchemaTypes.String
       },
       height:{
          type:mongoose.SchemaTypes.String
       },
       gender:{
          type:mongoose.SchemaTypes.String ,
          enum:['male','female']
      },
      dateOfBirth:{
          type:mongoose.SchemaTypes.String ,  
      },
  
  })
  
  
   const patientProfileSchema = new mongoose.Schema({
        userId:{
           type:mongoose.SchemaTypes.ObjectId,
           ref:'users'
       },
       profileType:{
          type:mongoose.SchemaTypes.String,
          enum:['personal','family']
   
       },
       mobileNo:{
           type:mongoose.SchemaTypes.String
       },
       homeAddress:{
           type:mongoose.SchemaTypes.String
       },
       workAddress:{
           type:mongoose.SchemaTypes.String
       },
       profilePicture:{
           type:mongoose.SchemaTypes.String 
       },
      vitalSigns:{
          type:patientVitalSignsSchema
      }
   
   
   
   })
   
   
   



  const tModel  =   ts.model('patientProfile',patientProfileSchema)


    const sModel  =  sd.model('patientProfile',patientProfileSchema)

 const doc = await  sModel.find().exec()

 await tModel.insertMany(doc)
*/
   return  ts
 } 
