
import mongoose from 'mongoose'
//mongodb+srv://CosmicForge:DevTeam1234@cluster0.amtdi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
 let  LOCAL_DB_URL = "mongodb://localhost:27017/cosmicbacken"
 let  STAGING_URL = "mongodb+srv://cosmicforgehealthnetDb:ew6EOylqK6oAVm3o@cosmicforge1.ouy8f.mongodb.net/CosmicForgeDb?retryWrites=true&w=majority&appName=Cosmicforge1";


// Create a MongoClient with a MongoClientOptions object to set the Stable API version

 export  const connectDB = async () =>{
 
  const source = "mongodb+srv://CosmicForge:DevTeam1234@cluster0.amtdi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
  //const target = "mongodb+srv://cosmicforgehealthnetDb:ew6EOylqK6oAVm3o@cosmicforge1.ouy8f.mongodb.net/CosmicForgeDb?retryWrites=true&w=majority&appName=Cosmicforge1"
   
  const ts =  mongoose.connect(STAGING_URL)

  const sd =   mongoose.createConnection(source)



  
   /*
   
   const DoctorSubscriptionDetailsSchema = new mongoose.Schema({
   
       name:{
           type:mongoose.SchemaTypes.String
       },
   
   
       message:{
           type:mongoose.SchemaTypes.String
       },
   
   
       currency:{
             type:mongoose.SchemaTypes.String,
             enum:['NGN','USD'],
             default:"NGN"
       },
       usdPrice:{
         type:mongoose.SchemaTypes.String,
         default:''
       },
       price:{
           type:mongoose.SchemaTypes.String
       },
       duration:{
           type:mongoose.SchemaTypes.String
       },
       commission:{
           type:mongoose.SchemaTypes.String
       },
       offers:[{
          type:mongoose.SchemaTypes.String
       }]
   
   })
   
   const PatientSubscriptionDetailsSchema = new mongoose.Schema({
   
       name:{
           type:mongoose.SchemaTypes.String
       },
   
   
       message:{
           type:mongoose.SchemaTypes.String
       },
   
   
       currency:{
             type:mongoose.SchemaTypes.String,
             enum:['NGN','USD'],
             default:"NGN"
       },
       usdPrice:{
         type:mongoose.SchemaTypes.String,
         default:''
       },
       price:{
           type:mongoose.SchemaTypes.String
       },
       duration:{
           type:mongoose.SchemaTypes.String
       },
       commission:{
           type:mongoose.SchemaTypes.String
       },
       offers:[{
          type:mongoose.SchemaTypes.String
       }]
   
   })
   
   
   const SubscriptionDtailsSchema = new mongoose.Schema({
   
       patient:{
           type:[PatientSubscriptionDetailsSchema]
       },
   
       doctor:{
           type:[DoctorSubscriptionDetailsSchema]
       }
   
   
       
   })
   



  const tModel  =   ts.model('subscriptionModelDetails',SubscriptionDtailsSchema)


    const sModel  =  sd.model('subscriptionModelDetails',SubscriptionDtailsSchema)

 const doc = await  sModel.find().exec()

 await tModel.insertMany(doc)

*/

   return  ts
 } 
