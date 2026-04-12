import axios from 'axios';

const API_URL = "http://localhost:8000/api";

const client = axios.create({
  baseURL: API_URL,
});

export const getRestaurants = async (filters) => {
  const { data } = await client.get("/restaurants", { params: filters });
  return data;
};

export const chatWithBot = async (message, history) => {
  const { data } = await client.post("/chat", { message, history });
  return data;
};

export default client;
