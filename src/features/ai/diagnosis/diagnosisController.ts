
const  requestDiagnosis = async (symptoms:string) =>{

  const response = await fetch(`${process.env.ai_diagnosis_api_base_url}/api/diagnose`,{
        method:"post",
        headers:{
            "Content-Type":"application/json",
            "access_token":process.env.ai_diagnosis_api_key!!
        },
        body:JSON.stringify({
            symptoms
        })

     })

console.log(response)
     return  response.json()
} 

const checkDiagnosisStatus = async (taskId:string) =>{
    return   fetch(`${process.env.ai_diagnosis_api_base_url}/api/diagnosis/status/${taskId}`,{
        method:"get",
        headers:{
            "Content-Type":"application/json",
            "access_token":process.env.ai_diagnosis_api_key!!
        },


     }).then(res=>{
        return res.json()
     })
}

const getDiagnosis = async (taskId:string) =>{
 const startTime = Date.now()
 while(Date.now()-startTime < 600000){
   const status = await checkDiagnosisStatus(taskId)

   if(status.status === "completed"){
    return status.result?.diagnosis
   }
   await new Promise(resolve=>setTimeout(resolve,5000))
 }
 return "time out"
}

export default  async (symptoms:string) =>{
    try {

        const result = await requestDiagnosis(symptoms)
           if(result.task_id){
            const diagnosis = await getDiagnosis(result.task_id)
           // console.log(diagnosis)
            return diagnosis
           }else{
            return ''
           // console.log(result)
           }
        
    } catch (error:any) {
        throw Error(error.message)
        console.log(error)
    }
}