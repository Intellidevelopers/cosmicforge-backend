
const { MongoClient, ServerApiVersion } = require('mongodb');

 let  LOCAL_DB_URL = "mongodb://localhost:27017/cosmicbacken"
 let  STAGING_URL = "mongodb+srv://CosmicForge:cosmicForgeDb@23@cluster0.amtdi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"


const uri = "mongodb+srv://CosmicForge:DevTeam1234@cluster0.amtdi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0";
// Create a MongoClient with a MongoClientOptions object to set the Stable API version
const client = new MongoClient(uri, {
  serverApi: {
    version: ServerApiVersion.v1,
    strict: true,
    deprecationErrors: true,
  }
});
 export  const connectDB = async () =>{
   return client.connect()
 } 
