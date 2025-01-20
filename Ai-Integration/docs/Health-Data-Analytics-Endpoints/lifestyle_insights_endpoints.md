Express.js Endpoint: 

POST /api/health-data-analytics/lifestyle-insights



React.js API call:

const getLifestyleInsights = async (patientData) => {
  const response = await axios.post('/api/health-data-analytics/lifestyle-insights', patientData);
  return response.data;
};