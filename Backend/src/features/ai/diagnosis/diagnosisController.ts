
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

export default  async () =>{
    try {

        const result = await requestDiagnosis("i have swollen legs")
           if(result.task_id){
            const diagnosis = await getDiagnosis(result.task_id)
            console.log(diagnosis)
           }else{
            console.log(result)
           }
        
    } catch (error) {
        console.log(error)
    }
}