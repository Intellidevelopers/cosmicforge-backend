import dotenv from "dotenv"

dotenv.config()

import { initializeApp ,cert} from "firebase-admin/app";
 import {getStorage} from "firebase-admin/storage"
  const serviceJson = process?.env?.firebaseService

initializeApp({
credential:cert(JSON.parse(serviceJson!!)),
storageBucket:""
})


const storage = getStorage()


export default storage
