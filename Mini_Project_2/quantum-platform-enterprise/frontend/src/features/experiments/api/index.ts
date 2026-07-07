import apiClient from '@/services/api/client';

export const getExperiments = async () => {
  const response = await apiClient.get('/experiments');
  return response.data;
};
