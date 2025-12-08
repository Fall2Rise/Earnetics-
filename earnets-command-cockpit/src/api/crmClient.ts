import axios from "axios";
import { Contact, Deal, Task } from "../types/crm";

const api = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 8000,
});

export async function getContacts(): Promise<Contact[]> {
  const res = await api.get("/crm/contacts");
  return res.data || [];
}

export async function getDeals(): Promise<Deal[]> {
  const res = await api.get("/crm/deals");
  return res.data || [];
}

export async function getTasks(): Promise<Task[]> {
  const res = await api.get("/crm/tasks");
  return res.data || [];
}
