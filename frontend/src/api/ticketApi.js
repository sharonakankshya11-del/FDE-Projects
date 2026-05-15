import axios from "axios";

const BASE = "http://localhost:8000";
const api  = axios.create({ baseURL: BASE, timeout: 8000 });

export const getAllTickets  = ()          => api.get("/tickets/");
export const getTicketById = (id)        => api.get(`/tickets/${id}`);
export const createTicket  = (data)      => api.post("/tickets/", data);
export const updateTicket  = (id, data)  => api.put(`/tickets/${id}`, data);
export const deleteTicket  = (id)        => api.delete(`/tickets/${id}`);
export const searchTickets = (params)    => api.get("/search", { params });
export const getStats      = ()          => api.get("/stats");
