import axios from "axios";
import { Stream } from "../types/streams";

const api = axios.create({
  baseURL: "http://localhost:8000/api/factory",
  timeout: 8000,
});

export async function getStreams(): Promise<Stream[]> {
  const res = await api.get("/streams");
  return res.data.streams || [];
}

export async function createStream(name: string, note = ""): Promise<Stream> {
  const res = await api.post("/streams", { name, note });
  return res.data.stream;
}

export async function advanceStream(id: number): Promise<Stream> {
  const res = await api.post(`/streams/${id}/advance`);
  return res.data.stream;
}
